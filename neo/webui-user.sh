#!/bin/bash

# Commandline arguments for webui.py, for example: export COMMANDLINE_ARGS="--medvram --opt-split-attention"
export COMMANDLINE_ARGS="--listen --uv --cuda-malloc --cuda-stream --pin-shared-memory --enable-insecure-extension-access --skip-prepare-environment --ui-config-file /home/ubuntu/config/ui-config.json --ui-settings-file /home/ubuntu/config/config.json"

# install command for torch
export TORCH_COMMAND="pip install torch torchvision --extra-index-url https://download.pytorch.org/whl/cu128"
