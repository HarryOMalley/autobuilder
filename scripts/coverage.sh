#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR=$(cd "$(dirname "$0")/../../.."; pwd)

cd "${PROJECT_DIR}/build"

NUM_CPUS=${NUM_CPUS:-$(nproc)}
BUILD_DIR=$(pwd)
LCOV_TRACEFILE=report.info
LCOV_OUTPUT_DIRECTORY="coverage-report"
LCOV_CONFIG_FILE="${PROJECT_DIR}/scripts/lcovrc"


# Collate coverage data.
lcov \
    --base-directory "${PROJECT_DIR}" \
    --config-file "${LCOV_CONFIG_FILE}" \
    --capture \
    --gcov-tool gcov \
    --directory . \
    --no-external \
    --output-file "${LCOV_TRACEFILE}"

# Exclude coverage data from dependencies.
lcov \
    --config-file "${LCOV_CONFIG_FILE}" \
    --remove "${LCOV_TRACEFILE}" \
        "${PROJECT_DIR}/test/unit/*" \
        "${PROJECT_DIR}/test/functional-test/*" \
        "${BUILD_DIR}/*" \
    --output-file "${LCOV_TRACEFILE}"

# Generate HTML report
mkdir "${LCOV_OUTPUT_DIRECTORY}" -p
genhtml \
    --config-file "${LCOV_CONFIG_FILE}" \
    --branch-coverage \
    --output-directory "${LCOV_OUTPUT_DIRECTORY}" \
    "${LCOV_TRACEFILE}" | tee coverage-report.log

tar -czf coverage-report.tgz "${LCOV_OUTPUT_DIRECTORY}"
