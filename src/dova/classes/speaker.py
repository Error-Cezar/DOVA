from dova.modules import tts
from dova.modules import printing

import re

class Speaker:
    def __init__(self):
        self.text_buffer = ""
        # Regex pattern to split on sentence boundaries
        # Handles: . ! ? (with lookahead/lookbehind for abbreviations)
        self.sentence_pattern = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s+'

    def _extract_and_process_sentences(self):
        """Extract complete sentences from buffer and process them"""
        # Split on sentence boundaries while preserving the sentences
        parts = re.split(self.sentence_pattern, self.text_buffer)

        # Process all but the last part (last part is incomplete sentence)
        for sentence in parts[:-1]:
            if sentence.strip():  # Skip empty strings
                self._tts_execute(sentence.strip())

        # Keep incomplete sentence in buffer for next addition
        self.text_buffer = parts[-1] if parts else ""

    def _tts_execute(self, sentence: str):
        """Execute TTS for a single complete sentence"""
        tts.tts(sentence)

    def add_word(self, text: str):
        """Add text to buffer. Automatically processes complete sentences."""
        if not text or not text.strip():
            return

        self.text_buffer += " " + text if self.text_buffer else text
        self._extract_and_process_sentences()

    def tts_finish(self):
        """Process any remaining incomplete sentence in buffer"""
        printing.warn(f"TTS Finish, remaining buffer size: {len(self.text_buffer)}")
        if self.text_buffer.strip():
            self._tts_execute(self.text_buffer.strip())
            self.text_buffer = ""
