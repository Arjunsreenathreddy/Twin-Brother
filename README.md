# Digital Persona API ("Digital Arjun" Starter)

Yes — now we are actually building.

This repo contains a working MVP backend for creating a verified user and attaching a digital persona profile that can answer in that user's style.

## What is implemented
- User registration (`/users/register`)
- User verification gate (`/users/{user_id}/verify`)
- Persona create/update for verified users only (`/persona/upsert`)
- Basic chat endpoint with boundary-aware safe mode (`/chat`)
- Health check (`/health`)
- API tests for the end-to-end user journey

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- Health: `http://127.0.0.1:8000/health`

## Example flow
1. Register user:
```bash
curl -X POST http://127.0.0.1:8000/users/register \
  -H 'Content-Type: application/json' \
  -d '{"name":"Arjun","email":"arjun@example.com"}'
```

2. Verify user:
```bash
curl -X POST http://127.0.0.1:8000/users/<user_id>/verify
```

3. Create persona:
```bash
curl -X POST http://127.0.0.1:8000/persona/upsert \
  -H 'Content-Type: application/json' \
  -d '{
    "user_id":"<user_id>",
    "persona_name":"Digital Arjun",
    "speaking_style":"calm and direct",
    "beliefs":["truth first"],
    "boundaries":["financial advice"],
    "sample_phrases":["Let me think clearly"]
  }'
```

4. Chat in safe mode:
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"user_id":"<user_id>","message":"Give me financial advice","mode":"safe"}'
```

## Next build steps
- Replace in-memory stores with Postgres + pgvector.
- Add real identity verification (Persona/Onfido/Stripe Identity).
- Add auth + tenant isolation.
- Add richer memory retrieval and scoring for "sounds-like-you" confidence.
- Add frontend dashboard for profile capture and testing.
