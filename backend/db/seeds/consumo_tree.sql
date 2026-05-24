-- ────────────────────────────────────────────────────────────────────────────
-- AK550_CONSUMO_V1: Árbol de diagnóstico de consumo excesivo de combustible
-- Nodos prefijados con "q" para distinguirlos de otros árboles
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO diagnostic_trees (tree_id, model, symptom, version, tree_json, active)
VALUES (
  'AK550_CONSUMO_V1', 'AK550', 'Consumo excesivo', 1,
  '{
    "start_node": "q1",
    "nodes": {
      "q1": {
        "type": "question",
        "text": "¿El consumo aumentó de forma repentina tras realizar algún cambio o reparación?",
        "answers": {"si": "q2", "no": "q3"}
      },
      "q2": {
        "type": "question",
        "text": "¿Se realizó sustitución de filtro de aire o limpieza del cuerpo de mariposa recientemente?",
        "answers": {"si": "q10", "no": "q11"}
      },
      "q10": {
        "type": "diagnosis",
        "result": "Filtro de aire mal instalado o cuerpo de mariposa sucio — revisar montaje y limpiar"
      },
      "q11": {
        "type": "question",
        "text": "¿El testigo CELP está encendido o ha aparecido recientemente?",
        "answers": {"si": "q12", "no": "q13"}
      },
      "q12": {
        "type": "diagnosis",
        "result": "Mezcla rica por sensor lambda averiado — verificar sonda lambda y leer códigos"
      },
      "q13": {
        "type": "diagnosis",
        "result": "Consumo excesivo por ajuste de inyección post-mantenimiento — revisión de calibración"
      },
      "q3": {
        "type": "question",
        "text": "¿El consumo es elevado principalmente en ciudad, con muchos arranques y paradas?",
        "answers": {"si": "q4", "no": "q5"}
      },
      "q4": {
        "type": "question",
        "text": "¿El ralentí es estable o se nota inestable/alto en reposo?",
        "answers": {"si": "q9", "no": "q8"}
      },
      "q8": {
        "type": "diagnosis",
        "result": "Ralentí desajustado o depósito de carbono en mariposa — limpiar y calibrar ralentí"
      },
      "q9": {
        "type": "diagnosis",
        "result": "Consumo elevado por uso urbano intensivo — patrón normal; verificar presión de neumáticos y frenos"
      },
      "q5": {
        "type": "question",
        "text": "¿Se detecta olor a gasolina quemada o humo negro por el escape?",
        "answers": {"si": "q6", "no": "q7"}
      },
      "q6": {
        "type": "diagnosis",
        "result": "Mezcla rica por inyector con fuga interna o sensor de temperatura de motor averiado"
      },
      "q7": {
        "type": "question",
        "text": "¿La moto ha superado el intervalo de mantenimiento (aceite, filtros, bujías)?",
        "answers": {"si": "q14", "no": "q15"}
      },
      "q14": {
        "type": "diagnosis",
        "result": "Consumo elevado por motor deteriorado — realizar mantenimiento completo (aceite, filtros, bujías)"
      },
      "q15": {
        "type": "diagnosis",
        "result": "Consumo excesivo sin causa mecánica clara — medir consumo normalizado y consultar técnico"
      }
    }
  }'::jsonb,
  TRUE
)
ON CONFLICT (tree_id) DO NOTHING;
