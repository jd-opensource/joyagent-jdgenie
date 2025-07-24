#!/bin/bash

# 需安装 jdk17
# export JAVA_HOME="<you jdk path>"

# 需安装 maven3
echo '<settings>
        <mirrors>
          <mirror>
            <id>aliyun</id>
            <url>https://maven.aliyun.com/repository/public</url>
            <mirrorOf>*</mirrorOf> <!-- 匹配所有仓库 -->
          </mirror>
        </mirrors>
      </settings>' > aliyun-settings.xml
mvn clean package -DskipTests -s aliyun-settings.xml
