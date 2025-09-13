#!/bin/bash

SCRIPT_DIR="$(dirname "$(realpath "$0")")"  # Get the absolute path of the script (app) directory
echo "Script directory: $SCRIPT_DIR"
VENV_PATH="$SCRIPT_DIR/babycam_venv"
# SCREEN_NAME="babymonitor" # Name of the screen session

# Activate venv and start app in a detached screen
# screen -dmS $SCREEN_NAME bash -c "
#     source $VENV_PATH/bin/activate
#     cd $APP_PATH
#     python run.py
# "

source $VENV_PATH/bin/activate
cd $SCRIPT_DIR
python run.py