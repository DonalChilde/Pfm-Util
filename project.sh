#!/usr/bin/env bash

# Master copy located at pfm_util
# Version 1.0
# 2021-03-15T16:27:09Z
# Note: this script expects to live in the top directory of a project.

#https://github.com/nickjj/docker-flask-example/blob/main/run

# -e Exit immediately if a pipeline returns a non-zero status.
# -u Treat unset variables and parameters other than the special parameters ‘@’ or ‘*’ as an error when performing parameter expansion.
# -o pipefail If set, the return value of a pipeline is the value of the last (rightmost) command to exit with a non-zero status, or zero if all commands in the pipeline exit successfully.
set -euo pipefail

# TODO make completions for script.
# https://iridakos.com/programming/2018/03/01/bash-programmable-completion-tutorial
# TODO make a more detailed help.
# TODO add check to make sure that we are piping to the correct virtual env.

PACKAGE="${PACKAGE:-pfmsoft}"
SRC_PATH="src/"
BROWSER="google-chrome"
CODE_PATHS=("./src" "./tests")

function project:init:dirs() {
    # make the project subdirectories. I think cookiecutter is better here
    DIRS=("./src/pfmsoft" "./docs" "./tests/pfmsoft")
    for d in "${DIRS[@]}"; do
        mkdir -p "$d"
    done
    FILES=("./setup.cfg" "./setup.py" "tox.ini" "requirements.txt" "requirements_dev.txt"
        "pyproject.toml" "MANIFEST.in" "LICENSE" "HISTORY.rst" "CONTRIBUTING.rst" "AUTHORS.rst"
        ".pre-commit-config.yaml" "README.rst" ".gitignore" ".coveragerc"
        "./src/pfmsoft/__init__.py" "./tests/pfmsoft/__init__.py" "./tests/__init__.py")
    for f in "${FILES[@]}"; do
        touch "$f"
    done
}

function project:init:all() {

    project:init:dirs
    venv:init
    pip3:install:all
}

function project:reset_venv() {
    venv:remove
    venv:init
    pip3:install:all

}

function project:install:editable() {
    # shellcheck disable=SC1091
    _pip3 install --editable .
}

function venv:init() {
    # makes a venv and installs dev dependencies
    python3 -m venv ./.venv
    # shellcheck disable=SC1091
    source ./.venv/bin/activate
    PIP_REQUIRE_VIRTUALENV=true pip install -U pip setuptools wheel
}

function venv:remove() {
    # removes a venv
    printf "\nDeleting ./.venv deactivate any terminal windows that were using that venv.\n"
    deactivate || true
    rm -r ./.venv/ || true
}

function _pip3() {
    printf "\nUsing virtual env located at:\n%s\n" "$VIRTUAL_ENV"
    PIP_REQUIRE_VIRTUALENV=true pip3 "${@}"
}

function pip3:install() {
    # shellcheck disable=SC1091
    # source ./.venv/bin/activate
    _pip3 install "${@}"
}

function pip3:uninstall() {
    _pip3 uninstall "${@}"
}

function pip3:install:all() {
    _pip3 install -r ./requirements_dev.txt
    _pip3 install -r ./requirements.txt
}

function pip3:outdated() {
    # List any installed packages that are outdated
    _pip3 list --outdated
}

function pip3:upgrade() {
    _pip3 install "${@}" --upgrade
}

function pip3:upgrade:all() {
    _pip3 install $(cat ./requirements.txt | sed /^\#/d | tr '\n' ' ') --upgrade
    _pip3 install $(cat ./requirements_dev.txt | sed /^\#/d | tr '\n' ' ') --upgrade
    # _pip3 install "$(pip list --outdated | tail +3 | grep -v sdist | awk '{ print $1 }')" --upgrade
}

function pytest() {
    # Run test suite with pytest
    python3 -m pytest tests/ "${@}"
}

function pytest-cov() {
    # Get test coverage with pytest-cov
    python3 -m pytest --cov test/ --cov-report term-missing "${@}"
}

function git:init() {
    git init
    # To set up the git hook scripts run
    pre-commit install
}

function git:install_pre_commit() {
    # To set up the git hook scripts run
    pre-commit install
}

function clean:build() {
    rm -fr build/
    rm -fr dist/
    rm -fr .eggs/
    find . -name '*.egg-info' -exec rm -fr {} +
    find . -name '*.egg' -exec rm -f {} +
}

function clean:pyc() {
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +
    find . -name '__pycache__' -exec rm -fr {} +
}

function clean:test() {
    rm -fr .tox/
    rm -f .coverage
    rm -fr htmlcov/
    rm -fr .pytest_cache
}

function format:isort() {
    # TODO change this to take a variable
    # add a function to format the whoel project
    printf "Running isort on %s\n" "${@}"
    python3 -m isort "${@}"
    # python3 -m isort "./tests"
}

function format:black() {
    printf "Running black on %s\n" "${@}"
    python3 -m black "${@}"
    # python3 -m black "./tests"
}

function format() {
    format:isort "${CODE_PATHS[@]}"
    format:black "${CODE_PATHS[@]}"
}

function coverage() {
    python3 -m coverage run --source "${SRC_PATH}""${PACKAGE}" -m pytest
    python3 -m coverage report -m
    python3 -m coverage html
    "${BROWSER}" htmlcov/index.html
}

function lint:mypy() {
    set +e
    printf "Running mypy on %s\n" "${@}"
    python3 -m mypy "${@}"
}

function lint:pylint() {
    set +e
    printf "Running pylint on %s\n" "${@}"
    python3 -m pylint "${@}"
}
function lint() {
    lint:mypy "${CODE_PATHS[@]}"
    lint:pylint "${CODE_PATHS[@]}"

}

function help() {
    printf "%s <task> [args]\n\nTasks:\n" "${0}"

    compgen -A function | grep -v "^_" | cat -n

    printf "\nExtended help:\n  Each task has comments for general usage\n"
}

# This idea is heavily inspired by: https://github.com/adriancooney/Taskfile
TIMEFORMAT=$'\nTask completed in %3lR'
time "${@:-help}"
