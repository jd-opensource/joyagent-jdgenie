# 部署的详细方法

## 🚀 Docker Compose 一键部署 (推荐)

> 🎉 **新增功能**：使用 Docker Compose 一键部署！更简单、更可靠、更易维护。

### 环境要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **系统内存**: 4GB+ (推荐 8GB+)
- **可用存储**: 10GB+

### 快速部署步骤

**1️⃣ 克隆项目**
```bash
git clone https://github.com/jd-opensource/joyagent-jdgenie.git
cd joyagent-jdgenie
```

**2️⃣ 修改 .env 文件**
```bash
# 复制环境变量模板
cd docker
cp .env.example .env

# 编辑配置文件
vim .env
```

**3️⃣ 一键启动**
```bash
docker compose up -d
```

**4️⃣ 访问服务**
- 🌐 **前端页面**: http://your-ip:3000
- 🔧 **后端API**: http://your-ip:8080
- 🐍 **Python客户端**: http://your-ip:8188  
- 🛠️ **工具服务**: http://your-ip:1601

### 管理命令
```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 更新部署 (重新构建镜像)
docker compose up -d --build
```

### 配置说明
- 所有服务配置通过环境变量管理，无需手动修改配置文件
- 数据持久化存储在Docker volumes中
- 支持健康检查和自动重启
- 网络自动配置，服务间通信无需额外配置

> 💡 **提示**: Docker Compose部署方式具有更好的隔离性、可移植性和维护性，推荐用于生产环境。

---

## 📋 手动部署详细步骤

> ⚠️ **注意**: 以下为传统手动部署方式，适用于开发调试或特殊需求场景。

### 前期准备， 如果java,python,pnpm都满足，直接 FLY Step 1

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


## Step 4: 启动mcp 服务

另外打开一个终端
cd joyagent-jdgenie/genie-client
uv venv
source .venv/bin/activate
sh start.sh 即可








