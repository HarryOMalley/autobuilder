#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "$0")/../../.."; pwd)

cd "${PROJECT_DIR}/build"

NUM_CPUS=${NUM_CPUS:-$(nproc)}

ctest \
  --output-on-failure \
  --parallel "${NUM_CPUS}" $@