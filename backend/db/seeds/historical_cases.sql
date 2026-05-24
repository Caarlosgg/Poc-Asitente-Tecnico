INSERT INTO historical_cases (case_id, model, symptom_category, case_text, final_diagnosis, base_confidence) VALUES
-- ── Paradas de motor ─────────────────────────────────────────────────────────
('CASE-001', 'AK550', 'Paradas de motor',
 'La moto se para en marcha al pasar por baches y vuelve a arrancar después de quitar y dar contacto.',
 'Sensor de inclinación defectuoso', 0.8500),

('CASE-002', 'AK550', 'Paradas de motor',
 'La moto se para y al volver a dar contacto no se escucha la bomba de gasolina.',
 'Bomba de gasolina defectuosa', 0.9000),

('CASE-003', 'AK550', 'Paradas de motor',
 'La moto se para en caliente y después de enfriar vuelve a arrancar con normalidad.',
 'Reglaje de válvulas pisado', 0.8800),

('CASE-004', 'AK550', 'Paradas de motor',
 'Tras repostar, la moto presenta paradas intermitentes y funcionamiento irregular.',
 'Agua en el depósito', 0.7500),

('CASE-005', 'AK550', 'Paradas de motor',
 'La moto se para de forma intermitente pero a veces rearranca sin necesidad de quitar contacto.',
 'Mal contacto en pipa de bujía', 0.7000),

('CASE-006', 'AK550', 'Paradas de motor',
 'La moto pierde fuerza progresivamente y finalmente se para. Al enfriar arranca bien durante unos minutos.',
 'Sensor de temperatura de motor (NTC) defectuoso — inyección en modo emergencia', 0.7800),

('CASE-007', 'AK550', 'Paradas de motor',
 'La moto se para en semáforo o a bajas revoluciones; en movimiento funciona bien.',
 'Regulador de ralentí (ISC) obstruido', 0.8200),

-- ── Testigo CELP encendido ───────────────────────────────────────────────────
('CASE-008', 'AK550', 'Testigo CELP encendido',
 'El testigo CELP se enciende de forma intermitente. El escáner muestra DTC P0136 (sonda lambda).',
 'Sonda lambda defectuosa o contaminada', 0.8200),

('CASE-009', 'AK550', 'Testigo CELP encendido',
 'El testigo CELP permanece encendido y la moto falla al acelerar. DTC P0351 en memoria.',
 'Bobina de encendido defectuosa', 0.7800),

('CASE-010', 'AK550', 'Testigo CELP encendido',
 'CELP encendido tras lluvia intensa. La ECU detecta fallo en sensor MAP. Se seca y desaparece.',
 'Conector del sensor MAP con humedad — corrosión en contactos', 0.7200),

('CASE-011', 'AK550', 'Testigo CELP encendido',
 'La moto consume más combustible y el CELP se enciende. DTC P0201 (inyector 1).',
 'Inyector obstruido o defectuoso', 0.8500),

-- ── Problemas de arranque ────────────────────────────────────────────────────
('CASE-012', 'AK550', 'Problemas de arranque',
 'La moto no arranca por las mañanas. El motor de arranque gira lento y el testigo de batería parpadea.',
 'Batería descargada o fin de vida útil', 0.9200),

('CASE-013', 'AK550', 'Problemas de arranque',
 'Al pulsar el botón de arranque no ocurre nada. Las luces funcionan correctamente.',
 'Relé de arranque defectuoso', 0.8000),

('CASE-014', 'AK550', 'Problemas de arranque',
 'La moto arranca en frío pero tarda varios intentos. El motor se cala al dar gas en los primeros minutos.',
 'Inyector parcialmente obstruido', 0.7500),

('CASE-015', 'AK550', 'Problemas de arranque',
 'El motor de arranque gira normalmente pero el motor no prende. Compresión correcta.',
 'Bujía en mal estado o con separación de electrodo incorrecta', 0.8600),

-- ── Consumo excesivo ─────────────────────────────────────────────────────────
('CASE-016', 'AK550', 'Consumo excesivo',
 'El consumo de combustible ha aumentado un 30% sin cambios en el uso. No hay pérdidas visibles.',
 'Filtro de aire obstruido — mezcla rica por restricción de aire', 0.7800),

('CASE-017', 'AK550', 'Consumo excesivo',
 'La moto consume mucho y huele a gasolina en el escape. Produce humo negro.',
 'Inyector con aguja atascada en posición abierta', 0.8500),

-- ── Xciting 400 ─────────────────────────────────────────────────────────────
('CASE-018', 'Xciting S 400', 'Paradas de motor',
 'La Xciting se para repentinamente en circulación sin previo aviso. Arranca de nuevo tras unos minutos.',
 'Sensor de presión de combustible defectuoso', 0.7300),

('CASE-019', 'Xciting S 400', 'Testigo CELP encendido',
 'El CELP se enciende en la Xciting 400 junto con pérdida de potencia en aceleración.',
 'Sensor de posición de mariposa (TPS) desajustado', 0.7900),

