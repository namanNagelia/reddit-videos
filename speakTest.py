from IPython.display import Audio
import soundfile as sf
from threading import Thread
from transformers import AutoTokenizer
from parler_tts import ParlerTTSForConditionalGeneration, ParlerTTSStreamer
import torch
import re
from IPython.display import Audio, display
from scipy.io import wavfile
import numpy as np
# !pip install git+https: // github.com/huggingface/parler-tts.git


torch_device = "cuda:0"  # Use "mps" for Mac
torch_dtype = torch.bfloat16
model_name = "parler-tts/parler-tts-large-v1"

# need to set padding max length
max_length = 50

# load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = ParlerTTSForConditionalGeneration.from_pretrained(
    model_name,
).to(torch_device, dtype=torch_dtype)

sampling_rate = model.audio_encoder.config.sampling_rate
frame_rate = model.audio_encoder.config.frame_rate


def split_text(text, max_chunk_length=500):
    """Split text into chunks, trying to break at sentence boundaries."""
    sentences = re.split('(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chunk_length:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def generate(text, description, play_steps_in_s=0.5):
    play_steps = int(frame_rate * play_steps_in_s)
    streamer = ParlerTTSStreamer(
        model, device=torch_device, play_steps=play_steps)
    # tokenization
    inputs = tokenizer(description, return_tensors="pt").to(torch_device)
    prompt = tokenizer(text, return_tensors="pt").to(torch_device)
    # create generation kwargs
    generation_kwargs = dict(
        input_ids=inputs.input_ids,
        prompt_input_ids=prompt.input_ids,
        attention_mask=inputs.attention_mask,
        prompt_attention_mask=prompt.attention_mask,
        streamer=streamer,
        do_sample=True,
        temperature=1.0,
        min_new_tokens=10,
    )
    # initialize Thread
    thread = Thread(target=model.generate, kwargs=generation_kwargs)
    thread.start()
    # iterate over chunks of audio
    for new_audio in streamer:
        if new_audio.shape[0] == 0:
            break
        yield sampling_rate, new_audio


def generate_and_merge(text, description, chunk_size_in_s=0.5, max_text_chunk_length=500):
    all_audio_chunks = []
    text_chunks = split_text(text, max_text_chunk_length)

    for i, text_chunk in enumerate(text_chunks):
        print(f"Processing text chunk {i+1}/{len(text_chunks)}")
        for sampling_rate, audio_chunk in generate(text_chunk, description, chunk_size_in_s):
            all_audio_chunks.append(audio_chunk)
            display(Audio(audio_chunk, rate=sampling_rate))

    # Concatenate all audio chunks
    full_audio = np.concatenate(all_audio_chunks)

    # Save the full audio to a file
    output_filename = "full_audio.wav"
    wavfile.write(output_filename, sampling_rate, full_audio)

    print(f"Full audio saved to {output_filename}")

    # Return the full audio for playback
    return Audio(full_audio, rate=sampling_rate)


# Your text and description
text = """My wife was pregnant and at the time I planned to take off work near her due date. Unfortunately she went into labor early (about a month early) and I was on an inspection. I only learned about her going into labor when I got signal again. By the time I got to the hospital she had already given birth. This was about a 1.5 years ago and I am an involved father. The issue is every single time we have an argument she will bring up I missed the birth.

She knows that I couldn't control the situation but uses it as ammunition every single time we argue. I've told her that it's unfair to keep bringing this up as I had no control over the situation. She says that I should've taken off earlier just in case and that missing the birth shows I don't care. I do care and I was devastated to miss it.

I don't know how to move past this. I've suggested therapy but she refuses. I love my wife and child but I'm getting worn down by constantly being told I'm a bad father and husband for something I couldn't control. How do I get her to stop using this against me? How do we move forward?"""

description = "Mike's talking really fast."

# Generate audio chunks, display them, and get the full merged audio
full_audio = generate_and_merge(text, description, max_text_chunk_length=500)

# Play the full merged audio
display(full_audio)
