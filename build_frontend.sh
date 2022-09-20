#!/usr/bin/env bash

# Exit on error
set -e

cd frontend || exit

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
  tsc --strict --project tsconfig.build.json --outDir ../sentrybot/static/js

  ./append_js.sh

fi
