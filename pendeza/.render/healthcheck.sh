#!/usr/bin/env bash
curl -f http://localhost:${PORT:-10000}/health/ || exit 1