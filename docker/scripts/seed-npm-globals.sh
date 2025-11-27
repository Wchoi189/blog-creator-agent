#!/bin/bash
set -euo pipefail

SEED_DIR=/opt/npm-global
TARGET_DIR=/workspaces/.npm-global

# Ensure target directory exists with correct permissions
mkdir -p "${TARGET_DIR}"

# If globals already exist on the mounted volume, respect them
if [ -n "$(ls -A "${TARGET_DIR}" 2>/dev/null)" ]; then
    exit 0
fi

# Otherwise copy the preinstalled toolchain into the mounted directory
if [ -d "${SEED_DIR}" ]; then
    cp -a "${SEED_DIR}"/. "${TARGET_DIR}"/
fi

