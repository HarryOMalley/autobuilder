#!/usr/bin/env bash

set -euo pipefail

: ' Run clang-format on all source and header files under src/ directory

Confidentiality and Proprietary Notice:
This document and/or code contains confidential and proprietary information of
Jaguar Land Rover Limited.
Copyright 2021 (c) Jaguar Land Rover Limited. All rights reserved
'

PROJECT_DIR=$(cd "$(dirname "$0")/../../.."; pwd)

find "$PROJECT_DIR"/src "$PROJECT_DIR"/test \
  -type f \( -name '*.c' -o -name '*.h' -o -name '*.cpp' -o -name '*.hpp' \) \
    -print0 | xargs -L 1 -0 "$PROJECT_DIR"/scripts/format-cpp-file.sh
