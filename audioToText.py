import speech_recognition as sr
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
import sys
import base64
import shutil


def audio_to_text(path):
    r = sr.Recognizer()
    def get_large_audio_transcription():

        sound = AudioSegment.from_mp3(path)
        chunks = split_on_silence(sound,
                                  min_silence_len=500,
                                  silence_thresh=sound.dBFS - 14,
                                  keep_silence=500,
                                  )
        folder_name = os.path.join(os.path.dirname(__file__), "audio-chunks")
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        for i, audio_chunk in enumerate(chunks, start=1):
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                try:
                    text = r.recognize_google(audio_listened, language="en")
                except sr.UnknownValueError as e:
                    pass
                else:
                    text = f"{text} "
                    whole_text += text
        return whole_text

    text = get_large_audio_transcription()

    try:
        shutil.rmtree(os.path.join(os.path.dirname(__file__), "audio-chunks"))
    except Exception:
        print(Exception)
        exit(1)
    return text
