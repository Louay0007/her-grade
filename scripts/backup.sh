#!/bin/bash
set -e
mkdir -p backups
sqlite3 data/hergrade.sqlite3 ".dump" > backups/hergrade-$(date +%F).sql
cp -r data/batches backups/batches-$(date +%F) 2>/dev/null || true
echo "backup done"
