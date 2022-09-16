#!/usr/bin/env bash
# Must be run from the 'frontend' directory

# Exit on error
set -e

# Replace
# import { sum } from "./sum";
# with
# import { sum } from "./sum.js";
sed -E -i '' 's/(from \".\/[a-z]+)(\";)/\1.js\2/g' ../sentrybot/static/js/*.js
