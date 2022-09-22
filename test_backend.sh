#!/usr/bin/env bash

# Exit on error
set -e

pytest --cov=sentrybot tests/
