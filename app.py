from flask import Flask, Response, send_file, request
from flask_cors import CORS
from subprocess import Popen,PIPE
import re

app = Flask(__name__)
CORS(app)
def generate_video_with_progress(param):

    command = [
        'python', 'script.py', param
    ]
    process = Popen(command, stderr=PIPE, universal_newlines=True)
    
    while True:
        line = process.stderr.readline()
       
        print(line) # For debugging
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
    print(request)
    param = request.args.get('about')
    if param is None:
        param = 'anything'
    try:
        response = Response(generate_video_with_progress(param), content_type='text/event-stream')
        return response
    except Exception as e:
        print(e)
        return('Something went wrong')

@app.route('/ping',methods=['GET'])
def ping_server():
    print(request)
    return 'Server is up and running!'
@app.route('/download_video', methods=['GET'])
def download_video():
    print(request)
    video_path = './here.mp4'  
    return send_file(video_path, as_attachment=True, download_name='AI_video.mp4')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)