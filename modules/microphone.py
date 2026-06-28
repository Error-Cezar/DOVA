import sounddevice  # required import to supress error / logs
import speech_recognition as sr
import vosk

from modules.printing import info, error, warn

vosk.SetLogLevel(-1)

def run_microphone() -> str | None:
    r = sr.Recognizer()
    with sr.Microphone() as source:
        info("Awaiting voice input...")
        audio = r.listen(source)

    # recognize speech using Sphinx
    try:
        detected = r.recognize_vosk(audio)
        info("Vosk thinks you said " + detected or "N/A")
        return detected or None
    except sr.UnknownValueError:
        warn("Vosk could not understand audio")
        return None
    except sr.RequestError as e:
        error("Vosk error; {0}".format(e))
        return None
