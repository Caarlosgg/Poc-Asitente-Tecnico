INSERT INTO faqs (model, category, question, answer) VALUES
-- ── Paradas de motor ─────────────────────────────────────────────────────────
('AK550', 'Paradas de motor',
 '¿Por qué puede pararse la moto en marcha de forma intermitente?',
 'Las causas más probables son: sensor de inclinación defectuoso, bomba de gasolina defectuosa, reglaje de válvulas pisado, agua en el depósito o mal contacto en pipa de bujía.'),

('AK550', 'Paradas de motor',
 '¿La moto se para al pasar baches y vuelve a arrancar sola?',
 'Ese comportamiento es muy característico del sensor de inclinación (TPS lateral). Al detectar una inclinación brusca corta el encendido como medida de seguridad. El sensor puede estar descalibrado o averiado.'),

-- ── Combustible ──────────────────────────────────────────────────────────────
('AK550', 'Combustible',
 '¿Qué significa que no se escuche la bomba de gasolina al dar contacto?',
 'Es una señal compatible con fallo de bomba de gasolina o falta de alimentación eléctrica al sistema de combustible.'),

('AK550', 'Combustible',
 '¿Por qué la moto presenta consumo de combustible más elevado de lo normal?',
 'Un consumo excesivo puede deberse a: inyector sucio o defectuoso, filtro de aire obstruido, presión de combustible incorrecta, sonda lambda con lecturas erróneas o reglaje de válvulas incorrecto.'),

-- ── Testigo CELP ─────────────────────────────────────────────────────────────
(NULL, 'General',
 '¿Qué significa el testigo CELP encendido?',
 'El testigo CELP indica una avería relacionada con la gestión electrónica del motor o el sistema de inyección. Puede deberse a fallos en la sonda lambda, sensor de temperatura de motor, bobina de encendido, o inyectores.'),

('AK550', 'Electrónica',
 '¿El testigo CELP se apaga solo al reiniciar la moto?',
 'Si el testigo desaparece tras varias reinicios sin síntomas claros puede tratarse de un error intermitente. Es conveniente leer la memoria de fallos con un escáner diagnóstico para identificar el código DTC exacto.'),

-- ── Mantenimiento ────────────────────────────────────────────────────────────
('AK550', 'Mantenimiento',
 '¿Qué puede indicar que falle en caliente y vuelva a arrancar en frío?',
 'Ese patrón es compatible con reglaje de válvulas pisado y pérdida de compresión en caliente.'),

('AK550', 'Mantenimiento',
 '¿Cuándo hay que cambiar el aceite en la AK550?',
 'El aceite de motor debe cambiarse cada 5000 km o anualmente, lo que ocurra primero. Se recomienda aceite sintético 10W-40 MA2 para motocicletas.'),

('AK550', 'Mantenimiento',
 '¿Cómo se revisan las válvulas en la AK550?',
 'El reglaje de válvulas debe revisarse cada 12000 km. Se accede al motor por la parte superior, con la moto fría. La holgura de admisión es 0,10-0,15 mm y la de escape 0,15-0,20 mm.'),

-- ── Arranque ─────────────────────────────────────────────────────────────────
('AK550', 'Arranque',
 '¿Por qué la moto no arranca en frío aunque el motor de arranque gira?',
 'Si el motor de arranque gira pero el motor no arranca en frío puede ser por: bujía en mal estado, presión de compresión baja, bomba de gasolina que no alcanza presión, o inyector obstruido.'),

('AK550', 'Arranque',
 '¿Qué causa que el motor de arranque no gire al pulsar el botón de arranque?',
 'Las causas más frecuentes son: batería descargada o defectuosa, relé de arranque averiado, fusible de arranque fundido, pletina de masa deteriorada, o interruptor de arranque dañado.'),

-- ── Frenos ───────────────────────────────────────────────────────────────────
('AK550', 'Frenos',
 '¿Por qué la moto vibra o tiembla al frenar?',
 'La vibración al frenar suele deberse a: disco de freno alabeado, pastillas de freno desgastadas de forma irregular, o pinza de freno con pistón bloqueado parcialmente.'),

(NULL, 'General',
 '¿Cómo se sangra el sistema de frenos en una moto con ABS?',
 'Para sangrar frenos con ABS es necesario un escáner que active el ciclo ABS durante el sangrado. Sin ese ciclo, puede quedar aire en el módulo ABS. Se recomienda hacerlo en servicio oficial.')
ON CONFLICT DO NOTHING;

INSERT INTO faqs (model, category, question, answer) VALUES
-- ── Variador / CVT ───────────────────────────────────────────────────────────
('AK550', 'Transmisión',
 '¿Cuándo se debe revisar el variador CVT de la AK550?',
 'El variador CVT de la AK550 debe revisarse cada 20.000 km o cuando se detecten síntomas como aceleración irregular, tirones al salir desde parado o ruidos en la zona de transmisión. Los rodillos, la correa y las zapatas de embrague son los elementos con mayor desgaste.'),

('AK550', 'Transmisión',
 '¿Cuáles son los síntomas de una correa CVT desgastada?',
 'Una correa CVT en mal estado produce: aceleración lenta o con tirones, ruido de roce o chirrido en la transmisión, pérdida de potencia progresiva y, en casos extremos, la correa puede partirse dejando la moto sin tracción. Se recomienda inspección visual cada 10.000 km.'),

