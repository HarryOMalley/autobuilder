#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "$0")/../../.."; pwd)
mkdir -p "${PROJECT_DIR}/build"
cd "${PROJECT_DIR}/build"


"${PROJECT_DIR}/scripts/build.sh" $@ \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON