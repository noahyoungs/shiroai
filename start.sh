#!/bin/bash

# Session name
SESSION_NAME="ai-presenter"

# Check if the session already exists
tmux has-session -t $SESSION_NAME 2>/dev/null

if [ $? != 1 ]; then
  # If the session exists, kill it
  tmux kill-session -t $SESSION_NAME
fi

# Start a new tmux session named 'ai-presenter' with the first window named 'Frontend Main'
tmux new-session -d -s $SESSION_NAME -n 'Frontend Main'
tmux send-keys -t $SESSION_NAME:0 'cd /Users/noahyoungs/VSCode/ai-presenter-v2/frontend' C-m
tmux send-keys -t $SESSION_NAME:0 'npm run dev' C-m

# Create a new window named 'Backend Main'
tmux new-window -t $SESSION_NAME -n 'Backend Main'
tmux send-keys -t $SESSION_NAME:1 'cd /Users/noahyoungs/VSCode/ai-presenter-v2/backend' C-m
tmux send-keys -t $SESSION_NAME:1 'uvicorn main:app --reload' C-m

# Create a new window and start the backend icon API router
tmux new-window -t $SESSION_NAME -n 'REST API'
tmux send-keys -t $SESSION_NAME:2 'cd /Users/noahyoungs/VSCode/ai-presenter-v2/backend' C-m
tmux send-keys -t $SESSION_NAME:2 'uvicorn rest_api:app --host 0.0.0.0 --port 8001 --log-level debug' C-m

# Create another window and start the mermaid.ink service
tmux new-window -t $SESSION_NAME -n 'Mermaid Ink'
tmux send-keys -t $SESSION_NAME:3 'cd ~/mermaid.ink' C-m
tmux send-keys -t $SESSION_NAME:3 'export COREPACK_ENABLE_STRICT=0' C-m
tmux send-keys -t $SESSION_NAME:3 'DEBUG=app:* PORT=3002 pnpm start' C-m

# Attach to the tmux session and select the 'Frontend Main' window
tmux select-window -t $SESSION_NAME:0
tmux attach-session -t $SESSION_NAME
