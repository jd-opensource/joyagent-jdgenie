# 部署的详细方法

## 前期准备， 如果java,python,pnpm都满足，直接 FLY Step 1

java > 17

mac用户安装
*. brew install maven

直接安装会同时安装openjava sdk， JAVA_HOME：/opt/homebrew/Cellar/openjdk/24.0.1/libexec/openjdk.jdk/Contents/Home, 如果没有需要手动安装java.

**.下载 https://www.oracle.com/java/technologies/downloads/，版本大于17
手动安装：/usr/libexec/java_home -V
/Library/Java/JavaVirtualMachines/jdk-17.jdk/Contents/Home

然后通过，写入zshrc

```
echo 'export JAVA_HOME=$(/usr/libexec/java_home)' >> ~/.zshrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

pnpm > 7
如何安装pnpm，https://pnpm.io/zh/installation
ps：资源包的安装如果速度比较慢建议使用国内镜像


python

---
## Step 1: 启动前端服务

打开一个终端

cd joyagent-jdgenie/ui && sh start.sh 

如果报错参见上面信息前期准备看看有没有pnpm

出现 Local:   http://localhost:3000/ 即成功！

---
## Step 2: 启动后端服务

另外打开一个终端

cd joyagent-jdgenie/genie-backend && sh build.sh

出现[INFO] BUILD SUCCESS即可
如有报错安装java>17,步骤见上

sh start.sh

启动后，可以通过命令tail -f genie-backend_startup.log观察日志情况。

ps 1: 可以动态适合自己key,编辑 joyagent-jdgenie/genie-backend/src/main/resources/application.yml,其中配置是可以添加多个模型，然后在不同模块下可以指定，比如在react模式下，我指定了claude-3-7-sonnet-v1，建议修改为适合自己的模型名字。
settings: '{"claude-3-7-sonnet-v1": {
        "model": "claude-3-7-sonnet-v1",
        "max_tokens": 8192,
        "temperature": 0,
        "base_url": "<input llm server here>",
        "apikey": "<input llm key here>",
        "max_input_tokens": 128000
}}'

ps 2:修改完配置后，重新build.sh,然后start.sh

---


## Step 3: 启动 tools 服务

另外打开一个终端

```
cd joyagent-jdgenie/genie-tool
pip install uv
cd genie-tool
uv sync
source .venv/bin/activate
```
首次启动需要执行
python -m genie_tool.db.db_engine
之后则无需执行。

然后
cp .env_template .env
编辑.env文件, 其中需要配置SERPER_SEARCH_API_KEY，申请网址https://serper.dev/
最后通过
uv run python server.py 启动服务即可

对于多模态子模块，需要配置`.env`中MRAG中相关的配置。

- 3.1 建议从`https://dashscope.aliyuncs.com`申请key并替换文件中的key。

- 3.2 本地启动qdrant, https://qdrant.tech/documentation/quickstart/ 或申请官方资源。

- 3.3 初始化数据 

需要将数据放到

```
genie-tool/genie_tool/tool/mrag/mrag_data
```

然后提交初始化数据的任务

```
uv run python -m genie_tool/tool/mrag/init/init_db
```

**注意：数据初始化过程中tool的server服务不能停止。**

## Step 4: 启动mcp 服务

另外打开一个终端
cd joyagent-jdgenie/genie-client
uv venv
source .venv/bin/activate
sh start.sh 即可








