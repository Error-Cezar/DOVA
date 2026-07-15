import queue
import threading

import pyttsx3

tts_queue = queue.Queue()
engine = pyttsx3.init()

def tts(text):
    """Queue text for TTS, splitting into sentences."""
    sentences = text
    tts_queue.put(sentences)


def wait_for_tts():
    """Wait for all queued TTS items to be processed."""
    tts_queue.join()


# Start a separate thread to process the TTS queue
def tts_thread():
    while True:
        text = tts_queue.get()
        if text is None:  # Exit signal
            break
        try:
            engine.say(text)
            engine.runAndWait()
        finally:
            tts_queue.task_done()


threading.Thread(target=tts_thread, daemon=True).start()
