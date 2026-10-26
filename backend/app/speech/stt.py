"""Speech-to-text behind a small interface, so the provider can be swapped or faked."""

from typing import Protocol

from pydantic import BaseModel


class Transcription(BaseModel):
    text: str
    confidence: float | None = None  # 0..1, None if the engine doesn't report one


class SpeechToText(Protocol):
    def transcribe(self, audio: bytes) -> Transcription: ...
