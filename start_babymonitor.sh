#!/bin/bash

# Path to your venv
VENV_PATH="/home/martons/raspberrypi-babycam/babycam_venv"
# Path to your Flask app
APP_PATH="/home/martons/raspberrypi-babycam"

# Name of the screen session
SCREEN_NAME="babymonitor"

# Activate venv and start app in a detached screen
# screen -dmS $SCREEN_NAME bash -c "
#     source $VENV_PATH/bin/activate
#     cd $APP_PATH
#     python run.py
# "

source $VENV_PATH/bin/activate
cd $APP_PATH
python run.py