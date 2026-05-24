-- ─────────────────────────────────────────────────────────────────────────────
-- vehicles_enrichment.sql
-- Bastidores adicionales para todos los modelos disponibles.
-- Usados para demostración y pruebas del flujo completo.
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO vehicles (vin, model, family, displacement_cc, market, model_year)
VALUES
  -- ── AK550 (Sport Maxi 550cc) ──────────────────────────────────────────────
  ('AK550-2022-0001', 'AK550', 'AK', 550, 'ES', 2022),
  ('AK550-2022-0002', 'AK550', 'AK', 550, 'ES', 2022),
  ('AK550-2023-0001', 'AK550', 'AK', 550, 'ES', 2023),
  ('AK550-2023-0002', 'AK550', 'AK', 550, 'FR', 2023),
  ('AK550-2024-0001', 'AK550', 'AK', 550, 'ES', 2024),
  ('AK550-2025-0001', 'AK550', 'AK', 550, 'ES', 2025),
  ('AK550-POC-0004',  'AK550', 'AK', 550, 'ES', 2023),
  ('AK550-POC-0005',  'AK550', 'AK', 550, 'ES', 2024),

  -- ── AK550 Elite (versión premium) ─────────────────────────────────────────
  ('AK550E-POC-0001', 'AK550 Elite', 'AK', 550, 'ES', 2023),
  ('AK550E-POC-0002', 'AK550 Elite', 'AK', 550, 'ES', 2024),
  ('AK550E-2025-0001','AK550 Elite', 'AK', 550, 'ES', 2025),

  -- ── Xciting S 400 (Sport Maxi 400cc) ──────────────────────────────────────
  ('XCITING-POC-0002', 'Xciting S 400', 'Xciting', 399, 'ES', 2023),
  ('XCITING-POC-0003', 'Xciting S 400', 'Xciting', 399, 'ES', 2024),
  ('XCITING-2024-0001','Xciting S 400', 'Xciting', 399, 'ES', 2024),
  ('XCITING-2024-0002','Xciting S 400', 'Xciting', 399, 'DE', 2024),
  ('XCITING-2025-0001','Xciting S 400', 'Xciting', 399, 'ES', 2025),

  -- ── CV5 (Scooter eléctrico) ───────────────────────────────────────────────
  ('CV5-POC-0001',  'CV5', 'CV', NULL, 'ES', 2023),
  ('CV5-POC-0002',  'CV5', 'CV', NULL, 'ES', 2024),
  ('CV5-POC-0003',  'CV5', 'CV', NULL, 'ES', 2024),
  ('CV5-2024-0001', 'CV5', 'CV', NULL, 'ES', 2024),
  ('CV5-2024-0002', 'CV5', 'CV', NULL, 'FR', 2024),
  ('CV5-2025-0001', 'CV5', 'CV', NULL, 'ES', 2025),

  -- ── DT X360 (Adventure 350cc) ─────────────────────────────────────────────
  ('DTXS-POC-0001',  'DT X360', 'DT', 350, 'ES', 2023),
  ('DTXS-POC-0002',  'DT X360', 'DT', 350, 'ES', 2024),
  ('DTXS-2025-0001', 'DT X360', 'DT', 350, 'ES', 2025),

  -- ── Agility 125 (Scooter urbano) ──────────────────────────────────────────
  ('AGILITY-POC-0001',  'Agility 125', 'Agility', 125, 'ES', 2022),
  ('AGILITY-POC-0002',  'Agility 125', 'Agility', 125, 'ES', 2023),
  ('AGILITY-2023-0001', 'Agility 125', 'Agility', 125, 'ES', 2023),
  ('AGILITY-2024-0001', 'Agility 125', 'Agility', 125, 'ES', 2024)

ON CONFLICT (vin) DO NOTHING;
