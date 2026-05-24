-- ────────────────────────────────────────────────────────────────────────────
-- Enriquecimiento de historical_cases: CASE-052 a CASE-076
-- Cubre: AK550 Consumo, Vibración/Ruido, Eléctrico; Xciting S 400 CELP/Motor;
--        AK550 CELP adicionales; DT X360 arranque; general
-- ────────────────────────────────────────────────────────────────────────────

INSERT INTO historical_cases (case_id, model, symptom_category, case_text, final_diagnosis, base_confidence) VALUES

-- ── AK550: Consumo excesivo ──────────────────────────────────────────────────
('CASE-052', 'AK550', 'Consumo excesivo',
 'El AK550 consume casi 6 litros cada 100 km en ciudad cuando la especificación es 4,5 L/100 km. No hay avería visible ni testigo encendido.',
 'Mezcla rica por ralentí desajustado o filtro de aire parcialmente obstruido', 0.8200),

('CASE-053', 'AK550', 'Consumo excesivo',
 'Tras cambiar el aceite y el filtro de aire, el consumo aumentó notablemente. Humo negro intermitente por el escape.',
 'Filtro de aire mal instalado o tipo incorrecto — mezcla rica por exceso de restricción', 0.8500),

('CASE-054', 'AK550', 'Consumo excesivo',
 'AK550 consume 2 litros extra por cada 100 km desde que se encendió el testigo CELP. El técnico borró el código pero vuelve a aparecer.',
 'Mezcla rica por sonda lambda averiada — sustituir sonda y recalibrar', 0.8800),

('CASE-055', 'AK550', 'Consumo excesivo',
 'Consumo excesivo detectado en larga distancia. Ralentí estable. Sin humos. Neumáticos y frenos correctos. Moto sin mantenimiento desde 14000 km.',
 'Consumo elevado por motor deteriorado — mantenimiento completo (aceite, bujías, filtros)', 0.7900),

('CASE-056', 'AK550', 'Consumo excesivo',
 'Olor a gasolina en marcha y consumo un 35% superior al normal. No hay pérdidas visibles externas. La moto funciona con normalidad.',
 'Inyector con fuga interna — provoca mezcla sobreenriquecida en todas las condiciones', 0.8600),

-- ── AK550: Vibración y ruido ─────────────────────────────────────────────────
('CASE-057', 'AK550', 'Vibración y ruido',
 'El AK550 presenta vibración intensa en el manillar a partir de 80 km/h que no existía antes.',
 'Desequilibrio de rueda delantera — equilibrar rueda dinámica y revisar neumático', 0.8700),

('CASE-058', 'AK550', 'Vibración y ruido',
 'Ruido metálico tipo "traqueteo" al arrancar en frío que desaparece a los 2-3 minutos de calentamiento.',
 'Cadena de distribución desgastada — inspeccionar tensor y sustituir si procede', 0.8400),

('CASE-059', 'AK550', 'Vibración y ruido',
 'AK550 con ruido grave y vibración en la parte trasera a velocidades medias. Se nota más en aceleración.',
 'Ruido en transmisión variador — revisar rodillos, correa y campana de embrague por desgaste', 0.8100),

('CASE-060', 'AK550', 'Vibración y ruido',
 'Vibración muy pronunciada del motor en ralentí. En rodaje desaparece. Reciente cambio de aceite con viscosidad incorrecta.',
 'Aceite de viscosidad incorrecta — sustituir por aceite SAE 10W-40 especificado por fabricante', 0.8300),

-- ── AK550: Eléctrico / Batería ───────────────────────────────────────────────
('CASE-061', 'AK550', 'Problemas de arranque',
 'El AK550 no arranca por las mañanas en invierno. La batería tiene 3 años. Al conectar cargador arranca sin problema.',
 'Batería descargada o sulfatada — sustituir batería y revisar sistema de carga (alternador/regulador)', 0.9000),

('CASE-062', 'AK550', 'Problemas de arranque',
 'El motor de arranque del AK550 gira con dificultad y lentamente aunque la batería está cargada al 100%.',
 'Motor de arranque defectuoso — desgaste de escobillas o cortocircuito interno en el devanado', 0.8500),

('CASE-063', 'AK550', 'Problemas eléctricos',
 'Las luces del AK550 parpadean intermitentemente en marcha. El regulador de tensión genera calor excesivo.',
 'Regulador-rectificador defectuoso — sustituir regulador y revisar estado del alternador', 0.8700),

