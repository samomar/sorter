#!/bin/bash

# Source conda
source ~/miniconda3/etc/profile.d/conda.sh
conda activate sorter

export NO_AT_BRIDGE=1

# Change to the directory containing the script
cd ~/Desktop/Scripts

# Run the Sorter application in the background
nohup python sorter.py > /dev/null 2>&1 &

# Deactivate conda environment
conda deactivate

# Exit the script
exit 0