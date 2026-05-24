INSERT INTO vehicles (vin, model, family, displacement_cc, market, model_year) VALUES
-- AK550 — diferentes años
('AK550-2020-0001', 'AK550', 'Scooter GT', 550, 'ES', 2020),
('AK550-2020-0002', 'AK550', 'Scooter GT', 550, 'ES', 2020),
('AK550-2021-0001', 'AK550', 'Scooter GT', 550, 'ES', 2021),
('AK550-POC-0001',  'AK550', 'Scooter GT', 550, 'ES', 2022),
('AK550-POC-0002',  'AK550', 'Scooter GT', 550, 'ES', 2023),
('AK550-POC-0003',  'AK550', 'Scooter GT', 550, 'ES', 2024),
-- AK550 Elite
('AK550E-2023-0001', 'AK550 Elite', 'Scooter GT', 550, 'ES', 2023),
('AK550E-2024-0001', 'AK550 Elite', 'Scooter GT', 550, 'ES', 2024),
-- Xciting S 400
('XCITING-POC-0001',  'Xciting S 400', 'Scooter GT', 400, 'ES', 2021),
('XCITING-2022-0001', 'Xciting S 400', 'Scooter GT', 400, 'ES', 2022),
('XCITING-2023-0001', 'Xciting S 400', 'Scooter GT', 400, 'ES', 2023),
-- CV5 Dink
('CV5-2023-0001', 'CV5', 'Scooter Urbano', 500, 'ES', 2023),
-- DT X360
('DTXS-2023-0001', 'DT X360',  'Adventure', 125, 'ES', 2023),
('DTXS-2024-0001', 'DT X360',  'Adventure', 125, 'ES', 2024),
-- Agility 125
('AGILITY-2022-0001', 'Agility 125', 'Scooter Urbano', 125, 'ES', 2022)
ON CONFLICT (vin) DO NOTHING;
