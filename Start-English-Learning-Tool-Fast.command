#!/bin/bash

cd "$(dirname "$0")" || exit 1
export STARTUP_CATCHUP_ENABLED=false
./start.sh
