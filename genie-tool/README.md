# Genie Tool

`python >= 3.11`

## 项目结构

```
.
├── genie_tool
│   ├── api                             # api 服务
│   ├── model                           # 协议和 DataClass
│   ├── prompt                          # Prompt 仓库
│   ├── tool                            # 工具执行逻辑
│   └── util                            # 工具类
├── .env_template                       # 环境变量
├── server.py                           # FastAPI 服务启动
└── start.sh                            # 启动脚本

```

## 项目启动

python 环境和依赖安装  
```bash
pip install uv
cd genie-tool
uv sync
source .venv/bin/activate # Linux/MacOS 执行
. .venv/Scripts/activate # Windows 执行
```

首次启动，需要初始化数据库（后续不再需要）
```bash

cd genie-tool

python -m genie_tool.db.db_engine
```

启动服务
```bash

cd genie-tool

cp .env_template .env
# 填写环境变量

uv run python server.py
```

