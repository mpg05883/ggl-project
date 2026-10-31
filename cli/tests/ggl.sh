#!/bin/bash

source ./cli/utils/utils.sh
activate_uv_env

pytest tests/ggl/utils/test_path.py
pytest tests/ggl/utils/test_wandb.py