#!/usr/bin/env bash
set -Eeuo pipefail

function build() {
    python3 -m nuitka --standalone --follow-imports --output-dir=build --show-progress --show-memory --lto=yes --include-package=websockets src/uptt_backend.py
    python3 -m nuitka --standalone --follow-imports --output-dir=build --show-progress --show-memory --lto=yes --include-module=uptt_mq_server src/uptt_mq_server.py

    # cp all files to the build directory: backend/build-packages
    mkdir -p build-packages
    cp -r build/uptt_backend.dist/* build-packages
    cp -r build/uptt_mq_server.dist/* build-packages
}

function script_usage() {
    cat << EOF

Usage: $0 <build>
EOF
}

function main() {
    if (( $# < 1 )); then
        script_usage
        exit 0
    fi

    action="${1}"

    local action="${1}"

    case "$action" in
      build)
          build
          ;;
      *)
          echo "Unknown action"
          echo
          script_usage
          exit 1
          ;;
    esac
}

main "$@"
