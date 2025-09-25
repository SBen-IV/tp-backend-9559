#!/bin/bash

set -e

MESSAGE=$1

if [[ -z "${MESSAGE}" ]]; then
    echo "Usage: ./add-revision.sh <message>"
    exit 1
fi

alembic revision --autogenerate -m "${MESSAGE}"
