#!/bin/bash

# Get the PID of the process using port 11434
OLLAMA_PID=$(sudo lsof -i :11434 | grep LISTEN | awk '{print $2}')

# Check if the PID is found
if [ -z "$OLLAMA_PID" ]; then
    echo "No process is running on port 11434."
else
    echo "Process with PID $OLLAMA_PID is running on port 11434. Stopping the process..."
    
    # Kill the process
    sudo kill -9 $OLLAMA_PID
    
    # Check if the process was successfully killed
    if [ $? -eq 0 ]; then
        echo "Process $OLLAMA_PID stopped successfully."
    else
        echo "Failed to stop the process."
    fi
fi

