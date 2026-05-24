-- ────────────────────────────────────────────────────────────────────────────
-- Enriquecimiento de FAQs: 14 nuevas FAQs añadidas
-- Nuevas categorías: Consumo, Batería; y ampliación de Arranque, CELP, General
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO faqs (model, category, question, answer, usage_count, active) VALUES

-- ── Consumo ─────────────────────────────────────────────────────────────────
(
  'AK550', 'Consumo',
  '¿Cuál es el consumo normal del AK550 en ciudad y carretera?',
  'El consumo homologado del AK550 es de aproximadamente 4,2-4,8 L/100 km en ciclo mixto. En ciudad con mucho stop-and-go puede subir a 5,5-6 L/100 km, lo que es normal. Un consumo sistemáticamente superior a 7 L/100 km en todas las condiciones indica una anomalía mecánica o de ajuste.',
  0, TRUE
),
(
  'AK550', 'Consumo',
  '¿Por qué puede aumentar el consumo de combustible de forma repentina?',
  'Las causas más frecuentes de aumento repentino de consumo son: filtro de aire obstruido, inyector con fuga interna, sonda lambda averiada, sensor de temperatura de motor defectuoso, ralentí desajustado o reglaje de válvulas fuera de especificación. Si el testigo CELP está encendido, conectar el equipo de diagnóstico para leer los códigos de avería.',
  0, TRUE
),
(
  NULL, 'Consumo',
  '¿Afecta la presión de los neumáticos al consumo de combustible?',
  'Sí, de forma significativa. Un neumático inflado por debajo de la presión recomendada aumenta la resistencia a la rodadura y puede incrementar el consumo entre un 5% y un 10%. Revisar y ajustar la presión en frío según las especificaciones del fabricante (generalmente 2,0-2,5 bar delante y 2,5-2,9 bar detrás en el AK550).',
  0, TRUE
),

-- ── Batería ──────────────────────────────────────────────────────────────────
(
  NULL, 'Batería',
  '¿Cada cuánto tiempo hay que cambiar la batería de una moto?',
  'La vida útil de una batería de plomo-ácido en moto es de 3 a 5 años en condiciones normales. Las baterías de gel o AGM pueden durar algo más. Si la tensión en reposo es inferior a 12,4 V o cae por debajo de 9,6 V durante el arranque, la batería debe sustituirse.',
  0, TRUE
),
(
  'AK550', 'Batería',
  '¿Qué batería lleva el AK550 de fábrica?',
  'El AK550 monta una batería de 12 V / 10 Ah tipo YTX12-BS (o equivalente AGM del mismo tamaño). Al sustituirla, usar siempre una batería de las mismas especificaciones. Tras la sustitución, verificar la tensión en ralentí (14-15 V indica carga correcta del alternador).',
  0, TRUE
),
(
  NULL, 'Batería',
  '¿Cómo se carga correctamente la batería de una moto sin dañarla?',
  'Usar un cargador inteligente (CTEK, Optimate, etc.) compatible con baterías de plomo-ácido o AGM. Conectar en polaridad correcta (rojo al positivo, negro al negativo). La carga lenta (0,5-1 A) durante 8-12 horas es preferible a la carga rápida. Nunca cargar con la batería montada en la moto si el cargador no es de mantenimiento.',
  0, TRUE
),

-- ── Arranque (adicionales) ───────────────────────────────────────────────────
(
  'AK550', 'Arranque',
  '¿Por qué el AK550 cuesta arrancar en frío pero en caliente va bien?',
  'La principal causa es una bujía desgastada o con gap fuera de especificación, que no genera chispa suficiente en frío. También puede ser el sensor de temperatura de motor averiado (la ECU no aplica mezcla de arranque en frío correctamente) o una batería debilitada que no aporta suficiente corriente en bajas temperaturas.',
  0, TRUE
),
(
  NULL, 'Arranque',
  '¿Qué hacer si el motor de arranque gira pero el motor no enciende?',
  'Verificar en este orden: (1) Nivel de combustible; (2) Posición del interruptor de parada y maneta lateral; (3) Chispa en la bujía (extraer y verificar); (4) Presión de combustible (zumbido de bomba al dar contacto); (5) Compresión en cilindro. Si todo lo anterior es correcto, conectar equipo de diagnóstico para revisar señales del sensor CKP y los inyectores.',
  0, TRUE
),

-- ── Testigo CELP (adicionales) ───────────────────────────────────────────────
(
  'AK550', 'Testigo CELP',
  '¿Cómo se leen los códigos de error del AK550 sin equipo de diagnóstico?',
  'El AK550 no dispone de lectura de códigos por parpadeos del testigo. Es necesario un escáner OBD compatible con el protocolo Kymco (ISO 14230-4 KWP o ISO 15765-4 CAN según versión). Los equipos compatibles más usados en talleres son Kymco Dealer System, HELLA Gutmann, Launch X431 y OBD11. No intentar borrar códigos sin identificar antes la causa raíz.',
  0, TRUE
),
(
  NULL, 'Testigo CELP',
  '¿Es peligroso continuar circulando con el testigo CELP encendido?',
  'Depende del tipo de código. Un código no bloqueante (moto funciona con normalidad) permite llegar al taller con precaución. Un código bloqueante (moto en modo de emergencia con potencia limitada o parada) requiere asistencia inmediata. Nunca ignorar un testigo CELP parpadeante, que generalmente indica un fallo activo y crítico.',
  0, TRUE
),

-- ── General (adicionales) ────────────────────────────────────────────────────
(
  NULL, 'General',
  '¿Cuál es el intervalo de mantenimiento recomendado para el AK550?',
  'El intervalo estándar del AK550 es cada 5.000 km o 6 meses (lo que ocurra primero) para cambio de aceite y revisión básica. Cada 10.000 km: filtro de aceite, filtro de aire, bujías, ajuste de válvulas. Cada 20.000 km: correa de transmisión (según desgaste), líquido de frenos y refrigerante. Consultar siempre el manual del propietario para el modelo y año exacto.',
  0, TRUE
),
(
  NULL, 'General',
  '¿Qué aceite motor usa el AK550?',
  'El AK550 requiere aceite de motor 4 tiempos API SJ o superior, SAE 10W-40. La capacidad del cárter es de 1,2 litros con cambio de filtro y 1,0 litros sin cambio de filtro. Usar aceite de calidad (Kymco original, Motul, Castrol, Shell) y respetar el intervalo de cambio para no comprometer la vida del motor.',
  0, TRUE
),
(
  'Xciting S 400', 'Mantenimiento',
  '¿Cada cuánto km hay que revisar el reglaje de válvulas de la Xciting S 400?',
  'Kymco recomienda revisar el reglaje de válvulas de la Xciting S 400 cada 12.000 km. El huelgo correcto es de 0,10-0,15 mm en admisión y 0,15-0,20 mm en escape, medido con la temperatura de motor a 20 °C (motor frío). Un reglaje fuera de especificación provoca ruido de válvulas, pérdida de compresión y mayor consumo.',
  0, TRUE
),
(
  NULL, 'Frenos',
  '¿Cómo saber si las pastillas de freno necesitan sustitución?',
  'Las pastillas de freno deben sustituirse cuando el grosor del material de fricción es inferior a 2 mm (hay una ranura de desgaste visible en la mayoría de modelos). También si se observa desgaste irregular, cristalización del material o ruido de chirriado constante. En el AK550, el sistema de frenos ABS requiere un reajuste del sensor de velocidad de rueda después de cualquier sustitución de disco.',
  0, TRUE
)

ON CONFLICT DO NOTHING;