-- ── Ruidos y vibraciones ─────────────────────────────────────────────────────
('CASE-020', 'AK550', 'Ruidos',
 'Se escucha un traqueteo metálico al acelerar que desaparece en caliente.',
 'Cadena de distribución desgastada — tensor sin tensión suficiente', 0.7700)
ON CONFLICT (case_id) DO NOTHING;

INSERT INTO historical_cases (case_id, model, symptom_category, case_text, final_diagnosis, base_confidence) VALUES
-- ── AK550 Ruidos y vibraciones (cont.) ───────────────────────────────────────
('CASE-021', 'AK550', 'Ruidos',
 'Vibración intensa en el manillar a partir de 80 km/h que desaparece al reducir. Aumenta con la velocidad.',
 'Rueda delantera desequilibrada o rodamiento de dirección con desgaste', 0.7800),

('CASE-022', 'AK550', 'Ruidos',
 'Ruido metálico raspante al frenar con el freno trasero. No duele ni tira, pero el ruido es constante.',
 'Pastillas de freno trasero agotadas — cambio urgente, disco posiblemente rayado', 0.9200),

('CASE-023', 'AK550', 'Ruidos',
 'Traqueteo en la zona del motor al ralentí que desaparece completamente al acelerar un poco.',
 'Ajuste de válvulas necesario — holgura excesiva en válvulas de admisión o escape', 0.8300),

('CASE-024', 'AK550', 'Ruidos',
 'Ruido y vibración en la zona de transmisión al acelerar a fondo. La moto funciona pero la aceleración es irregular.',
 'Desgaste de rodillos del variador CVT — verificar también estado de correa', 0.7900),

('CASE-025', 'AK550', 'Ruidos',
 'Chirrido agudo al frenar con el freno delantero. Solo aparece con el freno delantero, no con el trasero.',
 'Disco de freno delantero rayado o pastillas vitrificadas por frenadas fuertes', 0.8500),

('CASE-026', 'AK550', 'Ruidos',
 'Golpeteo sordo al pasar por baches desde la zona trasera. La moto oscila más de lo normal.',
 'Amortiguador trasero en fin de vida útil o bieletas de suspensión desgastadas', 0.7400),

-- ── AK550 Transmisión y CVT ───────────────────────────────────────────────────
('CASE-027', 'AK550', 'Transmisión',
 'La moto acelera con retraso importante, como si tirara al principio y luego cogiera la potencia de golpe.',
 'Correa CVT desgastada o rodillos del variador aplastados — revisión completa de variador', 0.8600),

('CASE-028', 'AK550', 'Transmisión',
 'Al salir desde parado hay un tirón brusco. En velocidad constante no hay problema.',
 'Embrague centrífugo desgastado o resorte de embrague flojo — verificar estado de zapatas', 0.8100),

('CASE-029', 'AK550', 'Transmisión',
 'La moto no avanza bien a bajas velocidades, pierde fuerza y se arrastra. En velocidad alta parece ir bien.',
 'Correa de transmisión CVT partida o con grietas — sustitución inmediata', 0.9000),

('CASE-030', 'AK550', 'Transmisión',
 'Ruido de roce continuo en la zona del variador mientras está en marcha. Se nota más al arrancar.',
 'Poleas del variador con desgaste irregular o pista del rodamiento de polea sucia', 0.7700),

-- ── AK550 Consumo excesivo (adicionales) ─────────────────────────────────────
('CASE-031', 'AK550', 'Consumo excesivo',
 'La moto consume aceite sin pérdidas visibles externas. Sale humo azulado por el escape en frío.',
 'Desgaste de retenes de válvulas o segmentos del pistón — pérdida de aceite hacia la cámara', 0.8500),

('CASE-032', 'AK550', 'Consumo excesivo',
 'El depósito se vacía antes de lo habitual aunque el motor funciona bien y no hay manchas de gasolina.',
 'Fuga interna en el circuito de inyección o inyector que gotea en reposo', 0.7600),

('CASE-033', 'AK550', 'Consumo excesivo',
 'Consumo muy alto con ralentí inestable. Humo negro-gris por el escape en frío y en aceleración.',
 'Inyector atascado en posición abierta — mezcla excesivamente rica, sustitución necesaria', 0.8800),

-- ── AK550 Frenos ─────────────────────────────────────────────────────────────
('CASE-034', 'AK550', 'Frenos',
 'El freno delantero tiene mucho recorrido en la palanca antes de frenar. Hay que apretarla casi al puño.',
 'Pastillas de freno delantero muy desgastadas o nivel de líquido bajo — revisión urgente', 0.8300),

('CASE-035', 'AK550', 'Frenos',
 'El freno trasero se bloquea con facilidad en frenadas que antes eran normales. Hay manchas en la rueda.',
 'Pastillas traseras contaminadas con grasa por fuga del retén de eje trasero', 0.7800),

