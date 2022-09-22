#!/usr/bin/env bash

# Exit on error
set -e

cd frontend || exit 1

npm test
