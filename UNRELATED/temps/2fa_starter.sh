#!/bin/bash

# JULY 16
# SAMIP REGMI
#  BASIC SHELL SCRIPT 

# CONSTANTS

MYSQL_START="sudo /opt/lampp/lampp startmysql"
MYSQL_STOP="sudo /opt/lampp/lampp stopmysql"

start_services() {

    echo "[1] Running Python backend scripts..."
    python3 app.py & 
    python3 API.py & 
    python3 analysis.py &

    echo "[2] Starting MySQL..."
    $MYSQL_START

    echo "[3] Starting live-server..."
    live-server &


    echo "[4] Generating QR code for 8080..."
    qr "$(hostname -I | awk '{print $1}'):8080"
}

stop_services() {
    echo "[STOP] Killing live-server and Python services..."
    $MYSQL_STOP
    pkill -f live-server
    pkill -f app.py
    pkill -f API.py
    pkill -f analysis.py
}


# ARGUMENTS ARGV

if [[ "$1" == "1" ]]; then
    start_services
elif [[ "$1" == "0" ]]; then
    stop_services
else
    echo "Usage: ./config.sh 1 "
    echo "       ./config.sh 0 "
fi
