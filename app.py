from flask import Flask, Response, send_file
from flask_cors import CORS
from subprocess import Popen,PIPE
import re

app = Flask(__name__)
CORS(app)
def generate_video_with_progress():

    command = [
        'python', 'script.py'
    ]
    process = Popen(command, stderr=PIPE, universal_newlines=True)
    
    while True:
        line = process.stderr.readline()
        if not line:
            break
        match = re.search(r"(\d+\.?\d*)%", line)
        if match:
            progress_percentage = float(match.group(1))
            yield f"data: {progress_percentage}%\n\n"

    process.wait()
    yield "data: 100%\n\n"
    yield "event: complete\n\n"
    print("Complete event sent")

@app.route('/generate_video', methods=['GET'])
def generate_video():
    
    return Response(generate_video_with_progress(), content_type='text/event-stream')

@app.route('/download_video', methods=['GET'])
def download_video():
    video_path = './here.mp4'  
    return send_file(video_path, as_attachment=True, download_name='AI_video.mp4')


if __name__ == '__main__':
    app.run(debug=True)