#!/usr/bin/env bash
# 统一构建入口：按 DESIGN.md 生成全站（见 scripts/build.py）
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 scripts/build.py
