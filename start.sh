#!/bin/bash

# Session name
SESSION_NAME="shiroai"

# Get the directory where the script is located
SCRIPT_DIR="$(dirname "$0")"

# Check if the session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 1 ]; then
  # If the session exists, kill it
  tmux kill-session -t $SESSION_NAME
fi

# Next frontend
tmux new-session -d -s $SESSION_NAME -n 'Next.js Frontend'
tmux send-keys -t $SESSION_NAME:0 "cd $SCRIPT_DIR/frontend" C-m
tmux send-keys -t $SESSION_NAME:0 'npm run dev' C-m

# FastAPI SocketIO Backend using Poetry
tmux new-window -t $SESSION_NAME -n 'FastAPI SocketIO Backend'
tmux send-keys -t $SESSION_NAME:1 "cd $SCRIPT_DIR/backend" C-m
tmux send-keys -t $SESSION_NAME:1 'poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000 --ssl-keyfile server.key --ssl-certfile server.crt' C-m

# FastAPI REST API Backend using Poetry
tmux new-window -t $SESSION_NAME -n 'FastAPI REST API Backend'
tmux send-keys -t $SESSION_NAME:2 "cd $SCRIPT_DIR/backend" C-m
tmux send-keys -t $SESSION_NAME:2 'poetry run uvicorn rest_api:app --host 0.0.0.0 --port 8001 --ssl-keyfile server.key --ssl-certfile server.crt --log-level debug' C-m

# Create another window and start the mermaid.ink service
tmux new-window -t $SESSION_NAME -n 'Headless API'
tmux send-keys -t $SESSION_NAME:3 "cd $SCRIPT_DIR/headless-service" C-m
tmux send-keys -t $SESSION_NAME:3 'npx ts-node src/index.ts' C-m

# Attach to the tmux session and select the 'Frontend Main' window
tmux select-window -t $SESSION_NAME:0
tmux attach-session -t $SESSION_NAME