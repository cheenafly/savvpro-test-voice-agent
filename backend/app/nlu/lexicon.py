"""Loads the YAML vocabulary in nlu/data once per process."""

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

DATA_DIR = Path(__file__).parent / "data"
LEXICON_PATH = DATA_DIR / "lexicon.yaml"
INTENTS_PATH = DATA_DIR / "intents.yaml"


@lru_cache
def load_lexicon() -> dict[str, Any]:
    with LEXICON_PATH.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_intents(path: Path = INTENTS_PATH) -> dict[str, list[str]]:
    with path.open(encoding="utf-8") as f:
        return {
            intent: [str(u) for u in utterances] for intent, utterances in yaml.safe_load(f).items()
        }