('CASE-036', 'AK550', 'Frenos',
 'Al frenar fuerte, la moto tira hacia el lado derecho. En frenadas suaves no se nota.',
 'Disco de freno deformado o pistón de pinza de freno atascado — verificar deformación del disco', 0.8000),

-- ── Xciting S 400 ────────────────────────────────────────────────────────────
('CASE-037', 'Xciting S 400', 'Paradas de motor',
 'La Xciting pierde potencia notable en aceleración fuerte desde bajo régimen. En aceleración suave funciona.',
 'Sensor MAF (medidor de caudal de aire) sucio o defectuoso — limpiar o sustituir', 0.7800),

('CASE-038', 'Xciting S 400', 'Paradas de motor',
 'Motor de la Xciting tiembla e irregularidades al ralentí. En movimiento va mejor pero el ralentí es inestable.',
 'Ralentí desajustado o bujía en mal estado — verificar también bobina de encendido', 0.8000),

('CASE-039', 'Xciting S 400', 'Problemas de arranque',
 'La Xciting S 400 no arranca, el motor de arranque gira fuerte pero el motor no prende nunca.',
 'Inyector sucio con obstrucción parcial o presión de combustible insuficiente — limpiar inyector', 0.8200),

('CASE-040', 'Xciting S 400', 'Testigo CELP encendido',
 'Testigo de avería intermitente en la Xciting. El funcionamiento es normal pero el testigo aparece y desaparece.',
 'Sensor de temperatura de motor con lectura errática — verificar conector y resistencia del sensor', 0.7400),

('CASE-041', 'Xciting S 400', 'Paradas de motor',
 'La Xciting S 400 se para a los pocos minutos de arrancar en caliente. En frío funciona perfectamente.',
 'Termostato de refrigeración defectuoso que provoca sobrecalentamiento — sustituir termostato', 0.8400),

('CASE-042', 'Xciting S 400', 'Ruidos',
 'Ruido de traqueteo en la Xciting al acelerar. El ruido viene claramente de la zona del motor.',
 'Desgaste de cadena de distribución o tensor de cadena flojo — revisión inmediata', 0.7700),

-- ── DT X360 ──────────────────────────────────────────────────────────────────
('CASE-043', 'DT X360', 'Problemas de arranque',
 'El DT X360 tiene dificultad de arranque en frío, necesita varios intentos y mucho tiempo de calentamiento.',
 'Sonda lambda en mal estado generando mezcla pobre en frío — verificar con escáner lambda', 0.7600),

('CASE-044', 'DT X360', 'Paradas de motor',
 'Pérdida de potencia notable en el DT X360 a alta velocidad en autopista. En ciudad va bien.',
 'Filtro de aire sucio o restricción en el sistema de admisión — inspección y cambio de filtro', 0.8000),

('CASE-045', 'DT X360', 'Testigo CELP encendido',
 'El testigo ABS se enciende en el DT X360 al iniciar la marcha. El freno funciona pero sin ABS.',
 'Sensor ABS con suciedad, daño en el anillo fónico o conector oxidado — revisar con escáner', 0.7900),

('CASE-046', 'DT X360', 'Ruidos',
 'Vibración en el manillar del DT X360 a velocidades superiores a 100 km/h. En ciudad no se nota.',
 'Desequilibrio en rueda delantera o rodamiento de dirección desgastado — equilibrar rueda', 0.8200),

-- ── CV5 ──────────────────────────────────────────────────────────────────────
('CASE-047', 'CV5', 'Problemas de arranque',
 'La CV5 no arranca bien en frío, hay que esperar 15-20 minutos antes de que prenda correctamente.',
 'Motor inundado por exceso de gasolina al arrancar — esperar con acelerador al fondo pulsado', 0.7700),

('CASE-048', 'CV5', 'Paradas de motor',
 'El motor de la CV5 se para al reducir a bajo régimen en ciudad, especialmente en semáforos.',
 'TPS (sensor de posición de mariposa) desajustado — ralentí incorrecto, recalibrar con escáner', 0.8500),

('CASE-049', 'CV5', 'Testigo CELP encendido',
 'Testigo de batería encendido en la CV5 mientras está en marcha. La batería arranca bien pero el testigo persiste.',
 'Alternador con rendimiento reducido o diodo del rectificador defectuoso — medir salida del alternador', 0.8300),

-- ── AK550 Arranque (adicionales) ─────────────────────────────────────────────
('CASE-050', 'AK550', 'Problemas de arranque',
 'La moto AK550 arranca pero se cala inmediatamente al quitar el choke o al mínimo de gasoline. En caliente funciona.',
 'Filtro de combustible parcialmente obstruido con presión insuficiente en frío — sustituir filtro', 0.7800),

('CASE-051', 'AK550', 'Problemas de arranque',
 'El motor de arranque da un solo clic o golpe y se detiene. No vuelve a girar hasta esperar.',
 'Batería con capacidad reducida que pierde tensión bajo la carga del motor de arranque — sustituir batería', 0.8700)
