from google.cloud import texttospeech
from pydub import AudioSegment
from pydub.silence import split_on_silence
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './redditGoogleKey.json'


def convert_text_to_speech(text, filename, voice_name="en-US-Neural2-J"):
    client = texttospeech.TextToSpeechClient()

    # Use SSML to add breaks and emphasis for more natural speech
    ssml_text = f"""
    <speak>
      {text}
    </speak>
    """

    synthesis_input = texttospeech.SynthesisInput(ssml=ssml_text)

    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name=voice_name,
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=1.0,
        pitch=0,
        volume_gain_db=0,
        effects_profile_id=["medium-bluetooth-speaker-class-device"]
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("temp.mp3", "wb") as out:
        out.write(response.audio_content)
        print(f'Audio content written to file "temp.mp3"')

    audio = AudioSegment.from_mp3("temp.mp3")

    chunks = split_on_silence(
        audio, silence_thresh=-40, min_silence_len=300, keep_silence=100
    )

    trimmed_audio = AudioSegment.empty()
    for chunk in chunks:
        trimmed_audio += chunk

    trimmed_audio.export(filename, format="mp3")
    print(f"Saved TTS audio to {filename}")

    os.remove("temp.mp3")


# Example usage
text_to_convert = """
Hello! This is an example of more natural-sounding text-to-speech. 
We're using advanced settings to make the voice sound more human-like.
Pauses and emphasis are added automatically to improve the flow of speech.
"""

convert_text_to_speech(text_to_convert, "natural_output.mp3")
