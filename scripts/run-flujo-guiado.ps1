# Test guiado para la POC de asistente tecnico
# Ejecuta una secuencia completa: start -> VIN -> menu -> sintoma -> respuesta -> feedback -> metricas.
# Uso:
#   .\scripts\run-flujo-guiado.ps1
#   .\scripts\run-flujo-guiado.ps1 -Vin "AK550-POC-0001" -Symptom "Paradas de motor" -Answer "si"
#   .\scripts\run-flujo-guiado.ps1 -SkipFeedback
#   .\scripts\run-flujo-guiado.ps1 -CheckDbLogs

[CmdletBinding()]
param(
    [string]$ApiBaseUrl = "http://127.0.0.1:8000",
    [string]$Vin = "AK550-POC-0001",
    [ValidateSet("Paradas de motor", "Testigo CELP encendido")]
    [string]$Symptom = "Paradas de motor",
    [ValidateSet("si", "no")]
    [string]$Answer = "si",
    [switch]$SkipFeedback,
    [switch]$CheckDbLogs,
    [string]$DbContainer = "poc_asistente_postgres"
)

$ErrorActionPreference = "Stop"

function Get-ErrorBody {
    param(
        [object]$Response
    )

    if (-not $Response) {
        return $null
    }

    if ($Response -is [System.Net.Http.HttpResponseMessage]) {
        try {
            return $Response.Content.ReadAsStringAsync().Result
        } catch {
            return $null
        }
    }

    if ($Response -is [System.Net.WebResponse]) {
        try {
            $stream = $Response.GetResponseStream()
            if (-not $stream) {
                return $null
            }
            $reader = New-Object System.IO.StreamReader($stream)
            $body = $reader.ReadToEnd()
            $reader.Close()
            return $body
        } catch {
            return $null
        }
    }

    return $null
}

function Invoke-PostJson {
    param(
        [string]$Url,
        [hashtable]$Body
    )

    $json = $Body | ConvertTo-Json
    try {
        return Invoke-RestMethod -Method Post -Uri $Url -ContentType "application/json" -Body $json
    } catch {
        $response = $_.Exception.Response
        $statusCode = $null
        if ($response -and $response.StatusCode) {
            $statusCode = [int]$response.StatusCode
        }
        $body = Get-ErrorBody -Response $response
        if ($statusCode) {
            Write-Host "    Error HTTP $statusCode" -ForegroundColor Red
        } else {
            Write-Host "    Error HTTP (sin codigo)" -ForegroundColor Red
        }
        if ($body) {
            Write-Host "    Respuesta: $body" -ForegroundColor Red
        }
        throw
    }
}

function Assert-Stage {
    param(
        [object]$Response,
        [string]$ExpectedStage,
        [string]$StepName
    )

    $actual = $Response.state.stage
    if ($actual -ne $ExpectedStage) {
        throw "[$StepName] Stage esperado '$ExpectedStage', recibido '$actual'."
    }
}

Write-Host "[1/7] Crear sesion..." -ForegroundColor Cyan
$start = Invoke-RestMethod -Method Post -Uri "$ApiBaseUrl/session/start"
if (-not $start.session_id) {
    throw "No se recibio session_id en /session/start."
}
$sessionId = $start.session_id
Write-Host "    session_id = $sessionId"

Write-Host "[2/7] Enviar bastidor..." -ForegroundColor Cyan
$vinRes = Invoke-PostJson -Url "$ApiBaseUrl/session/message" -Body @{ session_id = $sessionId; message = $Vin }
Assert-Stage -Response $vinRes -ExpectedStage "menu" -StepName "VIN"
Write-Host "    OK -> stage: menu"

Write-Host "[3/7] Seleccionar menu (sintomas frecuentes)..." -ForegroundColor Cyan
$menuRes = Invoke-PostJson -Url "$ApiBaseUrl/session/message" -Body @{ session_id = $sessionId; message = "Sintomas frecuentes" }
Assert-Stage -Response $menuRes -ExpectedStage "awaiting_symptom" -StepName "Menu"
Write-Host "    OK -> stage: awaiting_symptom"

Write-Host "[4/7] Seleccionar sintoma..." -ForegroundColor Cyan
$symRes = Invoke-PostJson -Url "$ApiBaseUrl/session/message" -Body @{ session_id = $sessionId; message = $Symptom }
Assert-Stage -Response $symRes -ExpectedStage "tree" -StepName "Sintoma"
Write-Host "    OK -> stage: tree"

Write-Host "[5/7] Responder arbol (si/no)..." -ForegroundColor Cyan
$answerRes = Invoke-PostJson -Url "$ApiBaseUrl/session/message" -Body @{ session_id = $sessionId; message = $Answer }
if ($answerRes.message -like "*Diagnostico preliminar*") {
    Write-Host "    Diagnostico obtenido."
} else {
    Write-Host "    Flujo continuo. Respuesta: $($answerRes.message)"
}

if (-not $SkipFeedback) {
    Write-Host "[6/7] Enviar feedback final..." -ForegroundColor Cyan
    $feedbackRes = Invoke-PostJson -Url "$ApiBaseUrl/session/$sessionId/feedback" -Body @{ useful = $true; comment = "Flujo OK" }
    if (-not $feedbackRes.stored) {
        Write-Host "    Feedback no almacenado (posible duplicado)." -ForegroundColor Yellow
    } else {
        Write-Host "    Feedback almacenado."
    }
} else {
    Write-Host "[6/7] Feedback omitido por -SkipFeedback." -ForegroundColor Yellow
}

Write-Host "[7/7] Consultar metricas..." -ForegroundColor Cyan
$metrics = Invoke-RestMethod -Method Get -Uri "$ApiBaseUrl/metrics/summary"
Write-Host "    Sesiones totales: $($metrics.total_sessions)"
Write-Host "    Sesiones completas: $($metrics.completed_sessions)"
Write-Host "    Promedio pasos: $([math]::Round($metrics.average_steps_per_session, 2))"
Write-Host "    Feedback +: $($metrics.positive_feedback_count) / -: $($metrics.negative_feedback_count)"

if ($CheckDbLogs) {
    Write-Host "[Opcional] Verificando logs en BD..." -ForegroundColor Cyan
    try {
        docker exec -t $DbContainer psql -U asistente_user -d asistente_poc -c "SELECT session_id, role, content FROM messages ORDER BY created_at DESC LIMIT 5;"
        docker exec -t $DbContainer psql -U asistente_user -d asistente_poc -c "SELECT session_id, module_name, input_data, output_data FROM decision_logs ORDER BY created_at DESC LIMIT 5;"
    } catch {
        Write-Host "    No se pudo ejecutar docker/psql. Verifica contenedor y credenciales." -ForegroundColor Yellow
    }
}

Write-Host "Test completado. session_id = $sessionId" -ForegroundColor Green
