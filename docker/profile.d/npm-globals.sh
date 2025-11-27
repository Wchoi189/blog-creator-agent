#!/bin/sh

# Ensure npm installs globals inside the mounted /workspaces volume so they persist
export NPM_CONFIG_PREFIX=/workspaces/.npm-global

# Prepend the persisted npm global bin directory to PATH if it exists and is not already included
if [ -d /workspaces/.npm-global/bin ]; then
    case ":$PATH:" in
        *:/workspaces/.npm-global/bin:*) ;;
        *) export PATH="/workspaces/.npm-global/bin:$PATH" ;;
    esac
fi

