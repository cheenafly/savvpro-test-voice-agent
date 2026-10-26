"""Text-to-speech behind a small interface, so the provider can be swapped or faked."""

from typing import Protocol


class TextToSpeech(Protocol):
    mime: str

    def synthesize(self, text: str) -> bytes | None: ...


class NullTTS:
    """No server-side voice: the frontend speaks the reply with the browser's speechSynthesis."""

    mime = "audio/wav"

    def synthesize(self, text: str) -> bytes | None:
        return None
