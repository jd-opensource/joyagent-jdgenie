# Genie 智能助手 - Docker Compose 部署指南

> 🎉 **优化升级**：使用 Docker Compose 一键部署！更简单、更可靠、更易维护。

## 📋 目录

- [快速开始](#-快速开始)
- [环境要求](#-环境要求)
- [配置说明](#-配置说明)
- [部署方式](#-部署方式)
- [服务管理](#-服务管理)
- [故障排除](#-故障排除)

## ⚡ 快速开始

### 1️⃣ 克隆项目
```bash
git clone https://github.com/jd-opensource/joyagent-jdgenie.git
cd joyagent-jdgenie
```

### 2️⃣ 修改 .env 文件
```bash
# 复制环境变量模板
cd docker
cp .env.example .env

# 编辑配置文件
vim .env
```

### 3️⃣ 一键部署
```bash
docker compose up -d
```

### 4️⃣ 访问服务
- 🌐 **前端页面**: http://your-ip:3000
- 🔧 **后端API**: http://your-ip:8080
- 🐍 **Python客户端**: http://your-ip:8188  
- 🛠️ **工具服务**: http://your-ip:1601

## 🔧 环境要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| **Docker** | 20.10+ | 容器运行时 |
| **Docker Compose** | 2.0+ | 容器编排工具 |
| **系统内存** | 4GB+ | 推荐 8GB+ |
| **可用存储** | 10GB+ | 包含镜像和数据 |

## ⚙️ 配置说明

### 核心配置

| 环境变量 | 说明 | 示例值 |
|----------|------|--------|
| `LLM_API_KEY` | LLM API密钥 | `sk-your-deepseek-api-key` |
| `LLM_BASE_URL` | LLM服务地址 | `https://api.deepseek.com/v1` |
| `LLM_MODEL` | 使用的模型名称 | `deepseek-chat` |
| `DEEPSEEK_API_KEY` | DeepSeek API密钥 | `sk-your-deepseek-api-key` |
| `SERPER_SEARCH_API_KEY` | 搜索API密钥 | `your-serper-search-api-key` |

### 端口配置

| 环境变量 | 默认端口 | 服务 | 说明 |
|----------|---------|------|------|
| `FRONTEND_PORT` | 3000 | 前端 | React应用 |
| `BACKEND_PORT` | 8080 | 后端 | Java Spring Boot |
| `TOOL_PORT` | 1601 | 工具服务 | Python工具服务 |
| `CLIENT_PORT` | 8188 | MCP客户端 | Python MCP客户端 |

## 🚀 部署方式

### .env文件配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑配置文件
vim .env

# 启动服务
docker compose up -d
```

## 🛠️ 服务管理

### 基本命令
```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f genie-backend

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 更新部署
docker compose up -d --build
```

### 数据管理
```bash
# 查看数据卷
docker volume ls | grep genie

# 备份数据
docker run --rm -v genie_tool_data:/data -v $(pwd):/backup alpine tar czf /backup/genie-tool-data.tar.gz -C /data .

# 恢复数据
docker run --rm -v genie_tool_data:/data -v $(pwd):/backup alpine tar xzf /backup/genie-tool-data.tar.gz -C /data
```

## 🔍 故障排除

### 常见问题

#### 1. 服务启动失败
```bash
# 查看详细日志
docker compose logs -f

# 检查端口占用
netstat -tlnp | grep -E "(3000|8080|8188|1601)"

# 检查Docker状态
docker info
```

#### 2. API调用失败
```bash
# 检查API密钥配置
echo $LLM_API_KEY
echo $DEEPSEEK_API_KEY

# 测试网络连接
curl -I https://api.deepseek.com/v1

# 检查服务健康状态
curl http://localhost:8080/web/health
```

#### 3. 前端无法访问后端
```bash
# 检查网络配置
docker network ls
docker network inspect genie_network

# 检查服务间通信
docker compose exec genie-frontend ping genie-backend
```

### 日志分析
```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f genie-backend
docker compose logs -f genie-tool

# 实时监控日志
docker compose logs -f --tail=100
```

## 🆚 部署方式对比

| 特性 | Docker Compose | 手动部署 | 单容器部署 |
|------|----------------|----------|------------|
| **部署复杂度** | 🟢 简单          | 🔴 复杂 | 🟡 中等 |
| **配置管理** | 🟢 环境变量        | 🔴 手动修改 | 🟡 配置文件 |
| **服务隔离** | 🟢 完全隔离        | 🟡 部分隔离 | 🟡 部分隔离 |
| **扩展性** | 🟢 易于扩展        | 🔴 困难 | 🟡 中等 |
| **维护性** | 🟢 统一管理        | 🔴 分散管理 | 🟡 中等 |
| **适用场景** | 快速部署           | 开发调试 | 简单部署 |

## 🎯 推荐使用场景

- ✅ **测试环境**: 快速搭建，环境隔离
- ✅ **演示部署**: 一键启动，配置简单
- ✅ **容器化部署**: 标准化部署流程
- ✅ **多环境管理**: 支持开发、测试、生产环境

---

> 💡 **提示**: 使用 Docker Compose 部署方式可以获得更好的隔离性、可移植性和维护性！

## 📚 相关文档

- 📖 [完整部署指南](../README.md)
- 🔧 [手动部署指南](../Deploy.md)
- 🐳 [Docker配置说明](./dockerfile/)
- 🚀 [快速开始指南](../README.md#快速开始) 