('CASE-064', 'AK550', 'Problemas eléctricos',
 'El cuadro de instrumentos del AK550 se reinicia aleatoriamente en marcha. La batería tiene carga correcta.',
 'Mal contacto en conector principal del cuadro — limpiar y asegurar conectores de la centralita de instrumentos', 0.8000),

-- ── AK550: Testigo CELP adicionales ─────────────────────────────────────────
('CASE-065', 'AK550', 'Testigo CELP encendido',
 'Testigo CELP encendido tras cambio de neumático trasero. La moto funciona normalmente. Código P0500 (sensor de velocidad).',
 'Código P0500 — sensor de velocidad de rueda desconectado durante el cambio de neumático', 0.9100),

('CASE-066', 'AK550', 'Testigo CELP encendido',
 'CELP con código P0115 (sensor de temperatura de motor). La moto consume más y acelera irregular en frío.',
 'Sensor de temperatura de motor (NTC) averiado — sustituir sensor y borrar código', 0.8800),

('CASE-067', 'AK550', 'Testigo CELP encendido',
 'CELP con código P0171 (mezcla pobre). No hay pérdidas de combustible visible. Filtro de aire limpio.',
 'Sonda lambda averiada o intake con fuga de aire secundaria — verificar juntas de admisión', 0.8200),

-- ── Xciting S 400: Motor adicionales ────────────────────────────────────────
('CASE-068', 'Xciting S 400', 'Paradas de motor',
 'La Xciting se para en caliente en ciudad. Arranca al cabo de unos minutos cuando el motor ha bajado temperatura.',
 'Válvula de admisión con reglaje pisado — pérdida de compresión en caliente por dilatación', 0.8600),

('CASE-069', 'Xciting S 400', 'Paradas de motor',
 'Xciting S 400 se para intermitentemente en autopista a velocidad constante. No hay aviso previo. Arranca en seguida.',
 'Bomba de gasolina con fallo intermitente por calor — sustituir bomba y filtro de combustible', 0.8400),

('CASE-070', 'Xciting S 400', 'Paradas de motor',
 'La Xciting corta el motor al pasar por baches o aceleraciones bruscas. Rearranca inmediatamente con el contacto.',
 'Sensor de inclinación defectuoso — se activa incorrectamente por vibración o impacto', 0.8900),

-- ── Xciting S 400: Testigo CELP ─────────────────────────────────────────────
('CASE-071', 'Xciting S 400', 'Testigo CELP encendido',
 'CELP encendido en la Xciting con código P0120 (sensor TPS). La moto tiene tirones al acelerar progresivamente.',
 'Sensor TPS (posición de mariposa) desgastado o mal calibrado — sustituir o recalibrar', 0.8700),

('CASE-072', 'Xciting S 400', 'Testigo CELP encendido',
 'Xciting con código P0340 (sensor CKP/árbol de levas). Motor marcha irregular. Difícil arranque en frío.',
 'Sensor de posición de árbol de levas (CMP) averiado — limpiar o sustituir sensor', 0.8500),

('CASE-073', 'Xciting S 400', 'Testigo CELP encendido',
 'CELP encendido con código P0201 (inyector). El inyector mide resistencia correcta pero el caudal es irregular.',
 'Inyector con obstrucción parcial — limpiar con ultrasonidos o sustituir', 0.8300),

-- ── DT X360: Problemas de arranque ──────────────────────────────────────────
('CASE-074', 'DT X360', 'Problemas de arranque',
 'La DT X360 cuesta arrancar en frío. Necesita varias pulsaciones del botón de arranque. En caliente arranca bien.',
 'Bujía desgastada o gap fuera de especificación — revisar y sustituir bujía por NGK CPR8EA-9', 0.8400),

('CASE-075', 'DT X360', 'Problemas de arranque',
 'DT X360 no arranca. Motor de arranque gira fuerte. No hay chispa en bujía. Batería nueva.',
 'Bobina de encendido defectuosa — medir resistencia primaria y secundaria; sustituir si procede', 0.8600),

-- ── General / CV5 ────────────────────────────────────────────────────────────
('CASE-076', 'CV5', 'Testigo CELP encendido',
 'CV5 con testigo CELP y código P0562 (tensión baja de sistema). La batería tiene 5 años.',
 'Batería envejecida con caída de tensión bajo carga — sustituir batería y verificar regulador', 0.8500)

ON CONFLICT (case_id) DO NOTHING;
