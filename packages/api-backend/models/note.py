"""Note models."""

from pydantic import BaseModel


class NoteCreate(BaseModel):
    title: str
    body: str


class Note(NoteCreate):
    id: int