# # !pip install git+https://github.com/huggingface/parler-tts.git
import torch

from parler_tts import ParlerTTSForConditionalGeneration
from transformers import AutoTokenizer
import soundfile as sf

device = "mps" if torch.backends.mps.is_available() else "cpu"
device = "cpu"
print(device)
model = ParlerTTSForConditionalGeneration.from_pretrained(
    "parler-tts/parler-tts-large-v1").to(device)
tokenizer = AutoTokenizer.from_pretrained("parler-tts/parler-tts-large-v1")
prompt = " AITA for telling my wife that she needs to get over me missing the birth of our daughter', 'I work in a job where they are certain times that I do not have access to my phone or I I am in the middle of nowhere.These times are well scheduled in advance and basically take up my whole day. There are a ton safety regulations I have to follow  during this time.\n\nMy wife was pregnant and at the time I planned to take off work near her due date. Unfortunately she went into labor early ( about a month early) and I was on an inspection.  I only learned about her going into labor when I got signal again. By the time I got to the hospital she has already given birth.\n\nThis was about a 1.5 years ago and I am involved father. The issue is every single time we have an argument she will bring up I missed the birth. It happens almost every single time form serious arguments to what fastfood should we get. Today was my breaking point, we got into an argument about her wanting to change the daycare situation. She wants to change daycare to one closer to the home. I do drop off and she does pick up. The only one closer to our home is too expensive and we can not afford it.\n\nIn the middle of the argument she pulled out I wasn’t there for the birth again.  I told her she needs to get over that and stop using it in every fucking argument we have. She called me a jerk and left?"
description = "Jon's voice is monotone in delivery, with a very clear recording that almost has no background noise."

input_ids = tokenizer(description, return_tensors="pt").input_ids.to(device)
prompt_input_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)

generation = model.generate(
    input_ids=input_ids, prompt_input_ids=prompt_input_ids)
audio_arr = generation.cpu().numpy().squeeze()
sf.write("parler_tts_out.wav", audio_arr, model.config.sampling_rate)


# # 1. Make a DB whcih has all reddit links, title, script, tags, etc etc
# # 2: Get sound file on GPU once a week and upload to supabase
# # 3: Make video
