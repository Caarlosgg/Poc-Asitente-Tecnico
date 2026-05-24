INSERT INTO diagnostic_trees (tree_id, model, symptom, version, tree_json, active) VALUES (
  'AK550_MOTOR_V1', 'AK550', 'Paradas de motor', 1,
  '{
    "start_node": "n1",
    "nodes": {
      "n1": {"type": "question", "text": "Cuando se para, ¿arranca sin quitar contacto?", "answers": {"si": "n2", "no": "n3"}},
      "n2": {"type": "diagnosis", "result": "Mal contacto en pipa de bujía"},
      "n3": {"type": "question", "text": "Quita contacto y vuelve a intentar. ¿Arranca?", "answers": {"si": "n4", "no": "n5"}},
      "n4": {"type": "diagnosis", "result": "Sensor de inclinación defectuoso"},
      "n5": {"type": "question", "text": "¿Se escucha la bomba de gasolina?", "answers": {"si": "n6", "no": "n7"}},
      "n7": {"type": "diagnosis", "result": "Bomba de gasolina defectuosa"},
      "n6": {"type": "question", "text": "¿Arranca después de enfriar?", "answers": {"si": "n8", "no": "n9"}},
      "n8": {"type": "diagnosis", "result": "Reglaje de válvulas pisado"},
      "n9": {"type": "diagnosis", "result": "Agua en el depósito"}
    }
  }'::jsonb, TRUE
) ON CONFLICT (tree_id) DO NOTHING;

INSERT INTO diagnostic_trees (tree_id, model, symptom, version, tree_json, active) VALUES (
  'AK550_CELP_V1', 'AK550', 'Testigo CELP encendido', 1,
  '{
    "start_node": "c1",
    "nodes": {
      "c1": {"type": "question", "text": "¿La moto arranca y funciona, aunque con el testigo CELP encendido?", "answers": {"si": "c2", "no": "c3"}},
      "c2": {"type": "diagnosis", "result": "Fallo electrónico no bloqueante; revisar sensor TPS, sensor de temperatura o lectura de códigos"},
      "c3": {"type": "question", "text": "¿Además del testigo CELP, hay dificultad de arranque o parada del motor?", "answers": {"si": "c4", "no": "c5"}},
      "c4": {"type": "diagnosis", "result": "Posible fallo de alimentación o gestión electrónica del combustible"},
      "c5": {"type": "diagnosis", "result": "Revisar lectura de códigos y comprobaciones eléctricas básicas"}
    }
  }'::jsonb, TRUE
) ON CONFLICT (tree_id) DO NOTHING;

INSERT INTO diagnostic_trees (tree_id, model, symptom, version, tree_json, active) VALUES (
  'AK550_ARRANQUE_V1', 'AK550', 'Problemas de arranque', 1,
  '{
    "start_node": "a1",
    "nodes": {
      "a1": {"type": "question", "text": "Al pulsar el botón de arranque, ¿gira el motor de arranque (se escucha intentar girar)?", "answers": {"si": "a3", "no": "a2"}},
      "a2": {"type": "question", "text": "¿Funcionan las luces del cuadro e instrumentación con el contacto puesto?", "answers": {"si": "a5", "no": "a4"}},
      "a4": {"type": "diagnosis", "result": "Batería descargada o fusible principal fundido — verificar tensión de batería y estado de fusibles"},
      "a5": {"type": "diagnosis", "result": "Relé de arranque defectuoso o botón de arranque averiado — probar con puente en relé"},
      "a3": {"type": "question", "text": "¿Se escucha el cebado de la bomba de combustible (zumbido 2-3 seg) al dar contacto?", "answers": {"si": "a6", "no": "a7"}},
      "a7": {"type": "diagnosis", "result": "Bomba de combustible defectuosa o fusible de bomba fundido — revisar circuito de alimentación de bomba"},
      "a6": {"type": "question", "text": "¿Ha probado en punto muerto (N) o con embrague pulsado a fondo?", "answers": {"si": "a8", "no": "a9"}},
      "a9": {"type": "diagnosis", "result": "Interruptor de seguridad de parada activo — verificar posición palanquilla, sensor embrague o switch de caballete"},
      "a8": {"type": "question", "text": "Al girar el motor de arranque, ¿se nota resistencia mecánica (no gira libre)?", "answers": {"si": "a10", "no": "a11"}},
      "a10": {"type": "diagnosis", "result": "Compresión insuficiente por desgaste de motor — medir compresión en bujía, revisar válvulas y junta de culata"},
      "a11": {"type": "question", "text": "¿La bujía tiene chispa visible al probarla fuera del motor?", "answers": {"si": "a12", "no": "a13"}},
      "a13": {"type": "diagnosis", "result": "Sin chispa: bobina de encendido defectuosa o CDI/ECU con fallo de encendido"},
      "a12": {"type": "diagnosis", "result": "Encendido correcto pero sin combustión: inyector obstruido, presión de combustible baja o sensor de posición de cigüeñal defectuoso"}
    }
  }'::jsonb, TRUE
) ON CONFLICT (tree_id) DO NOTHING;

INSERT INTO diagnostic_trees (tree_id, model, symptom, version, tree_json, active) VALUES (
  'XCITING_MOTOR_V1', 'Xciting S 400', 'Paradas de motor', 1,
  '{
    "start_node": "x1",
    "nodes": {
      "x1": {"type": "question", "text": "¿La moto se para de forma repentina (sin aviso) en lugar de con pérdida progresiva de potencia?", "answers": {"si": "x2", "no": "x5"}},
      "x2": {"type": "question", "text": "Tras la parada repentina, ¿arranca de nuevo después de unos minutos de reposo?", "answers": {"si": "x3", "no": "x4"}},
      "x3": {"type": "diagnosis", "result": "Probablemente sensor de temperatura o presión de combustible defectuoso — el motor corta por lectura incorrecta y se recupera al enfriarse"},
      "x4": {"type": "question", "text": "¿Se escucha la bomba de combustible al dar contacto?", "answers": {"si": "x8", "no": "x9"}},
      "x8": {"type": "diagnosis", "result": "Fallo de señal ECU o sensor de cigüeñal — conectar escáner diagnóstico para leer códigos DTC"},
      "x9": {"type": "diagnosis", "result": "Bomba de gasolina averiada — verificar fusible de bomba y relé antes de sustituir"},
      "x5": {"type": "question", "text": "¿Aparece el testigo de avería (CELP) antes o durante la pérdida de potencia?", "answers": {"si": "x6", "no": "x7"}},
      "x6": {"type": "diagnosis", "result": "Avería electrónica detectada por ECU — leer códigos DTC con escáner, probablemente sensor TPS, MAF o sonda lambda"},
      "x7": {"type": "question", "text": "¿El problema ocurre más en caliente que en frío?", "answers": {"si": "x10", "no": "x11"}},
      "x10": {"type": "diagnosis", "result": "Pérdida de compresión en caliente — revisar estado de válvulas, anillos y posible fuga en junta de culata"},
      "x11": {"type": "diagnosis", "result": "Obstrucción en filtro de combustible o inyector sucio — revisar sistema de alimentación y presión de combustible"}
    }
  }'::jsonb, TRUE
) ON CONFLICT (tree_id) DO NOTHING;
