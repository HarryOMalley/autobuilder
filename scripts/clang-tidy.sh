#!/usr/bin/env bash

set -euo pipefail

: ' Run clang-tidy on all source and header files under src/ directory

Confidentiality and Proprietary Notice:
This document and/or code contains confidential and proprietary information of
Jaguar Land Rover Limited.
Copyright 2021 (c) Jaguar Land Rover Limited. All rights reserved
'

PROJECT_DIR=$(cd "$(dirname "$0")/../../.."; pwd)
cd "${PROJECT_DIR}/build"
"${PROJECT_DIR}/scripts/build.sh" \
  -DCMAKE_CXX_CLANG_TIDY=clang-tidy \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON
exit 0