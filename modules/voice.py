from typing import TypedDict

import modules.microphone as microphone


class DetectionResult(TypedDict):
    detected: str
    wake: bool
    normal: bool


wake_words = [
    "wake up"
]


def is_wake_word(text):
    """Check if the text is a wake word."""
    for wake_word in wake_words:
        if text.lower() == wake_word:
            return True
    return False


def is_wake_normal_word(text):
    """Check if the text starts with a wake word."""
    for wake_word in wake_words:
        if text.lower().startswith(wake_word):
            return True
    return False


def run_detection() -> DetectionResult:
    """Run wake word detection and trigger appropriate callbacks."""
    word = microphone.run_microphone()

    if word:
        if is_wake_word(word):
            return {"detected": word, "wake": True, "normal": False}
        elif is_wake_normal_word(word):
            return {"detected": word, "wake": True, "normal": True}
        else:
            return {"detected": word, "wake": False, "normal": True}
    else:
        return {"detected": "", "wake": False, "normal": False}
