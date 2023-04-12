import os
import threading
from threading import Lock
from threading import Semaphore

import gtts
import requests
from playsound import playsound

from configs import Config

cfg = Config()


class TextToSpeech:
    def __init__(self, cfg):
        self.cfg = cfg
        self.mutex_lock = Lock()
        self.queue_semaphore = Semaphore(1)
        self.voices = ["ErXwobaYiN019PkySvjV", "EXAVITQu4vr4xnSDxMaL"]
        self.tts_headers = {
            "Content-Type": "application/json",
            "xi-api-key": self.cfg.elevenlabs_api_key,
        }

    def eleven_labs_speech(self, text, voice_index=0):
        """Speak text using elevenlabs.io's API"""
        tts_url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}".format(
            voice_id=self.voices[voice_index]
        )
        formatted_message = {"text": text}
        response = requests.post(
            tts_url, headers=self.tts_headers, json=formatted_message
        )

        if response.status_code == 200:
            with open("temp.mp3", "wb") as f:
                f.write(response.content)
            playsound("temp.mp3")
            os.remove("temp.mp3")
        else:
            print("Error: ", response.status_code)

    def google_speech(self, text):
        """Speak text using Google's TTS API"""
        tts = gtts.gTTS(text)
        self.playsoundText(tts)

    def gtts_speech(self, text):
        tts = gtts.gTTS(text)
        with self.mutex_lock:
            self.playsoundText(tts)

    def playsoundText(self, tts):
        tts.save("temp.mp3")
        playsound("temp.mp3")
        os.remove("temp.mp3")

    def macos_tts_speech(self, text):
        os.system(f'say "{text}"')

    def queue_speech(self, text, voice_index=0):
        """Queue a speech task to be executed in a separate thread"""
        self.queue_semaphore.acquire()
        threading.Thread(target=self._queue_speech, args=(text, voice_index)).start()

    def _queue_speech(self, text, voice_index):
        self.eleven_labs_speech(text, voice_index)
        self.queue_semaphore.release()

    def speak(self, text, voice_index=0):
        if cfg.elevenlabs_api_key:
            success = self.eleven_labs_speech(text, voice_index)
            if not success:
                self.gtts_speech(text)
        elif cfg.use_mac_os_tts == "True":
            self.macos_tts_speech(text)
        else:
            self.gtts_speech(text)
        self.queue_semaphore.release()

    def say_text(self, text, voice_index=0):
        """Speak text using the best available TTS API"""
        self.queue_semaphore.acquire(True)
        thread = threading.Thread(target=self.speak)
        thread.start()
