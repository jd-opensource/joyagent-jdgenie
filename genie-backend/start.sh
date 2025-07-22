#!/bin/bash

# 开始启动后端程序
BASEDIR="./genie-backend"
CLASSPATH="$BASEDIR/conf/:$BASEDIR/lib/*"
MAIN_MODULE="com.jd.genie.GenieApplication"
LOGFILE="./genie-backend_startup.log"

sed -i "s#<input llm server here>#${OPENAI_BASE_URL}#g" "$BASEDIR/conf/application.yml"
sed -i "s/<input llm key here>/$OPENAI_API_KEY/g" $BASEDIR/conf/application.yml

echo "starting $APP_NAME :)"
java -classpath "$CLASSPATH" -Dbasedir="$BASEDIR" -Dfile.encoding="UTF-8" ${MAIN_MODULE} > $LOGFILE 2>&1 &