-- ── Xciting S 400 específico ─────────────────────────────────────────────────
('Xciting S 400', 'Mantenimiento',
 '¿Qué tipo de aceite utiliza el motor de la Xciting S 400?',
 'La Xciting S 400 utiliza aceite sintético 10W-40 para motores de cuatro tiempos, especificación MA2. El intervalo de cambio es de 4.000 km en uso normal. Consultar el manual para condiciones de uso extremo (temperatura, carga, carretera de montaña).'),

('Xciting S 400', 'Paradas de motor',
 '¿Por qué la Xciting S 400 se para a los pocos minutos de arrancar en caliente?',
 'Las causas más probables son termostato defectuoso que genera sobrecalentamiento, sensor de temperatura con lectura errónea que corta el suministro de combustible, o fallo intermitente del sensor de presión de combustible. Se recomienda conectar escáner y leer códigos DTC.'),

-- ── Mantenimiento general ─────────────────────────────────────────────────────
('AK550', 'Mantenimiento',
 '¿Cada cuánto hay que ajustar las válvulas en la AK550?',
 'El ajuste de válvulas de la AK550 debe realizarse cada 12.000 km o cada 2 años (lo que ocurra antes). Una holgura excesiva provoca traqueteo al ralentí y pérdida de compresión. La holgura correcta es: admisión 0,10-0,15 mm, escape 0,17-0,22 mm en frío.'),

('AK550', 'Mantenimiento',
 '¿Cuándo hay que cambiar la bujía en la AK550?',
 'La bujía de la AK550 debe cambiarse cada 8.000 km en uso normal. Se recomienda inspeccionarla cada 4.000 km: un electrodo erosionado, aislante agrietado o depósitos excesivos indican necesidad de cambio inmediato. El tipo de bujía recomendado es NGK CR8EH-9 o equivalente Denso.'),

-- ── Neumáticos y presión ─────────────────────────────────────────────────────
('AK550', 'Neumáticos',
 '¿Cuál es la presión correcta de los neumáticos de la AK550?',
 'La presión recomendada para la AK550 es: delantera 2,2 bar (32 PSI) y trasera 2,5 bar (36 PSI) en frío, con un ocupante. Con pasajero y equipaje, aumentar la trasera a 2,8 bar. Verificar siempre con el neumático frío y ajustar cada 2 semanas.'),

('AK550', 'Neumáticos',
 '¿Cuáles son los neumáticos recomendados para la AK550?',
 'La AK550 equipa de fábrica neumáticos Michelin Pilot Street 2 (120/70-14 delantero, 160/60-14 trasero) o equivalentes Pirelli Angel City. Se recomienda mantener la especificación de tamaño original para no alterar el comportamiento dinámico y la precisión del ABS.'),

-- ── Líquidos y fluidos ────────────────────────────────────────────────────────
(NULL, 'Mantenimiento',
 '¿Con qué frecuencia se cambia el líquido de frenos en una moto Kymco?',
 'El líquido de frenos debe cambiarse cada 2 años independientemente del kilometraje, ya que es higroscópico (absorbe humedad) y pierde efectividad. Se utiliza líquido DOT 4 en todos los modelos Kymco con frenos de disco. Verificar el nivel visualmente cada 5.000 km.'),

-- ── Electrónica y CELP ───────────────────────────────────────────────────────
('AK550', 'Testigo CELP',
 '¿Cuál es la diferencia entre un fallo CELP leve y uno crítico?',
 'Un fallo CELP leve (parpadeo o intermitente) indica un problema detectado pero no bloqueante: la moto puede funcionar en modo degradado. Un fallo crítico (CELP fijo con pérdida de potencia o parada) indica que la ECU ha cortado funciones por seguridad. Siempre leer los códigos DTC con escáner antes de intervenir.'),

(NULL, 'Electrónica',
 '¿Qué es el sensor IACV y cuándo puede fallar?',
 'El IACV (Idle Air Control Valve) o válvula de control de ralentí regula el flujo de aire en ralentí. Cuando falla, los síntomas son: ralentí inestable, motor que se cala al mínimo, arranque dificultoso en frío o ralentí excesivamente alto. Se diagnostica con escáner midiendo el ciclo de trabajo de la válvula.'),

-- ── DT X360 específico ───────────────────────────────────────────────────────
('DT X360', 'Frenos',
 '¿Cómo funciona el sistema ABS del DT X360 y cuándo requiere mantenimiento?',
 'El ABS del DT X360 es de canal doble con sensores en ambas ruedas. El módulo ABS interviene si detecta bloqueo de rueda. El mantenimiento consiste en: inspeccionar los sensores ABS y anillos fónicos cada 10.000 km, verificar que no haya suciedad o daño en los cables, y realizar el sangrado del sistema con escáner diagnóstico.'),

-- ── Revisiones periódicas ─────────────────────────────────────────────────────
(NULL, 'Mantenimiento',
 '¿Qué incluye la revisión de los 10.000 km en modelos Kymco?',
 'La revisión de 10.000 km incluye: cambio de aceite y filtro, inspección de frenos (pastillas, discos y líquido), comprobación de cadena de distribución o variador CVT, ajuste de válvulas si procede, revisión de neumáticos e iluminación, lectura de códigos DTC con escáner, y verificación del sistema de refrigeración en modelos con refrigeración líquida.')
ON CONFLICT DO NOTHING;
