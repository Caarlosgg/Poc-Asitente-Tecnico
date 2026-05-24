# Details

Date : 2026-05-24 20:07:04

Directory c:\\Users\\Carlos\\Desktop\\Proyectos\\poc-asistente-tecnico

Total : 92 files,  7981 codes, 709 comments, 1625 blanks, all 10315 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [PROJECT\_CONTEXT.md](/PROJECT_CONTEXT.md) | Markdown | 938 | 0 | 134 | 1,072 |
| [PROJECT\_CONTEXT2.md](/PROJECT_CONTEXT2.md) | Markdown | 1,017 | 0 | 125 | 1,142 |
| [README.md](/README.md) | Markdown | 469 | 0 | 126 | 595 |
| [backend/.dockerignore](/backend/.dockerignore) | Ignore | 20 | 7 | 7 | 34 |
| [backend/Dockerfile](/backend/Dockerfile) | Docker | 11 | 3 | 7 | 21 |
| [backend/README.md](/backend/README.md) | Markdown | 12 | 0 | 5 | 17 |
| [backend/api/\_\_init\_\_.py](/backend/api/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/api/routes/\_\_init\_\_.py](/backend/api/routes/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/api/routes/feedback.py](/backend/api/routes/feedback.py) | Python | 71 | 10 | 18 | 99 |
| [backend/api/routes/metrics.py](/backend/api/routes/metrics.py) | Python | 65 | 16 | 16 | 97 |
| [backend/api/routes/session.py](/backend/api/routes/session.py) | Python | 273 | 39 | 55 | 367 |
| [backend/api/schemas/\_\_init\_\_.py](/backend/api/schemas/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/api/schemas/feedback.py](/backend/api/schemas/feedback.py) | Python | 9 | 3 | 8 | 20 |
| [backend/api/schemas/session.py](/backend/api/schemas/session.py) | Python | 36 | 6 | 17 | 59 |
| [backend/core/\_\_init\_\_.py](/backend/core/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/core/config.py](/backend/core/config.py) | Python | 12 | 4 | 9 | 25 |
| [backend/core/database.py](/backend/core/database.py) | Python | 30 | 3 | 10 | 43 |
| [backend/core/exceptions.py](/backend/core/exceptions.py) | Python | 20 | 6 | 16 | 42 |
| [backend/db/migrations/init.sql](/backend/db/migrations/init.sql) | MS SQL | 144 | 17 | 18 | 179 |
| [backend/db/seeds/diagnostic\_trees.sql](/backend/db/seeds/diagnostic_trees.sql) | MS SQL | 70 | 0 | 4 | 74 |
| [backend/db/seeds/faqs.sql](/backend/db/seeds/faqs.sql) | MS SQL | 82 | 14 | 26 | 122 |
| [backend/db/seeds/historical\_cases.sql](/backend/db/seeds/historical_cases.sql) | MS SQL | 156 | 14 | 51 | 221 |
| [backend/db/seeds/knowledge\_chunks.sql](/backend/db/seeds/knowledge_chunks.sql) | MS SQL | 29 | 7 | 3 | 39 |
| [backend/db/seeds/vehicles.sql](/backend/db/seeds/vehicles.sql) | MS SQL | 17 | 6 | 1 | 24 |
| [backend/main.py](/backend/main.py) | Python | 42 | 6 | 14 | 62 |
| [backend/models/\_\_init\_\_.py](/backend/models/__init__.py) | Python | 20 | 1 | 3 | 24 |
| [backend/models/decision\_log.py](/backend/models/decision_log.py) | Python | 20 | 2 | 9 | 31 |
| [backend/models/feedback.py](/backend/models/feedback.py) | Python | 21 | 2 | 9 | 32 |
| [backend/models/knowledge.py](/backend/models/knowledge.py) | Python | 42 | 1 | 16 | 59 |
| [backend/models/knowledge\_chunk.py](/backend/models/knowledge_chunk.py) | Python | 44 | 6 | 14 | 64 |
| [backend/models/message.py](/backend/models/message.py) | Python | 18 | 2 | 9 | 29 |
| [backend/models/session.py](/backend/models/session.py) | Python | 51 | 3 | 14 | 68 |
| [backend/models/vehicle.py](/backend/models/vehicle.py) | Python | 17 | 2 | 9 | 28 |
| [backend/orchestrator/\_\_init\_\_.py](/backend/orchestrator/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/orchestrator/graph.py](/backend/orchestrator/graph.py) | Python | 140 | 35 | 39 | 214 |
| [backend/orchestrator/nodes/\_\_init\_\_.py](/backend/orchestrator/nodes/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/orchestrator/nodes/classifier.py](/backend/orchestrator/nodes/classifier.py) | Python | 182 | 32 | 24 | 238 |
| [backend/orchestrator/nodes/faq\_matcher.py](/backend/orchestrator/nodes/faq_matcher.py) | Python | 136 | 28 | 29 | 193 |
| [backend/orchestrator/nodes/free\_text.py](/backend/orchestrator/nodes/free_text.py) | Python | 152 | 21 | 27 | 200 |
| [backend/orchestrator/nodes/menu.py](/backend/orchestrator/nodes/menu.py) | Python | 49 | 7 | 15 | 71 |
| [backend/orchestrator/nodes/tree\_engine.py](/backend/orchestrator/nodes/tree_engine.py) | Python | 184 | 16 | 30 | 230 |
| [backend/orchestrator/nodes/vin\_lookup.py](/backend/orchestrator/nodes/vin_lookup.py) | Python | 99 | 8 | 17 | 124 |
| [backend/orchestrator/state.py](/backend/orchestrator/state.py) | Python | 19 | 2 | 5 | 26 |
| [backend/pytest.ini](/backend/pytest.ini) | Ini | 6 | 0 | 1 | 7 |
| [backend/requirements.txt](/backend/requirements.txt) | pip requirements | 14 | 8 | 9 | 31 |
| [backend/services/\_\_init\_\_.py](/backend/services/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/services/groq\_client.py](/backend/services/groq_client.py) | Python | 161 | 53 | 29 | 243 |
| [backend/services/ranking.py](/backend/services/ranking.py) | Python | 67 | 40 | 27 | 134 |
| [backend/services/response\_builder.py](/backend/services/response_builder.py) | Python | 104 | 31 | 21 | 156 |
| [backend/services/tracing.py](/backend/services/tracing.py) | Python | 87 | 32 | 13 | 132 |
| [backend/tests/\_\_init\_\_.py](/backend/tests/__init__.py) | Python | 0 | 1 | 1 | 2 |
| [backend/tests/test\_faq\_matcher.py](/backend/tests/test_faq_matcher.py) | Python | 62 | 5 | 18 | 85 |
| [backend/tests/test\_free\_text.py](/backend/tests/test_free_text.py) | Python | 103 | 6 | 20 | 129 |
| [backend/tests/test\_tree\_engine.py](/backend/tests/test_tree_engine.py) | Python | 91 | 4 | 24 | 119 |
| [backend/tests/test\_vin\_lookup.py](/backend/tests/test_vin_lookup.py) | Python | 71 | 6 | 23 | 100 |
| [docker-compose.yml](/docker-compose.yml) | YAML | 58 | 2 | 5 | 65 |
| [docs/DDT.md](/docs/DDT.md) | Markdown | 709 | 0 | 131 | 840 |
| [docs/diagrams/database-er.mmd](/docs/diagrams/database-er.mmd) | Mermaid Radar | 91 | 0 | 10 | 101 |
| [docs/diagrams/flujo-asistente.mmd](/docs/diagrams/flujo-asistente.mmd) | Mermaid Radar | 19 | 0 | 5 | 24 |
| [docs/flujos-guiados-control-operativo.md](/docs/flujos-guiados-control-operativo.md) | Markdown | 125 | 0 | 49 | 174 |
| [docs/pruebas-flujos-guiados.md](/docs/pruebas-flujos-guiados.md) | Markdown | 108 | 0 | 77 | 185 |
| [erDiagram.mmd](/erDiagram.mmd) | Mermaid Radar | 122 | 0 | 12 | 134 |
| [frontend/Dockerfile](/frontend/Dockerfile) | Docker | 14 | 2 | 12 | 28 |
| [frontend/README.md](/frontend/README.md) | Markdown | 20 | 0 | 10 | 30 |
| [frontend/index.html](/frontend/index.html) | HTML | 14 | 0 | 1 | 15 |
| [frontend/package.json](/frontend/package.json) | JSON | 29 | 0 | 1 | 30 |
| [frontend/postcss.config.js](/frontend/postcss.config.js) | JavaScript | 6 | 0 | 1 | 7 |
| [frontend/src/App.jsx](/frontend/src/App.jsx) | JavaScript JSX | 72 | 6 | 11 | 89 |
| [frontend/src/components/Chat/ChatContainer.jsx](/frontend/src/components/Chat/ChatContainer.jsx) | JavaScript JSX | 189 | 21 | 27 | 237 |
| [frontend/src/components/Chat/InputBar.jsx](/frontend/src/components/Chat/InputBar.jsx) | JavaScript JSX | 41 | 4 | 5 | 50 |
| [frontend/src/components/Chat/MenuOptions.jsx](/frontend/src/components/Chat/MenuOptions.jsx) | JavaScript JSX | 61 | 6 | 5 | 72 |
| [frontend/src/components/Chat/MessageBubble.jsx](/frontend/src/components/Chat/MessageBubble.jsx) | JavaScript JSX | 77 | 11 | 12 | 100 |
| [frontend/src/components/Chat/QuickReplies.jsx](/frontend/src/components/Chat/QuickReplies.jsx) | JavaScript JSX | 23 | 3 | 2 | 28 |
| [frontend/src/components/Chat/RouteHeader.jsx](/frontend/src/components/Chat/RouteHeader.jsx) | JavaScript JSX | 36 | 9 | 5 | 50 |
| [frontend/src/components/Diagnosis/ConfidenceBadge.jsx](/frontend/src/components/Diagnosis/ConfidenceBadge.jsx) | JavaScript JSX | 17 | 4 | 3 | 24 |
| [frontend/src/components/Diagnosis/DiagnosisResult.jsx](/frontend/src/components/Diagnosis/DiagnosisResult.jsx) | JavaScript JSX | 76 | 13 | 13 | 102 |
| [frontend/src/components/Diagnosis/HypothesisList.jsx](/frontend/src/components/Diagnosis/HypothesisList.jsx) | JavaScript JSX | 21 | 3 | 2 | 26 |
| [frontend/src/components/UI/ErrorMessage.jsx](/frontend/src/components/UI/ErrorMessage.jsx) | JavaScript JSX | 17 | 3 | 1 | 21 |
| [frontend/src/components/UI/FeedbackModal.jsx](/frontend/src/components/UI/FeedbackModal.jsx) | JavaScript JSX | 87 | 3 | 8 | 98 |
| [frontend/src/components/UI/PhaseBar.jsx](/frontend/src/components/UI/PhaseBar.jsx) | JavaScript JSX | 51 | 7 | 5 | 63 |
| [frontend/src/components/UI/Spinner.jsx](/frontend/src/components/UI/Spinner.jsx) | JavaScript JSX | 8 | 3 | 1 | 12 |
| [frontend/src/hooks/useChat.js](/frontend/src/hooks/useChat.js) | JavaScript | 82 | 17 | 12 | 111 |
| [frontend/src/hooks/useSession.js](/frontend/src/hooks/useSession.js) | JavaScript | 35 | 6 | 7 | 48 |
| [frontend/src/index.css](/frontend/src/index.css) | PostCSS | 18 | 2 | 4 | 24 |
| [frontend/src/main.jsx](/frontend/src/main.jsx) | JavaScript JSX | 9 | 0 | 2 | 11 |
| [frontend/src/services/api.js](/frontend/src/services/api.js) | JavaScript | 42 | 37 | 10 | 89 |
| [frontend/src/utils/messageTypes.js](/frontend/src/utils/messageTypes.js) | JavaScript | 11 | 10 | 3 | 24 |
| [frontend/tailwind.config.js](/frontend/tailwind.config.js) | JavaScript | 14 | 1 | 1 | 16 |
| [frontend/vite.config.js](/frontend/vite.config.js) | JavaScript | 22 | 2 | 2 | 26 |
| [scripts/reset\_db.sh](/scripts/reset_db.sh) | Shell Script | 27 | 3 | 7 | 37 |
| [scripts/run-flujo-guiado.ps1](/scripts/run-flujo-guiado.ps1) | PowerShell | 133 | 7 | 21 | 161 |
| [scripts/seed\_db.sh](/scripts/seed_db.sh) | Shell Script | 14 | 2 | 10 | 26 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)