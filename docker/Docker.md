





# Docker部署Genie 指南(DeepSeek)

# 构建镜像

## 前端镜像

```bash
$ vim docker/Dockerfile_frontend
FROM docker.m.daocloud.io/library/node:20-alpine as frontend-builder
WORKDIR /app
RUN npm install -g pnpm --registry=https://registry.npmmirror.com && \
    pnpm config set registry https://registry.npmmirror.com
COPY ui /app/ui
RUN cd ui && \
    pnpm install && \
    pnpm build
RUN { \
    echo '#!/bin/sh'; \
    echo 'set -e'; \
    echo 'if [ -f /usr/share/nginx/html/config.js ]; then'; \
    echo '    echo "Replacing SERVER_BASE_URL with: $SERVER_BASE_URL"'; \
    echo '    envsubst '"'"'${SERVER_BASE_URL}'"'"' < /usr/share/nginx/html/config.js > /tmp/config.js'; \
    echo '    mv /tmp/config.js /usr/share/nginx/html/config.js'; \
    echo 'fi'; \
    echo 'exec nginx -g "daemon off;"'; \
} > /docker-entrypoint.sh

FROM nginx
COPY --from=frontend-builder /app/ui/dist/ /usr/share/nginx/html/
COPY --from=frontend-builder /docker-entrypoint.sh /docker-entrypoint.sh
ENV SERVER_BASE_URL=http://127.0.0.1:8080
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]

$ docker build -t genie-frontend -f ./docker/Dockerfile_frontend .
```



## 后端镜像

```bash
# 后端
$ vim docker/Dockerfile_backend
FROM docker.m.daocloud.io/library/maven:3.8-openjdk-17 as backend-builder
WORKDIR /app
COPY genie-backend ./

RUN echo '<settings>\
  <mirrors>\
    <mirror>\
      <id>aliyun</id>\
      <url>https://maven.aliyun.com/repository/public</url>\
      <mirrorOf>*</mirrorOf>\
    </mirror>\
  </mirrors>\
</settings>' > aliyun-settings.xml && \
    mvn clean package -DskipTests -s aliyun-settings.xml

FROM docker.m.daocloud.io/library/maven:3.8-openjdk-17
WORKDIR /app
COPY --from=backend-builder /app/start.sh ./
COPY --from=backend-builder /app/target/genie-backend ./
CMD ["sh", "start.sh"]

$ docker build -t genie-backend -f ./docker/Dockerfile_backend .
```

## python client 镜像

```bash
# python - genie-client
$ vim docker/Dockerfile_client
FROM docker.m.daocloud.io/library/python:3.11-slim
WORKDIR /app
RUN sed -i 's/deb.debian.org/mirrors.huaweicloud.com/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    netcat-openbsd \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/* 
RUN pip install uv -i https://mirrors.aliyun.com/pypi/simple/
COPY genie-client ./
RUN uv venv .venv && \
    . .venv/bin/activate && \
    uv pip install -r pyproject.toml -i https://mirrors.aliyun.com/pypi/simple/
CMD ["uv", "run", "server.py"]

$ docker build -t genie-client -f ./docker/Dockerfile_client .
```

## python tool 镜像

```bash
# python - genie-tool
$ vim docker/Dockerfile_tool
FROM docker.m.daocloud.io/library/python:3.11-slim
WORKDIR /app
RUN sed -i 's/deb.debian.org/mirrors.huaweicloud.com/g' /etc/apt/sources.list.d/debian.sources
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    netcat-openbsd \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/* 
RUN pip install uv -i https://mirrors.aliyun.com/pypi/simple/
COPY genie-tool ./
RUN uv venv .venv && \
    . .venv/bin/activate && \
    chmod +x start.sh && \
    uv pip install . -i https://mirrors.aliyun.com/pypi/simple/ && \
    mkdir -p /data/genie-tool && \
    cp .env_template .env && \
    python -m genie_tool.db.db_engine
VOLUME ["/data/genie-tool"]
CMD ["./start.sh"]

docker build -t genie-tool -f ./docker/Dockerfile_tool .

```

# 启动服务

## 前端

```bash
$ docker run -it -d \
  --name genie-frontend \
  -e SERVER_BASE_URL=http://xxx.xxx.xxx.xxx:8080 \
  -p 3345:80 \
  -p 3346:443 \
  genie-frontend
```

参数说明:

- `SERVER_BASE_URL`: 后端服务地址, 将`xxx.xxx.xxx.xxx` 替换为真正IP即可。



## 后端

