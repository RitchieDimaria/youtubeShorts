
from openai import OpenAI
import os 
import requests
import sys
from dotenv import load_dotenv

ffmpeg_path = "./"  # Replace with the actual path

# Set the IMAGEIO_FFMPEG_EXE environment variable
os.environ["IMAGEIO_FFMPEG_EXE"] = ffmpeg_path

from moviepy.editor import VideoFileClip,AudioFileClip, TextClip, ImageClip, CompositeVideoClip
from moviepy.config import change_settings
from gtts import gTTS 
import random
import math
import pvleopard
import json
import time
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords

#nltk.download('punkt')
#nltk.download('stopwords')

change_settings({"FFMPEG_BINARY": "./ffmpeg"})

load_dotenv()
leopard_key = os.environ.get('LEOPARD_KEY')
openai_key = os.environ.get('OPENAI_KEY')
unsplash_key = os.environ.get('UNSPLASH_KEY')

leopard = pvleopard.create(access_key=leopard_key)
ffmpeg_params = ['-c:v', 'h264_videotoolbox']


def gen_interesting_fact(about):
    client = OpenAI(api_key=openai_key)


    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[{"role": "user", "content": "Tell me an interesting fact about {} in a small paragraph. If spoken it should last between 30-45 seconds. Start it with 'Did you know,'".format(about)}],
        max_tokens=240)

    # Access the generated response
    generated_text = response.choices[0].message.content
    print(generated_text)
    return(generated_text)

def tts(text):
    tts_obj = gTTS(text=text, lang='en', slow=False)
    tts_obj.save("assets/test.mp3") 
    #audio = AudioSegment.from_mp3("assets/test.mp3")
   #audio.speedup(playback_speed=1.5) # speed up by 1.5x
    # export to mp3
    #final.export("test.mp3", format="mp3")
    time.sleep(2)

def crop_center(video_clip, target_ratio):
    # Calculate the current aspect ratio of the video clip
    current_ratio = video_clip.size[0] / video_clip.size[1]

    # Calculate the height after cropping to maintain the target aspect ratio
    new_height = int(video_clip.size[0] / target_ratio)

    # Calculate the y-coordinate for cropping the central portion
    y_center = (video_clip.size[1] - new_height) // 2

    # Crop the video clip
    cropped_clip = video_clip.crop(y1=y_center, y2=y_center + new_height)

    return cropped_clip


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
    video_clip.reader.close()
    return(random_clip)

def add_captions(word_data,clip):
    final_clip = clip
    text_clips = []
    for i in word_data:
        text_clip = TextClip(
            i.word,
            fontsize=72,
            color='white',
            stroke_color='black',  # Border color
            stroke_width=2,  # Border width
            font='Arial',  # Change the font to Arial
        )
        text_clip=text_clip.set_duration(round(i.end_sec,2) - round(i.start_sec,2))
        text_clip=text_clip.set_position('center')
        text_clip=text_clip.set_start(round(i.start_sec,2))
        text_clips.append(text_clip)
    final_clip = CompositeVideoClip([final_clip] + text_clips)
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
    
def download_img(image_url, output_path='assets/temp_image.jpg'):
    response = requests.get(image_url)
    with open(output_path, 'wb') as f:
        f.write(response.content)

    return output_path
    
def split_list(input_list, num_splits):
    # Calculate the approximate size of each split
    avg_size = len(input_list) // num_splits
    remainder = len(input_list) % num_splits

    # Initialize the starting index
    start = 0

    # Split the list
    splits = []
    for _ in range(num_splits):
        # Determine the size of the current split
        split_size = avg_size + 1 if remainder > 0 else avg_size
        remainder -= 1

        # Extract the split from the original list
        split = input_list[start:start + split_size]

        # Update the starting index for the next split
        start += split_size

        # Append the split to the result
        splits.append(split)

    return splits
def extract_keywords(text):
    # Tokenize the text
    words = word_tokenize(text.lower())

    # Remove stopwords (common words that may not contribute much to meaning)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word.isalnum() and word not in stop_words]

    return filtered_words

def add_images(video_clip,image_urls, duration, num_images):
    img_duration = (duration/num_images) - 1
    image_clips = []
    for i in range(num_images):
        print("adding an image")
        image_path = download_img(image_urls[i], "assets/temp.png")
        image_clip = ImageClip(image_path, duration=2)
        start_time = img_duration*i + 1
        image_clip = image_clip.set_start(start_time)
        image_clip = image_clip.set_position(('center', 'center'))
        image_clips.append(image_clip)
    video_clip = CompositeVideoClip([video_clip] + image_clips)
    return video_clip

    
text = gen_interesting_fact(sys.argv[1])
image_urls = []
num_images = 4
parts = split_list(extract_keywords(text),num_images)
target_aspect_ratio = 9 / 16

for i in range(num_images):
    image_urls.append(fetch_image(parts[i]))

tts(text)
audio_clip = get_audio_clip("assets/test.mp3")
duration = math.floor(audio_clip.duration) +1
transcript = transcribe("assets/test.mp3")
unedited_clip = parkour_clip(duration)
image_clip = add_images(unedited_clip,image_urls,duration,num_images)
print("adding captions...")
captioned_clip = add_captions(transcript,image_clip)
print("adding audio...")
captioned_clip = captioned_clip.set_audio(audio_clip)
captioned_clip.write_videofile("./here.mp4", codec='libx264', audio_codec='aac',threads=4,ffmpeg_params=ffmpeg_params)


audio_clip.close()
captioned_clip.close()

#Demonic