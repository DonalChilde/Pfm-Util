#!/usr/bin/env bash

# Master copy located at ?
# Version 1.0
# 2021-03-15T16:27:09Z
# Note: this script expects to be run from the top directory of a project.

# Ideas shamelessly lifted from:
# https://github.com/nickjj/docker-flask-example/blob/main/run
# https://github.com/audreyfeldroy/cookiecutter-pypackage/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/Makefile

# -e Exit immediately if a pipeline returns a non-zero status.
# -u Treat unset variables and parameters other than the special parameters ‘@’ or ‘*’ as an error when performing parameter expansion.
# -o pipefail If set, the return value of a pipeline is the value of the last (rightmost) command to exit with a non-zero status, or zero if all commands in the pipeline exit successfully.
set -euo pipefail

# TODO make completions for script.
# https://iridakos.com/programming/2018/03/01/bash-programmable-completion-tutorial
# TODO add check to make sure that we are piping to the correct virtual env?

PACKAGE="${PACKAGE:-click_hash}"
# SRC_PATH="src/"
BROWSER="google-chrome"
CODE_PATHS=("./src" "./tests")
PYTHON_VENV_VERSION="${PYTHON_VENV_VERSION:-3.10}"
# https://stackoverflow.com/questions/4774054/reliable-way-for-a-bash-script-to-get-the-full-path-to-itself
SCRIPT_PATH=$(realpath $0)

function clean() { ## Clean build,python, and test artifacts.
    clean:build
    clean:pyc
    clean:test
}

function clean:build() { ## Clean build artifacts.
    rm -fr build/
    rm -fr dist/
    rm -fr .eggs/
    find . -name '*.egg-info' -exec rm -fr {} +
    find . -name '*.egg' -exec rm -f {} +
}

function clean:pyc() { ## Clean python aritfacts.
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +
    find . -name '__pycache__' -exec rm -fr {} +
}

function clean:test() { ## Clean test artifacts.
    rm -fr .tox/
    rm -f .coverage
    rm -fr htmlcov/
    rm -fr .pytest_cache
    rm -fr .mypy_cache
}

function _countdown() {
    # https://superuser.com/questions/611538/is-there-a-way-to-display-a-countdown-or-stopwatch-timer-in-a-terminal
    # countdown 5 to count down from 5 seconds
    date1=$((`date +%s` + $1));
    while [ "$date1" -ge `date +%s` ]; do
        echo -ne "$(date -u --date @$(($date1 - `date +%s`)) +%H:%M:%S)\r";
        sleep 0.1
    done
}

function dist:build() { ## builds source and wheel package.
    clean:build
    python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist
}

