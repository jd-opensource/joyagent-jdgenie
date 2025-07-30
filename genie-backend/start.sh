#!/bin/bash

BASEDIR="./genie-backend"
CLASSPATH="$BASEDIR/conf/:$BASEDIR/lib/*"
MAIN_MODULE="com.jd.genie.GenieApplication"
LOGFILE="./genie-backend_startup.log"

echo "starting $APP_NAME :)"
exec java -classpath "$CLASSPATH" -Dbasedir="$BASEDIR" -Dfile.encoding="UTF-8" ${MAIN_MODULE} 2>&1 | tee "$LOGFILE"

