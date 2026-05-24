"""Cliente Groq API — wrapper para LLM y generación de embeddings."""

import json
import logging
from typing import Any

from groq import AsyncGroq

from core.config import settings
from core.exceptions import GroqAPIError

logger = logging.getLogger(__name__)

# Cliente global reutilizable (una instancia por proceso)
_client: AsyncGroq | None = None


def _get_client() -> AsyncGroq:
    """Devuelve el cliente Groq inicializado (lazy singleton)."""
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise GroqAPIError("GROQ_API_KEY no configurada")
        _client = AsyncGroq(api_key=settings.groq_api_key)
    return _client


async def generate_response(prompt: str, system_prompt: str = "") -> str:
    """
    Llama al LLM de Groq con un prompt y devuelve el texto de respuesta.

    Args:
        prompt: El mensaje del usuario / instrucción principal.
        system_prompt: Instrucción de sistema opcional.

    Returns:
        Texto generado por el LLM.
    """
    client = _get_client()
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    try:
        response = await client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=0.3,
            max_tokens=512,
        )
        text = response.choices[0].message.content or ""
        logger.debug("Groq LLM response: %d chars", len(text))
        return text.strip()
    except Exception as exc:
        logger.error("Error Groq LLM: %s", exc)
        raise GroqAPIError(str(exc)) from exc


async def get_embedding(text: str) -> list[float]:
    """
    Genera un embedding vectorial para el texto dado usando Groq.

    DESIGN DECISION: Groq usa el modelo nomic-embed-text-v1_5 (dim=768).
    Si la API de embeddings de Groq no está disponible, lanza GroqAPIError.

    Args:
        text: Texto a embeber.

    Returns:
        Lista de floats representando el embedding.
    """
    client = _get_client()

    try:
        response = await client.embeddings.create(
            model=settings.groq_embedding_model,
            input=text,
        )
        embedding = response.data[0].embedding
        logger.debug("Embedding generado: dim=%d", len(embedding))
        return embedding
    except Exception as exc:
        logger.warning("Groq embeddings no disponibles (modelo retirado): %s — usando fallback léxico", exc)
        raise GroqAPIError(f"Error generando embedding: {exc}") from exc


async def extract_tags(text: str, vehicle_model: str) -> dict[str, Any]:
    """
    Usa el LLM para extraer tags técnicos del texto de diagnóstico.

    Devuelve un dict con: symptom_category, tags (list), severity.

    Args:
        text: Texto libre del usuario.
        vehicle_model: Modelo del vehículo identificado.

    Returns:
        Dict con tags extraídos o dict vacío si falla.
    """
    system = (
        "Eres un asistente técnico de motocicletas. "
        "Extrae tags técnicos del texto. "
        "Devuelve SOLO un JSON válido con: "
        '{"symptom_category": "...", "tags": [...], "severity": "high|medium|low"}. '
        "No añadas texto fuera del JSON."
    )
    prompt = f"Texto: {text}\nModelo: {vehicle_model}"

    try:
        raw = await generate_response(prompt, system_prompt=system)
        # Limpiar posible markdown ```json ... ```
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        parsed = json.loads(raw)
        return parsed
    except Exception as exc:
        logger.warning("Error extrayendo tags con LLM: %s. Devolviendo vacío.", exc)
        return {"symptom_category": "", "tags": [], "severity": "medium"}


