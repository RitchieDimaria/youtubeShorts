How to run server:

Switch to proper directory

cd /home/ritchiedima/youtubeShorts 

Enable virtual environment

source venv/bin/activate

open tmux session

tmux new-session -s backendsesh

run server in tmux session

gunicorn -c gunicorn.conf.py app:app

exit tmux session

ctrl+B, D
