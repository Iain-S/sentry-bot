#!/usr/bin/env bash
# Transpile our TypeScript frontend code to JavaScript

# Exit on error
set -e

cd frontend || exit 1

if [ "$1" = "--watch" ]; then

  # Continuously compile TypeScript files into JavaScript
  npx tsc-watch \
    --strict \
    --project tsconfig.build.json \
    --outDir ../sentrybot/static/js \
    --onSuccess './append_js.sh' \
    --onFailure 'echo "Compilation failed!"'\

else

  # Compile TypeScript files into JavaScript
  npx tsc --strict --project tsconfig.build.json --outDir ../sentrybot/static/js

  ./append_js.sh

fi