async def classify_user_intent(text: str, vehicle_model: str) -> dict[str, Any]:
    """
    Clasifica texto libre del técnico en una ruta de diagnóstico.

    Returns:
        Dict con claves: route ('tree'|'faq'|'other'), symptom_key (str|None), confidence (float)

    symptom_key values: 'motor_para' | 'arranque' | 'celp' | 'consumo' | 'frenos' | 'ruido' | 'otro'
    """
    system = (
        "Eres un clasificador de consultas técnicas de motocicletas Kymco. "
        "Clasifica el texto del técnico en UNA de estas rutas:\n"
        "- 'tree': el técnico describe un síntoma mecánico concreto "
        "(motor se apaga/para, dificultad de arranque, testigo encendido, consumo anómalo, "
        "ruido o vibración extraña, problema de frenos)\n"
        "- 'faq': pregunta técnica sobre procedimiento, mantenimiento, especificaciones, "
        "intervalos de revisión, cómo hacer algo\n"
        "- 'other': descripción vaga, mixta, saludo o no relacionado\n\n"
        "Si la ruta es 'tree', elige el symptom_key más apropiado:\n"
        "  'motor_para' → motor se apaga, para o pierde potencia en marcha\n"
        "  'arranque' → no arranca, dificultad de arranque, motor no prende\n"
        "  'celp' → testigo CELP, luz de avería, código de error electrónico\n"
        "  'consumo' → consumo excesivo de gasolina u aceite\n"
        "  'frenos' → problemas de frenada, ruido en frenos, freno bloquea\n"
        "  'ruido' → ruido o vibración anómala sin síntoma de paro\n"
        "  'otro' → síntoma mecánico que no encaja en las categorías anteriores\n\n"
        "Devuelve SOLO JSON válido (sin texto adicional):\n"
        "{\"route\": \"tree\", \"symptom_key\": \"motor_para\", \"confidence\": 0.87}"
    )
    prompt = f"Texto del técnico: \"{text}\"\nModelo del vehículo: {vehicle_model or 'desconocido'}"

    try:
        raw = await generate_response(prompt, system_prompt=system)
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        parsed = json.loads(raw)
        logger.debug("Clasificación LLM: route=%s symptom=%s conf=%.2f",
                     parsed.get("route"), parsed.get("symptom_key"), parsed.get("confidence", 0))
        return parsed
    except Exception as exc:
        logger.warning("Error clasificando intención con LLM: %s → fallback: other", exc)
        return {"route": "other", "symptom_key": None, "confidence": 0.3}


async def generate_free_text_diagnosis(
    user_message: str,
    model: str,
    top_candidates: list[dict[str, Any]],
    tags_data: dict[str, Any],
) -> str:
    """
    Genera una respuesta diagnóstica conversacional y personalizada con LLM.
    Toma la descripción del técnico y los candidatos rankeados del historial.

    Returns:
        Texto en español, 4-6 frases, sin listas, para mostrar directamente al técnico.
    """
    if not top_candidates:
        return (
            f"No encontré casos históricos similares para el {model}. "
            "Te recomiendo conectar el escáner de diagnóstico para leer los códigos DTC "
            "y realizar una revisión completa del sistema de inyección y electrónica."
        )

    candidates_ctx = ""
    for i, c in enumerate(top_candidates[:3], 1):
        score_pct = round(float(c.get("score", c.get("base_confidence", 0.5))) * 100)
        candidates_ctx += (
            f"{i}. {c['final_diagnosis']} (afinidad {score_pct}%)\n"
            f"   Caso registrado: {c.get('case_text', '')[:150]}\n\n"
        )

    symptom_cat = tags_data.get("symptom_category", "síntoma no clasificado")
    severity = tags_data.get("severity", "medium")
    tags = tags_data.get("tags", [])
    severity_label = {"high": "alta — requiere atención inmediata",
                      "medium": "media", "low": "baja"}.get(severity, "media")

    system = (
        "Eres un asistente técnico experto en motocicletas Kymco con 15 años de experiencia. "
        "Genera una respuesta diagnóstica conversacional, útil y personalizada para el técnico. "
        "FORMATO: 4-6 oraciones en texto fluido, sin listas ni viñetas, sin encabezados. "
        "CONTENIDO obligatorio:\n"
        "  1. Reconoce brevemente lo que describe el técnico\n"
        "  2. Indica la hipótesis principal y por qué concuerda con la descripción\n"
        "  3. Si hay hipótesis alternativa relevante, menciónala en una frase\n"
        "  4. Indica UNA comprobación concreta y específica a realizar primero\n"
        "Usa terminología técnica correcta. No inventes datos. "
        "Trata al técnico de 'tú'. Responde en español."
    )

    prompt = (
        f"Vehículo: {model}\n"
        f"El técnico describe: '{user_message}'\n"
        f"Categoría del síntoma: {symptom_cat}\n"
        f"Severidad estimada: {severity_label}\n"
        f"Tags técnicos identificados: {', '.join(tags) if tags else 'ninguno extraído'}\n\n"
        f"Hipótesis del sistema (basadas en casos históricos similares):\n{candidates_ctx}"
        f"Genera la respuesta diagnóstica personalizada para el técnico."
    )

    try:
        response = await generate_response(prompt, system_prompt=system)
        return response.strip()
    except Exception as exc:
        logger.warning("Error generando narrativa de diagnóstico LLM: %s", exc)
        primary = top_candidates[0]["final_diagnosis"]
        return (
            f"Basándome en el análisis del historial de casos para el {model}, "
            f"la causa más probable es: {primary}. "
            f"Te recomiendo realizar una inspección detallada del sistema para confirmar este diagnóstico."
        )

