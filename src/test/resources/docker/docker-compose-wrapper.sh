#!/usr/bin/env bash

set -euo pipefail

export SHELLOPTS
declare SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

export XLR_PLUGIN_JAR=$( find "$SCRIPT_DIR/../../../../build/libs/" -name '*.jar' -printf '%f' -quit )

docker-compose --project-name xlr-rundeck-plugin --file "$SCRIPT_DIR/docker-compose.yml" rm --force
docker-compose --project-name xlr-rundeck-plugin --file "$SCRIPT_DIR/docker-compose.yml" up
