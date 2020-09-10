#!/bin/bash

# chmod u+x ./scripts/develop_venv.sh

python3 -m venv ./.venv
source ./.venv/bin/activate
pip install -U pip
pip install wheel
pip install -r ./requirements_dev.txt
pip install -r ./requirements.txt
pip install --editable .