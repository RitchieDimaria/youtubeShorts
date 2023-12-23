
from openai import OpenAI
import os 
import requests
from moviepy.editor import VideoFileClip,AudioFileClip, TextClip, CompositeVideoClip
from gtts import gTTS 
import random
import math
import pvleopard
import json
import time 



with open('config.json', 'r') as config_file:
    config = json.load(config_file)

leopard_key=config.get('LEOPARD_KEY', None)
openai_key=config.get('OPENAI_KEY', None)
unsplash_key=config.get('UNSPLASH_KEY', None)

leopard = pvleopard.create(access_key=leopard_key)

def gen_interesting_fact():
    client = OpenAI(api_key=openai_key)


    response = client.completions.create(
        model="text-davinci-003",
        prompt="Tell me an interesting fact in a small paragraph. If spoken it should last between 30-45 seconds. Start it with 'Did you know,'",
        max_tokens=240)

    # Access the generated response
    generated_text = response.choices[0].text
    print(generated_text)
    return(generated_text)

def tts(text):
    tts_obj = gTTS(text=text, lang='en', slow=False)
    tts_obj.save("assets/test.mp3") 
    time.sleep(2)

def get_audio_clip(file_path):

    audio_clip = AudioFileClip(file_path)
    return audio_clip

def transcribe(voice_path):
    transcript, words = leopard.process_file(voice_path)
    return(words)

def parkour_clip(length):

    video_clip = VideoFileClip("assets/minecraft.mp4")

    video_duration = video_clip.duration

    # Set the desired duration of the random clip (30 seconds)
    clip_duration = length

    # Calculate a random starting point within the valid range
    start_time = random.uniform(0, video_duration - clip_duration)

    # Extract the random 30-second clip
    random_clip = video_clip.subclip(start_time, start_time + clip_duration)

    return(random_clip)

def add_captions(word_data,clip):
    final_clip = clip
    for i in word_data:
        text_clip = TextClip(
            i.word,
            fontsize=64,
            color='white',
            stroke_color='black',  # Border color
            stroke_width=2,  # Border width
            font='Arial',  # Change the font to Arial
        )
        text_clip = text_clip.set_duration(round(i.end_sec,2) - round(i.start_sec,2))
        text_clip = text_clip.set_position('center')
        final_clip = CompositeVideoClip([final_clip, text_clip.set_start(round(i.start_sec,2))])
    return final_clip

def fetch_image(query):
    url = f"https://api.unsplash.com/photos/random/?query={query}&client_id={unsplash_key}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        image_url = data["urls"]["regular"]
        return image_url
    else:
        print(f"Error: {response.status_code}")
        return None
    
def split_text(text, num_parts):
    # Calculate the length of each part
    part_length = len(text) // num_parts

    # Split the string into parts
    parts = [text[i * part_length:(i + 1) * part_length] for i in range(num_parts)]

    return parts

    
text = "Did you know the wattage of a lightbulb has nothing to do with its brightness? The wattage refers to the amount of energy the bulb uses to create light, while its brightness is determined by the lumens rating - the higher the lumens rating, the brighter the light. As a result, it's possible to buy bulbs that provide a brighter light than your existing ones while consuming the same amount of energy."

image_urls = []
num_images = 5
parts = split_text(text,num_images)

for i in range(num_images):
    image_urls.append(fetch_image(parts[i]))
    

#tts(text)
#audio_clip = get_audio_clip("assets/test.mp3")
#duration = math.floor(audio_clip.duration) +1
#transcript = transcribe("assets/test.mp3")
#unedited_clip = parkour_clip(duration)
#aptioned_clip = add_captions(transcript,unedited_clip)
#captioned_clip = captioned_clip.set_audio(audio_clip)
#resized_clip = captioned_clip.resize(width=720, height=1280)
#resized_clip.write_videofile("./here.mp4", codec='libx264', audio_codec='aac',threads=8)
