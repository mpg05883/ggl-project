#!/bin/bash

source ./cli/utils/utils.sh
activate_uv_env

pytest tests/ggl/pipeline/test_wandb.py