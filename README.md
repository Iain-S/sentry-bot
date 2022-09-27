# sentry-bot

![license](./assets/license-MIT-green.svg)
![platform](./assets/platform-Linux_or_macOS-lightgrey.svg)
![python](./assets/python-3_10-blue.svg)

An autonomous Nerf turret

## User Setup

### Installation

1. Install the sentry-bot package
1. _optional_ Make a `config.toml` file, with these contents, in the directory you will run the app from

   ```toml
   VIDEO_PATH='/path/to/any/video.mp4'
   ```

1. _optional_ Build webGL project with Unity and copy the `Build/`, `StreamingAssets/` and `TemplateData/` directories to `sentrybot/static/`.
   This game can be accessed via the `/game` URL.
1. Proceed to [Run the Server](#run-the-server)

## Developer Setup

### Obtain the Code

1. Clone the repository with something like `git clone path/to/sentry-bot-repo`
1. Change directory with `cd sentry-bot/`
   (subsequent instructions assume you are in the repo root directory)

#### Layout

- [assets/](./assets) contains images, etc. for the README
- [frontend/](./frontend) contains the frontend code and tests, which are written in TypeScript
- [sentrybot/](./sentrybot) contains the backend code, which is a Python Flask webserver
- [stubs/](./stubs) contains type stubs for Mypy
- [tests/](./tests) contains the backend tests

### Pre-requisites

#### Python & Poetry

1. Install Python >= 3.10
1. [Install Poetry](https://python-poetry.org/docs/#installation)
1. Install the `sentrybot` package with `poetry install`
1. Active our new virtual environment with `poetry shell`
   (subsequent instructions assume this is still active)

#### Node

1. Install Node and npm
1. Install our frontend dependencies with `npm --prefix ./frontend install ./frontend`

#### Pre-commit

1. [Install pre-commit](https://pre-commit.com/index.html#install)
1. Install pre-commit hooks with `pre-commit install`

The formatters and linters specified in [.pre-commit-config.yaml](.pre-commit-config.yaml) will run whenever you `git commit`.

#### Checks

1. Check that pre-commit hooks pass when you run `pre-commit run --all-files`
1. Check that Python pytest tests pass when you run `./test_backend.sh`
1. Check that TypeScript Jest tests pass when you run `./test_frontend.sh`

#### Frontend

1. Check that you can build the frontend with `./build_frontend.sh`
   (you can build whenever a .ts file changes by adding a `--watch` argument)

## Run the Server

1. Run the webserver with `flask --app sentrybot --debug run`
1. Go to `localhost:5000/` in your web browser
