
from openai import OpenAI
import os 
from moviepy.editor import VideoFileClip,AudioFileClip, TextClip, CompositeVideoClip
from gtts import gTTS 
import random
import math
import pvleopard

leopard = pvleopard.create(access_key="OeefaJBTwpvqe/A5hW9BxDjo1MbU1fW7glOUenNCCzV7+5gSlGo1Zg==")

def gen_interesting_fact():
    client = OpenAI(api_key='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')


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

def get_mp3_length(file_path):

    audiofile = AudioFileClip(file_path)
    duration = math.floor(audiofile.duration) +1
    return duration

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
        text_clip = TextClip(i.word, fontsize=40, color='white')
        text_clip = text_clip.set_duration(i.end_sec - i.start_sec)
        text_clip = text_clip.set_position('center')
        final_clip = CompositeVideoClip([final_clip, text_clip.set_start(i.start_sec)])
    final_clip.write_videofile("./here.mp4", codec='libx264', audio_codec='aac')

    
text = "India has the world's oldest living tree, an Inbriagetta fig tree, located in the village of Jharkhand that is over 1,000 years old."
tts(text)
length = get_mp3_length("assets/test.mp3")
transcript = transcribe("assets/test.mp3")
unedited_clip = parkour_clip(length)
add_captions(transcript,unedited_clip)

