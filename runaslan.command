#!/bin/bash
# runaslan.command
# Make sure this file is executable: chmod +x runaslan.command

# Change to project directory
cd ~/Coding\ projects/aslan || exit

# Activate virtual environment
source venv/bin/activate

# Run Flask app in the background
python app.py &

# Give Flask time to start
sleep 3

# Open the local server in Safari
open -a Safari http://127.0.0.1:5000

# Open the project folder in VS Code
code .

# Open a new Terminal window and run 'gemini'
osascript <<EOF
tell application "Terminal"
    do script "cd ~/Coding\ projects/aslan && gemini"
end tell
EOF

# Keep the first terminal window alive so Flask doesn’t close
wait