function dist:release() { ## Upload a release to PyPi.
    echo "Preparing to upload to PyPi."
    echo "Did you:"
    echo "\t- Check for the correct branch?"
    echo "\t- Update the version number?"
    echo "\t- Update the documentation?"
    echo "\t- Run ALL THE TESTS?"
    echo "\t- Update the changelog?"
    echo "\t- Build a fresh dist/?"
    echo
    echo "Take ten seconds to be sure:"
    _countdown 10
    # https://stackoverflow.com/a/1885534/105844
    read -p "Are you sure? (Y/N)" -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        twine check dist/*
        source ./.twine-secrets.env
        twine upload dist/*
    fi
}

function dist:test:release() { ## Upload a release to TestPyPi.
    echo "Preparing to upload to TestPyPi"
    echo "Did you:"
    echo "\t- Check for the correct branch?"
    echo "\t- Update the version number?"
    echo "\t- Update the documentation?"
    echo "\t- Run ALL THE TESTS?"
    echo "\t- Update the changelog?"
    echo "\t- Build a fresh dist/?"
    echo
    echo "Take ten seconds to be sure:"
    _countdown 10
    # https://stackoverflow.com/a/1885534/105844
    read -p "Are you sure? (Y/N)" -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        source ./.twine-test-secrets.env
        twine check dist/*
        twine upload --repository testpypi dist/*
    fi
}

function docs:build() { ## Build documentation.
    # sphinx-apidoc makes an ugly format, see the Rich docs for a better manual example.
    # rm -f docs/$PACKAGE.rst
	# rm -f docs/modules.rst
	# sphinx-apidoc -o ./docs/ ./src/$PACKAGE
    sphinx-build -b html ./docs ./docs/_build
}

function docs:serve() { ## Open docs in a web browser
    echo "Not implemented yet"
}

function format:isort() { ## Takes Arguments. Run isort.
    printf "Running isort on %s\n" "${@}"
    python3 -m isort "${@}"
}

function format:black() { ## Takes Arguments. Run isort.
    printf "Running black on %s\n" "${@}"
    python3 -m black "${@}"
}

function format:isort:diff() { ## Takes Arguments. Run isort --diff.
    printf "Running isort --diff on %s\n" "${@}"
    python3 -m isort "${@}" --diff
}

function format:black:diff() { ## Takes Arguments. Run isort --diff.
    printf "Running black --diff on %s\n" "${@}"
    python3 -m black "${@}" --diff
}

function format() { ## isort and black on project.
    format:isort "${CODE_PATHS[@]}"
    format:black "${CODE_PATHS[@]}"
}

function format:diff() { ## isort --diff and black --diff on project.
    format:isort:diff "${CODE_PATHS[@]}"
    format:black:diff "${CODE_PATHS[@]}"
}

function git:init() { ## Set up local git repo, and install git pre-commit hooks.
    git init
    git:pre-commit
}

function git:pre-commit() { ## Set up the git hook scripts.
    pre-commit install
}

function help() { ## Get script help.
    printf "\nInstructions for the script located at:\n$SCRIPT_PATH\n"
    _help
}

function lint() { ## Run mypy and pylint on project.
    lint:mypy "${CODE_PATHS[@]}"
    lint:pylint "${CODE_PATHS[@]}"
}

function lint:mypy() { ## Takes Arguments. Run mypy.
    set +e
    printf "Running mypy on %s\n" "${@}"
    python3 -m mypy "${@}"
}

function lint:pylint() { ## Takes Arguments. Run pylint.
    set +e
    printf "Running pylint on %s\n" "${@}"
    python3 -m pylint "${@}"
}

function pip3:install() { ## Takes arguments. Install requested packages.
    _pip3 install "${@}"
}

function pip3:install:editable() { ## Install project as editable in venv.
    # shellcheck disable=SC1091
    _pip3 install --editable .
}

function pip3:install:project() { ## Install project in venv.
    # shellcheck disable=SC1091
    _pip3 install .
}

function pip3:install:req() { ## Install from both requirements files
    _pip3 install -r ./requirements_dev.txt
    _pip3 install -r ./requirements.txt
}

function pip3:outdated() { ## List any installed packages that are outdated.
    _pip3 list --outdated
}

function pip3:uninstall() { ## Takes arguments. Remove requested packages.
    _pip3 uninstall "${@}"
}

function pip3:upgrade() { ## Takes arguments. Upgrade requested packages.
    _pip3 install "${@}" --upgrade
}

function pip3:upgrade:all() { ## Upgrade only packages found in either requirements file.
    _pip3 install $(cat ./requirements.txt | sed /^\#/d | tr '\n' ' ') --upgrade
    _pip3 install $(cat ./requirements_dev.txt | sed /^\#/d | tr '\n' ' ') --upgrade
    # _pip3 install "$(pip list --outdated | tail +3 | grep -v sdist | awk '{ print $1 }')" --upgrade
}

function pip3:upgrade:pip() { ## Upgrade pip, wheel, setuptools.
    PIP_REQUIRE_VIRTUALENV=true pip3 install -U pip setuptools wheel
}

function _pytest() {
    python3 -m pytest "${@}"
}

function pytest() { ## Takes Arguments. Run test suite with pytest.
    _pytest tests/ "${@}"
}

function pytest:cov() { ## Takes arguments. Get test coverage with pytest-cov.
    _pytest tests/ --cov src/ --cov-report term-missing "${@}"
}

function tox() { ## Run tox.
    tox
}

function venv:init() { ## makes a venv in the project directory.
    python${PYTHON_VENV_VERSION} -m venv ./.venv
}

function venv:init:all() { ## Initialize a venv, upgrade pip, wheel, and setuptools, and install both requirements files.
    venv:init
    source ./.venv/bin/activate
    pip3:upgrade:pip
    pip3:install:req
}

function venv:remove() { ## Delete the project venv.
    printf "\nDeleting ./.venv deactivate any terminal windows that were using that venv.\n"
    deactivate || true
    rm -r ./.venv/ || true
}

function venv:reset() { ## Remove and reinstall a venv including both requirements files.
    venv:remove
    venv:init:all
}

function _help() {
    python3 - << EOF
from pathlib import Path
from operator import itemgetter
import re
script_path = Path("$SCRIPT_PATH")
with open(script_path) as file:
    functions = []
    for line in file:
        match = re.match(r'^function\s*([a-zA-Z0-9\:-]*)\(\)\s*{\s*##\s*(.*)', line)
        if match is not None:
            functions.append(match.groups())
    for target, help in sorted(functions):
        print("  {0:20}    {1}".format(target,help))
EOF
}

function _pip3() { ## Private function used as the base for most pip calls.
    printf "\nUsing virtual env located at:\n%s\n" "$VIRTUAL_ENV"
    PIP_REQUIRE_VIRTUALENV=true pip3 "${@}"
}

function _help:old(){
    printf "%s <task> [args]\n\nTasks:\n" "${0}"

    compgen -A function | grep -v "^_" | cat -n

    printf "\nExtended help:\n  Each task has comments for general usage\n"
}

# This idea is heavily inspired by: https://github.com/adriancooney/Taskfile
# Runs the help function if no arguments given to script.
TIMEFORMAT=$'\nTask completed in %3lR'
time "${@:-help}"
