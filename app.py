from flask import Flask, Response, send_file, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from subprocess import Popen,PIPE
import threading 
import time
import re

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)

progress_data = {}

lock = threading.Lock()

def update_progress(task_id, progress):
    # Acquire the lock before accessing the dictionary
    with lock:
        # Update the progress for the task ID
        progress_data[task_id] = progress

# Function to read progress atomically
def read_progress(task_id):
    # Acquire the lock before accessing the dictionary
    with lock:
        # Read the progress for the task ID
        return progress_data.get(task_id, "null")

def generate_video_with_progress(task_id, param):

    command = [
        'python', 'script.py', param
    ]
    process = Popen(command, stderr=PIPE, text=True)
    
    for line in process.stderr:
        if line:
            update_progress(task_id,line)
            #print(progress_data[task_id])
            match = re.search(r"(\d+\.?\d*)%",line.strip())
            if match:

                pro = float(match.group(1))
                
                update_progress(task_id,pro)
       
        #print(line) # For debugging
        #if not line:
           # break
        #match = re.search(r"(\d+\.?\d*)%", line)

        #if match :
        #    print(match)
        #    progress_percentage = float(match.group(1))
        #    yield f"data: {progress_percentage}%\n\n"

    process.wait()
    progress_data[task_id] = "Video generation complete."
    print("Complete event sent")

@app.route('/generate_video', methods=['GET'])
def generate_video():
    print(request)
    param = request.args.get('about')
    if param is None:
        param = 'anything'
    try:
        task_id = str(time.time())
        thread = threading.Thread(target=generate_video_with_progress,args=[task_id,param])
        thread.start()
        return jsonify({'task_id': task_id, 'status': 'Video generation started'}), 202

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

@app.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    print(task_id)
    #print(progress_data)
    progress = read_progress(task_id)
    print(progress)
    return jsonify({'task_id': task_id, 'progress': progress})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
