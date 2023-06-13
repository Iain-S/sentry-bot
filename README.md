# sentry-bot

![license](./assets/license-MIT-green.svg)
![platform](./assets/platform-Linux_or_macOS-lightgrey.svg)
![python](./assets/python-3_10-blue.svg)
![pre-commit](./assets/pre--commit-enabled-brightgreen.svg)

An autonomous Nerf turret

## Optional Extras

This package has two optional extras.
You must install at least one for camera-related features to work.

- `[picamera]` can only be installed on Raspberry Pi hardware
- `[opencv]` is used for object recognition.
  It can be installed on Pi and non-Pi hardware but is extremely slow to compile on a Pi.

## Deployment

To install on a Raspberry Pi, log in and then:

1. Install the project with

   ```shell
   pip install "git+https://github.com/Iain-S/sentry-bot#egg=sentrybot[picamera]"`
   ```

   **Note** that we are installing the `[picamera]` extra and that the `"` quotes are required if using `zsh`.

1. _optional_ Manually compile and install OpenCV by following, for example, [these](https://pimylifeup.com/raspberry-pi-opencv/) instructions
1. Proceed to [Run the Server](#run-the-server)

## User Setup

You can install this package on non-Pi hardware using `pip`.
Some features of this package will be unavailable on non-Pi hardware but the web server will still run.

If your computer has a camera, you can install the `[opencv]` extra.
You should not try to install the `[picamera]` extra on non-Pi hardware as installation will fail.

1. Install the project with

   ```shell
   pip install "git+https://github.com/Iain-S/sentry-bot#egg=sentrybot[opencv]"`
   ```

   **Note** that we are installing the `[opencv]` extra and that the `"` quotes are required if using `zsh`.

1. Proceed to [Run the Server](#run-the-server)

## Developer Setup

### Obtain the Code

1. Clone the repository with something like `git clone path/to/sentry-bot-repo`
1. Change directory with `cd sentry-bot/`
   (subsequent instructions assume you are in the repo root directory)

#### Layout

- [assets/](./assets) contains images, etc. for the README
- [frontend/](./frontend) contains the frontend code and tests, which are written in TypeScript
- [sentrybot/](./sentrybot) contains the backend code, which is a Python webserver
- [stubs/](./stubs) contains type stubs for Mypy
- [tests/](./tests) contains the backend tests

### Pre-requisites

#### Python & Poetry

1. Install Python >= 3.10
1. [Install Poetry](https://python-poetry.org/docs/#installation)
1. Install the `sentrybot` package and `[opencv]` extra with `poetry install -E opencv`
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

### On a Raspberry Pi

1. Start the pigpio daemon with `sudo pigpiod`
1. Set the `CONTROL_TURRET` environment variable to `1`
1. Set the `CAMERA_LIBRARY` environment variable to either `"picamera"` or `"opencv"`
1. Run the webserver with `python -m sentrybot.http_server` but be aware that **it will make the webserver accessible to all machines on the network**
1. Go to `ip.of.the.pi:8000/` in your web browser, replacing `ip.of.the.pi` with your Pi's IP address

### On Other Hardware

1. Set the `CONTROL_TURRET` environment variable to `0`
1. Set the `CAMERA_LIBRARY` environment variable to either `"picamera"` or `"opencv"`
1. Run the webserver with `python -m sentrybot.http_server` but be aware that **it will make the webserver accessible to all machines on the network**
1. Go to `localhost:8000/` in your web browser
