#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "$0")/../../.."; pwd)

# remove the build directory
rm -rf "${PROJECT_DIR}/build"

# recreate the build directory
mkdir "${PROJECT_DIR}/build"