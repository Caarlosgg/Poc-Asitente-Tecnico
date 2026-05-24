# Backend - Implementacion minima funcional

Este backend implementa un flujo funcional minimo alineado con el DDT:

- bastidor obligatorio,
- menu principal,
- arboles iniciales,
- logging por modulo en decisiones clave.

No incluye LLM ni busqueda vectorial aun.

## Arranque local

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```