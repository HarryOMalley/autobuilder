#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "$0")/../../.."; pwd)

cd "${PROJECT_DIR}/build"
ctest --show-only=json-v1