"""Servicio: construye respuestas de diagnóstico con el contrato de salida estándar."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def build_diagnosis_response(
    primary: str,
    asked_questions: list[str],
    tree_nodes: dict[str, Any],
) -> dict[str, Any]:
    """
    Construye la respuesta estándar de diagnóstico desde el árbol.

    Contrato de salida:
    {
        "primary_hypothesis": str,
        "alternatives": list[str],
        "next_check": str,
        "short_explanation": str,
        "confidence": float
    }

    DESIGN DECISION: Para el árbol, la confianza es fija en 0.90 (resultado determinista).
    Las alternativas se derivan de los otros nodos de diagnóstico del árbol.
    """
    # Recopilar diagnósticos alternativos del árbol (excluyendo el principal)
    alternatives = [
        node["result"]
        for node_id, node in tree_nodes.items()
        if node.get("type") == "diagnosis" and node.get("result") != primary
    ][:2]  # Máximo 2 alternativas

    next_check = _infer_next_check(primary)
    explanation = _infer_explanation(primary)

    return {
        "primary_hypothesis": primary,
        "alternatives": alternatives,
        "next_check": next_check,
        "short_explanation": explanation,
        "confidence": 0.90,
        "source_type": "tree",
    }


def build_free_text_response(
    top_candidates: list[dict[str, Any]],
    user_query: str,
    tags_data: dict[str, Any],
) -> dict[str, Any]:
    """
    Construye la respuesta estándar de diagnóstico desde el ranking híbrido (Ruta C).

    Args:
        top_candidates: Lista de candidatos rankeados con scores.
        user_query: Consulta original del usuario.
        tags_data: Tags extraídos por el LLM.

    Returns:
        Dict con el contrato de salida estándar.
    """
    if not top_candidates:
        return {
            "primary_hypothesis": "No se encontró diagnóstico",
            "alternatives": [],
            "next_check": "Contactar con el servicio técnico oficial",
            "short_explanation": "No se encontraron casos similares en el historial.",
            "confidence": 0.0,
            "source_type": "historical",
        }

    primary = top_candidates[0]
    alternatives = [c["final_diagnosis"] for c in top_candidates[1:]]

    primary_diagnosis = primary["final_diagnosis"]
    confidence = round(float(primary.get("score", primary.get("base_confidence", 0.5))), 4)

    next_check = _infer_next_check(primary_diagnosis)
    explanation = _build_explanation_from_tags(primary_diagnosis, tags_data, user_query)

    return {
        "primary_hypothesis": primary_diagnosis,
        "alternatives": alternatives,
        "next_check": next_check,
        "short_explanation": explanation,
        "confidence": confidence,
        "source_type": "historical",
    }


def _infer_next_check(diagnosis: str) -> str:
    """Infiere la siguiente comprobación recomendada según el diagnóstico."""
    checks: dict[str, str] = {
        # Paradas de motor / Motor
        "Reglaje de válvulas pisado": "Verificar reglaje de válvulas y compresión en frío y en caliente",
        "Sensor de inclinación defectuoso": "Inspeccionar, limpiar y reponer el sensor de inclinación (lateral y vertical)",
        "Bomba de gasolina defectuosa": "Medir presión de combustible en rampa; verificar relé y fusible de bomba",
        "Agua en el depósito": "Drenar depósito completamente, sustituir filtro de combustible y purgar línea",
        "Mal contacto en pipa de bujía": "Revisar resistencia de la pipa, limpiar conector y verificar torque de bujía",
        "Fallo electrónico no bloqueante": "Conectar equipo de diagnóstico OBD y leer códigos de error activos",
        "Posible fallo de alimentación": "Verificar fusibles, relé de inyección y tensión en la ECU",
        # Arranque
        "Batería descargada": "Medir tensión en bornes con multímetro; cargar y repetir prueba de arranque",
        "Motor de arranque defectuoso": "Verificar tensión en borne positivo del motor de arranque al accionar",
        "Relé de arranque defectuoso": "Sustituir relé de arranque y verificar continuidad de circuito",
        "Bujía defectuosa o fouled": "Extraer bujías, inspeccionar electrodo y medir gap; sustituir si procede",
        "Sensor de punto muerto defectuoso": "Verificar señal del sensor con osciloscopio o multímetro en neutro",
        "Filtro de aire obstruido": "Inspeccionar y sustituir el filtro de aire; verificar cuerpo de mariposa",
        "Interruptor de parada de motor activo": "Verificar interruptor lateral y manetas de freno; limpiar contactos",
        "Fallo en sistema de encendido": "Verificar bobina de encendido, cables de alta tensión y sincronización",
        "Compresión insuficiente": "Medir compresión en cilindro; inspeccionar segmentos y guías de válvulas",
        # CELP / Electrónico
        "Código de avería transitorio": "Borrar código con equipo de diagnóstico y comprobar si reaparece",
        "Fallo en sensor de temperatura": "Medir resistencia del sensor NTC; comparar con tabla de valores del fabricante",
        "Fallo en sensor de oxígeno": "Inspeccionar sonda lambda; verificar tensión de señal con motor caliente",
        "Fallo en sensor de presión admisión": "Verificar conexión del MAP sensor y tubo de vacío de referencia",
        "Problema en circuito de inyectores": "Medir resistencia de inyectores (11-15 Ω) y señal de activación",
        "ECU requiere actualización o reseteo": "Realizar reset de ECU desconectando batería 10 min; actualizar firmware si disponible",
        # Xciting / Motor
        "Bobina de encendido defectuosa": "Medir resistencia primaria (0.5-1 Ω) y secundaria (8-15 kΩ) de la bobina",
        "Inyector obstruido": "Realizar limpieza ultrasónica de inyector; medir caudal y comparar especificación",
        "Válvula de mariposa sucia": "Limpiar cuerpo de mariposa con limpiador específico; verificar posición en reposo",
        # Consumo / Combustible
        "Consumo excesivo de combustible": "Medir consumo real en ciclo urbano normalizado y comparar con especificación",
        "Fuga de combustible interna": "Inspeccionar válvula de aguja del inyector; verificar retorno de combustible",
        "Mezcla rica por sensor lambda averiado": "Verificar tensión de la sonda lambda en ralentí (debería oscilar 0.1-0.9 V)",
        "Mezcla rica por filtro de aire obstruido": "Sustituir filtro de aire y limpiar cuerpo de mariposa; reevaluar mezcla",
        # Ruido / Vibración
        "Rodamiento de rueda defectuoso": "Elevar moto y girar rueda manualmente; buscar juego lateral o ruido metálico",
        "Cadena de distribución desgastada": "Inspeccionar tensión de cadena y desgaste de piñones; verificar ruido en frío",
        "Ruido en transmisión variador": "Revisar rodillos del variador, correa y campana de embrague; medir desgaste",
        "Vibración por desequilibrio de rueda": "Equilibrar rueda con máquina dinámica; inspeccionar neumático",
    }
    diag_lower = diagnosis.lower()
    for key, check in checks.items():
        if key.lower() in diag_lower:
            return check
    return "Realizar diagnóstico completo con equipo de diagnóstico especializado"


def _infer_explanation(diagnosis: str) -> str:
    """Genera una explicación corta y técnica para diagnósticos del árbol."""
    explanations: dict[str, str] = {
        "Reglaje de válvulas pisado": (
            "La moto falla en caliente y recupera al enfriar: patrón clásico de pérdida "
            "de compresión por válvulas con huelgo insuficiente que se dilatan en caliente."
        ),
        "Sensor de inclinación defectuoso": (
            "La moto se para al recibir golpes o impactos y arranca tras quitar y dar contacto: "
            "activación incorrecta del sensor de inclinación que corta el encendido falsamente."
        ),
        "Bomba de gasolina defectuosa": (
            "La ausencia de zumbido de la bomba al dar contacto indica fallo eléctrico o mecánico "
            "en el módulo de alimentación; sin presión de combustible la ECU no activa los inyectores."
        ),
        "Agua en el depósito": (
            "Las paradas intermitentes, especialmente tras repostar, son compatibles con "
            "contaminación por agua que provoca cortes de combustible al llegar a la bomba."
        ),
        "Mal contacto en pipa de bujía": (
            "La moto rearranca sin necesidad de quitar el contacto: fallo eléctrico intermitente "
            "en el circuito de encendido que se normaliza sólo al vibrar o cambiar temperatura."
        ),
        "Fallo electrónico no bloqueante": (
            "El testigo CELP indica un código de avería activo; el motor sigue funcionando pero "
            "puede estar en modo de emergencia con prestaciones reducidas."
        ),
        "Batería descargada": (
            "Tensión de batería inferior a 12 V en reposo o caída bajo carga al arrancar; "
            "el motor de arranque gira lento o no responde."
        ),
        "Motor de arranque defectuoso": (
            "La batería está en buen estado pero el motor de arranque no gira o gira con "
            "dificultad: desgaste de escobillas o avería del devanado del rotor."
        ),
        "Bujía defectuosa o fouled": (
            "Chispa débil o ausente en el cilindro; el motor puede girar pero no encender, "
            "o encender de forma irregular con pérdidas de potencia."
        ),
        "Código de avería transitorio": (
            "El testigo CELP se encendió puntualmente por una condición anómala que ya no persiste; "
            "borrar el código y monitorizar si reaparece en las próximas sesiones de conducción."
        ),
        "Consumo excesivo de combustible": (
            "Consumo significativamente por encima del valor de referencia del modelo; "
            "indica mezcla rica, pérdidas internas o uso inapropiado del vehículo."
        ),
        "Inyector obstruido": (
            "Patrón de pulverización deficiente o caudal reducido; provoca mezcla pobre "
            "con síntomas de tirones, pérdida de potencia y posible fallo de arranque en frío."
        ),
    }
    diag_lower = diagnosis.lower()
    for key, expl in explanations.items():
        if key.lower() in diag_lower:
            return expl
    return f"Diagnóstico determinado por árbol de decisión técnico: {diagnosis}."


def _build_explanation_from_tags(
    diagnosis: str,
    tags_data: dict[str, Any],
    query: str,
) -> str:
    """Construye explicación técnica para respuesta de historial de casos (Ruta C)."""
    category = tags_data.get("symptom_category", "")
    severity = tags_data.get("severity", "medium")
    tags: list[str] = tags_data.get("tags", [])

    severity_text = {"high": "alta — requiere atención inmediata", "medium": "media", "low": "baja"}.get(severity, "media")

    parts = [f"Diagnóstico más probable basado en casos históricos similares: **{diagnosis}**."]
    if category:
        parts.append(f"Categoría del síntoma identificada: {category}.")
    if tags:
        parts.append(f"Indicadores detectados: {', '.join(tags[:4])}.")
    parts.append(f"Severidad estimada: {severity_text}.")
    parts.append("Verifica los pasos indicados antes de realizar ningún desmontaje.")
    return " ".join(parts)