```bash
$ docker run -it -d \
  --name genie-backend \
  -p 8080:8080 \
  -e LLM_BASE_URL=https://api.deepseek.com/v1 \
  -e LLM_APIKEY=sk-xxx \
  -e LLM_INTERFACE_URL=/chat/completions \
  -e LLM_MODEL=deepseek-chat \
  -e SETTINGS_LLM_NAME=deepseek-chat \
  -e SETTINGS_LLM_MODEL=deepseek-chat \
  -e SETTINGS_LLM_BASE_URL=https://api.deepseek.com/v1 \
  -e SETTINGS_LLM_APIKEY=sk-xxx \
  -e SETTINGS_LLM_INTERFACE_URL=/chat/completions \
  -e PLANNER_MODEL=deepseek-chat \
  -e EXECUTOR_MODEL=deepseek-chat \
  -e REACT_MODEL=deepseek-chat \
  -e REACT_MODEL=deepseek-chat \
  -e SUMMARY_MODEL=deepseek-chat \
  -e GENIE_TOOL_URL=http://xxx.xxx.xxx.xxx:1601 \
  -e GENIE_MCP_CLIENT_URL=http://xxx.xxx.xxx.xxx:8188 \
  -e GENIE_MCP_SERVER_URL=https://mcp.api-inference.modelscope.net/1784ac5c6d0044/sse \
  genie-backend
```

参数说明:

- `LLM_BASE_URL`: 大模型地址, 如 DeepSeek: `https://api.deepseek.com/v1`;
- `LLM_APIKEY`: ApiKey;
- `LLM_INTERFACE_URL`: 默认 `/chat/completions`;
- `LLM_MODEL`: 默认 `gpt-4.1`
- `SETTINGS_LLM_NAME`: LLM setting, 默认 `claude-3-7-sonnet-v1`;
- `SETTINGS_LLM_MODEL`: LLM model, 默认 `claude-3-7-sonnet-v1`;
- `SETTINGS_LLM_BASE_URL`: LLM url, 默认空, 但必填;
- `SETTINGS_LLM_APIKEY`: LLM apikey, 默认空;
- `SETTINGS_LLM_INTERFACE_URL`: 默认 `/chat/completions`;
- `PLANNER_MODEL`: 默认 `gpt-4.1`;
- `EXECUTOR_MODEL`: 默认 `gpt-4.1 `;
- `REACT_MODEL`: 默认 `claude-3-7-sonnet-v1`;
- `SUMMARY_MODEL`: 默认 `gpt-4.1`;
- `GENIE_TOOL_URL`: genie-tool 容器访问地址, 默认 `http://127.0.0.1:1601`;
- `GENIE_MCP_CLIENT_URL`: genie-client 默认访问地址, 默认 `http://127.0.0.1:8188`;
- `GENIE_MCP_SERVER_URL`: 默认 `https://mcp.api-inference.modelscope.net/1784ac5c6d0044/sse`

## python client 

```bash
$ docker run -it -d --name genie-client -p 8188:8188 genie-client
```

## python tool

```bash
docker run -it -d \
  --name genie-tool \
  -p 1601:1601 \
  -e OPENAI_API_KEY=sk-xxx \
  -e OPENAI_BASE_URL=https://api.deepseek.com/v1 \
  -e FILE_SAVE_PATH=file_db_dir \
  -e SQLITE_DB_PATH=autobots.db \
  -e FILE_SERVER_URL=http://xxx.xxx.xxx.xxx:1601/v1/file_tool \
  -e USE_SEARCH_ENGINE=serp \
  -e SEARCH_COUNT=10 \
  -e SEARCH_TIMEOUT=10 \
  -e SEARCH_THREAD_NUM=5 \
  -e DEFAULT_MODEL=openai/deepseek-chat \
  -e SERPER_SEARCH_URL=https://google.serper.dev/search \
  -e SERPER_SEARCH_API_KEY=xxx \
  genie-tool
```

# 检查镜像

```bash
$ docker ps | grep genie
2f42e3f4773d   genie-tool     "./start.sh"     25 minutes ago   Up 25 minutes     0.0.0.0:1601->1601/tcp, :::1601->1601/tcp   genie-tool
94230f5c1982   genie-client   "uv run server.py"  26 minutes ago   Up 26 minutes  0.0.0.0:8188->8188/tcp, :::8188->8188/tcp   genie-client
3bd31ead4e56   genie-backend  "/usr/local/bin/mvn-…"   27 minutes ago   Up 27 minutes  0.0.0.0:8080->8080/tcp, :::8080->8080/tcp  genie-backend
8f377ac4e9e0   5e1351af07ec   "/docker-entrypoint.…"   28 minutes ago   Up 28 minutes  0.0.0.0:3345->80/tcp, :::3345->80/tcp, 0.0.0.0:3346->443/tcp, :::3346->443/tcp     genie-frontend
```

# 访问

http://DOCKER_IP:3345

# 常见Issue

待补充
