from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Literal, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Digital Persona API", version="0.1.0")


class User(BaseModel):
    user_id: str
    name: str
    email: str
    is_verified: bool = False
    created_at: datetime


class PersonaProfile(BaseModel):
    user_id: str
    persona_name: str = Field(..., description="e.g. Digital Arjun")
    speaking_style: str = Field(..., description="Tone and writing style")
    beliefs: List[str] = Field(default_factory=list)
    boundaries: List[str] = Field(default_factory=list)
    sample_phrases: List[str] = Field(default_factory=list)
    updated_at: datetime


class RegisterUserRequest(BaseModel):
    name: str
    email: str


class RegisterUserResponse(BaseModel):
    user: User


class VerifyUserResponse(BaseModel):
    user: User


class UpsertPersonaRequest(BaseModel):
    user_id: str
    persona_name: str
    speaking_style: str
    beliefs: List[str] = Field(default_factory=list)
    boundaries: List[str] = Field(default_factory=list)
    sample_phrases: List[str] = Field(default_factory=list)


class UpsertPersonaResponse(BaseModel):
    persona: PersonaProfile


class ChatRequest(BaseModel):
    user_id: str
    message: str
    mode: Literal["exact", "safe"] = "safe"


class ChatResponse(BaseModel):
    reply: str
    persona_found: bool


USERS: Dict[str, User] = {}
PERSONAS: Dict[str, PersonaProfile] = {}


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "service": "digital-persona-api"}


@app.post("/users/register", response_model=RegisterUserResponse)
def register_user(payload: RegisterUserRequest) -> RegisterUserResponse:
    user_id = str(uuid4())
    user = User(
        user_id=user_id,
        name=payload.name.strip(),
        email=payload.email.strip().lower(),
        is_verified=False,
        created_at=now_utc(),
    )
    USERS[user_id] = user
    return RegisterUserResponse(user=user)


@app.post("/users/{user_id}/verify", response_model=VerifyUserResponse)
def verify_user(user_id: str) -> VerifyUserResponse:
    user = USERS.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    USERS[user_id] = user
    return VerifyUserResponse(user=user)


@app.post("/persona/upsert", response_model=UpsertPersonaResponse)
def upsert_persona(payload: UpsertPersonaRequest) -> UpsertPersonaResponse:
    user = USERS.get(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User must be verified before creating a persona")

    persona = PersonaProfile(
        user_id=payload.user_id,
        persona_name=payload.persona_name,
        speaking_style=payload.speaking_style,
        beliefs=payload.beliefs,
        boundaries=payload.boundaries,
        sample_phrases=payload.sample_phrases,
        updated_at=now_utc(),
    )
    PERSONAS[payload.user_id] = persona
    return UpsertPersonaResponse(persona=persona)


def _blocked(boundaries: List[str], message: str) -> Optional[str]:
    lowered = message.lower()
    for boundary in boundaries:
        b = boundary.lower().strip()
        if b and b in lowered:
            return boundary
    return None


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    user = USERS.get(payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    persona = PERSONAS.get(payload.user_id)
    if not persona:
        return ChatResponse(
            reply="I do not have your digital profile yet. Please complete persona setup first.",
            persona_found=False,
        )

    blocked_term = _blocked(persona.boundaries, payload.message)
    if payload.mode == "safe" and blocked_term:
        return ChatResponse(
            reply=(
                f"I am avoiding this topic because it matches your boundary: '{blocked_term}'. "
                "Would you like me to answer in a safer way?"
            ),
            persona_found=True,
        )

    phrase = persona.sample_phrases[0] if persona.sample_phrases else "Here is how I see it"
    belief = persona.beliefs[0] if persona.beliefs else "clarity over noise"
    reply = (
        f"{phrase}. Based on your style ({persona.speaking_style}), "
        f"I'd answer: {payload.message} — and keep {belief} in mind."
    )

    return ChatResponse(reply=reply, persona_found=True)
