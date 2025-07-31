#!/bin/bash
chmod +x check_dep_port.sh
# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置文件路径
CONFIG_FILE="genie-backend/src/main/resources/application.yml"
ENV_TEMPLATE="genie-tool/.env_template"
ENV_FILE="genie-tool/.env"

# 检查配置是否完成
check_config_completed() {
    if [ ! -f "$CONFIG_FILE" ]; then
        echo -e "${RED}❌ 配置文件 $CONFIG_FILE 不存在${NC}"
        return 1
    fi
    
    # 如果.env文件不存在，自动复制模板
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠️  环境变量文件 $ENV_FILE 不存在，正在复制模板...${NC}"
        if [ -f "$ENV_TEMPLATE" ]; then
            cp "$ENV_TEMPLATE" "$ENV_FILE"
            echo -e "${GREEN}✅ 已复制环境变量模板文件${NC}"
        else
            echo -e "${RED}❌ 环境变量模板文件 $ENV_TEMPLATE 不存在${NC}"
            return 1
        fi
    fi
    
    # 检查配置文件是否还有占位符
    if grep -q "<input llm server here>" "$CONFIG_FILE" || grep -q "<input llm key here>" "$CONFIG_FILE"; then
        echo -e "${RED}❌ 后端配置文件 $CONFIG_FILE 中还有未配置的占位符${NC}"
        echo -e "${YELLOW}💡 请检查并替换以下占位符：${NC}"
        echo -e "   - <input llm server here> -> 你的LLM服务器地址"
        echo -e "   - <input llm key here> -> 你的LLM API密钥"
        return 1
    fi
    
    # 检查环境变量文件是否还有占位符（忽略注释行）
    if grep -v "^#" "$ENV_FILE" | grep -q "<your api key>" || grep -v "^#" "$ENV_FILE" | grep -q "<your base url>"; then
        echo -e "${RED}❌ 环境变量文件 $ENV_FILE 中还有未配置的占位符${NC}"
        echo -e "${YELLOW}💡 请检查并替换以下占位符：${NC}"
        echo -e "   - <your api key> -> 你的LLM API密钥"
        echo -e "   - <your base url> -> 你的LLM服务器地址"
        return 1
    fi
    
    return 0
}

# 配置检查
setup_config() {
    echo -e "${BLUE}🚀 配置检查...${NC}"
    echo "=================================="
    
    # 如果.env文件不存在，自动复制模板
    if [ ! -f "$ENV_FILE" ]; then
        echo -e "${YELLOW}⚠️  环境变量文件 $ENV_FILE 不存在，正在复制模板...${NC}"
        if [ -f "$ENV_TEMPLATE" ]; then
            cp "$ENV_TEMPLATE" "$ENV_FILE"
            echo -e "${GREEN}✅ 已复制环境变量模板文件${NC}"
        else
            echo -e "${RED}❌ 环境变量模板文件 $ENV_TEMPLATE 不存在${NC}"
            exit 1
        fi
    fi
    
    echo -e "${YELLOW}📝 请确保以下文件已正确配置：${NC}"
    echo ""
    echo -e "${BLUE}1. 后端配置文件: ${GREEN}$CONFIG_FILE${NC}"
    echo -e "   需要配置LLM服务信息："
    echo -e "   - 将 <input llm server here> 替换为你的LLM服务器地址"
    echo -e "   - 将 <input llm key here> 替换为你的LLM API密钥"
    echo ""
    echo -e "${BLUE}2. 工具服务环境变量: ${GREEN}$ENV_FILE${NC}"
    echo -e "   需要配置以下信息："
    echo -e "   - OPENAI_API_KEY: 你的LLM API密钥"
    echo -e "   - OPENAI_BASE_URL: 你的LLM服务器地址"
    echo -e "   - SERPER_SEARCH_API_KEY: Serper Search API密钥 (申请地址: https://serper.dev/)"
    echo ""
    echo -e "${YELLOW}💡 配置完成后，重新运行此脚本即可启动服务${NC}"
    echo "=================================="
    
    # 检查配置是否完成
    echo -e "${BLUE}🔍 检查配置文件...${NC}"
    if ! check_config_completed; then
        echo -e "${RED}❌ 配置文件检查失败，请完成配置后重新运行${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 配置文件检查通过，继续启动服务${NC}"
}

# 初始化设置
init_setup() {
    echo -e "${BLUE}🔧 初始化设置...${NC}"
    echo "=================================="
    
    # 1. 后端构建
    echo -e "${BLUE}🔨 构建后端项目...${NC}"
    cd genie-backend
    if sh build.sh; then
        echo -e "${GREEN}✅ 后端构建成功${NC}"
    else
        echo -e "${RED}❌ 后端构建失败${NC}"
        cd ..
        return 1
    fi
    cd ..
    
    # 2. 工具服务数据库初始化
    echo -e "${BLUE}🗄️  初始化工具服务数据库...${NC}"
    cd genie-tool
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo -e "${BLUE}创建Python虚拟环境...${NC}"
        uv sync
    fi
    
    # 激活虚拟环境并初始化数据库
    source .venv/bin/activate
    echo -e "${BLUE}初始化数据库...${NC}"
    if python -m genie_tool.db.db_engine; then
        echo -e "${GREEN}✅ 数据库初始化成功${NC}"
    else
        echo -e "${RED}❌ 数据库初始化失败${NC}"
        cd ..
        return 1
    fi
    cd ..
    
    # 3. MCP客户端虚拟环境创建
    echo -e "${BLUE}🔌 创建MCP客户端虚拟环境...${NC}"
    cd genie-client
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo -e "${BLUE}创建Python虚拟环境...${NC}"
        uv venv
    fi
    cd ..
    
    echo -e "${GREEN}✅ 初始化设置完成${NC}"
    echo "=================================="
}

# 启动前端服务
start_frontend() {
    echo -e "${BLUE}🌐 启动前端服务...${NC}"
    cd ui
    if [ -f "start.sh" ]; then
        sh start.sh &
        FRONTEND_PID=$!
        echo -e "${GREEN}✅ 前端服务启动中 (PID: $FRONTEND_PID)${NC}"
    else
        echo -e "${RED}❌ 前端启动脚本不存在${NC}"
        return 1
    fi
    cd ..
}

# 启动后端服务
start_backend() {
    echo -e "${BLUE}🔧 启动后端服务...${NC}"
    cd genie-backend
    
    # 启动服务
    if [ -f "start.sh" ]; then
        sh start.sh &
        BACKEND_PID=$!
        echo -e "${GREEN}✅ 后端服务启动中 (PID: $BACKEND_PID)${NC}"
    else
        echo -e "${RED}❌ 后端启动脚本不存在${NC}"
        cd ..
        return 1
    fi
    cd ..
}

# 启动工具服务
start_tool_service() {
    echo -e "${BLUE}🛠️  启动工具服务...${NC}"
    cd genie-tool
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo -e "${BLUE}创建Python虚拟环境...${NC}"
        uv sync
    fi
    
    # 激活虚拟环境并启动
    source .venv/bin/activate
    
    # 启动服务
    if [ -f "start.sh" ]; then
        sh start.sh &
        TOOL_PID=$!
        echo -e "${GREEN}✅ 工具服务启动中 (PID: $TOOL_PID)${NC}"
    else
        echo -e "${RED}❌ 工具启动脚本不存在${NC}"
        cd ..
        return 1
    fi
    cd ..
}

# 启动MCP客户端服务
start_mcp_client() {
    echo -e "${BLUE}🔌 启动MCP客户端服务...${NC}"
    cd genie-client
    
    # 检查虚拟环境
    if [ ! -d ".venv" ]; then
        echo -e "${BLUE}创建Python虚拟环境...${NC}"
        uv venv
    fi
    
    # 激活虚拟环境并启动
    source .venv/bin/activate
    
    if [ -f "start.sh" ]; then
        sh start.sh &
        MCP_PID=$!
        echo -e "${GREEN}✅ MCP客户端服务启动中 (PID: $MCP_PID)${NC}"
    else
        echo -e "${RED}❌ MCP客户端启动脚本不存在${NC}"
        cd ..
        return 1
    fi
    cd ..
}

# 显示进度条
show_progress() {
    local current=$1
    local total=$2
    local width=50
    local percentage=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))
    
    printf "\r${BLUE}["
    printf "%${filled}s" | tr ' ' '█'
    printf "%${empty}s" | tr ' ' '░'
    printf "] ${percentage}%% (${current}/${total})${NC}"
}

# 等待服务启动
wait_for_services() {
    echo -e "${BLUE}⏳ 等待服务启动...${NC}"
    
    local services=(
        "前端服务:3000"
        "后端服务:8080" 
        "工具服务:1601"
        "MCP客户端:8188"
    )
    
    local total_services=${#services[@]}
    local started_services=0
    local failed_services=()
    local max_attempts=30
    local attempt=0
    
    echo ""
    
    while [ $attempt -lt $max_attempts ] && [ $started_services -lt $total_services ]; do
        started_services=0
        failed_services=()
        
        for service_info in "${services[@]}"; do
            IFS=':' read -r service_name port <<< "$service_info"
            
            if curl -s http://localhost:$port > /dev/null 2>&1; then
                started_services=$((started_services + 1))
            else
                failed_services+=("$service_name")
            fi
        done
        
        show_progress $started_services $total_services
        attempt=$((attempt + 1))
        sleep 2
    done
    
    echo ""
    echo ""
    echo -e "${BLUE}🔍 服务启动状态检查...${NC}"
    echo "=================================="
    
    # 详细检查每个服务
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service_info"
        
        if curl -s http://localhost:$port > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name 运行正常 (http://localhost:$port)${NC}"
        else
            echo -e "${RED}❌ $service_name 启动失败 (http://localhost:$port)${NC}"
        fi
    done
    
    echo "=================================="
    
    # 显示失败的服务
    if [ ${#failed_services[@]} -gt 0 ]; then
        echo -e "${RED}⚠️  以下服务启动失败：${NC}"
        for service in "${failed_services[@]}"; do
            echo -e "${RED}   - $service${NC}"
        done
        echo ""
        echo -e "${YELLOW}💡 建议：${NC}"
        echo -e "   - 检查端口是否被占用"
        echo -e "   - 查看对应服务的日志"
        echo -e "   - 重新运行启动脚本"
        echo "=================================="
    fi
}

# 显示服务信息
show_service_info() {
    local services=(
        "前端界面:3000"
        "后端API:8080" 
        "工具服务:1601"
        "MCP客户端:8188"
    )
    
    local all_running=true
    
    # 检查所有服务是否都运行正常
    for service_info in "${services[@]}"; do
        IFS=':' read -r service_name port <<< "$service_info"
        if ! curl -s http://localhost:$port > /dev/null 2>&1; then
            all_running=false
            break
        fi
    done
    
    echo "=================================="
    if [ "$all_running" = true ]; then
        echo -e "${GREEN}🎉 所有服务启动完成！${NC}"
        echo "=================================="
        echo -e "${BLUE}服务访问地址：${NC}"
        echo -e "  🌐 前端界面: ${GREEN}http://localhost:3000${NC}"
        echo -e "  🔧 后端API: ${GREEN}http://localhost:8080${NC}"
        echo -e "  🛠️  工具服务: ${GREEN}http://localhost:1601${NC}"
        echo -e "  🔌 MCP客户端: ${GREEN}http://localhost:8188${NC}"
    else
        echo -e "${YELLOW}⚠️  部分服务启动完成${NC}"
        echo "=================================="
        echo -e "${BLUE}可用的服务地址：${NC}"
        for service_info in "${services[@]}"; do
            IFS=':' read -r service_name port <<< "$service_info"
            if curl -s http://localhost:$port > /dev/null 2>&1; then
                echo -e "  ✅ $service_name: ${GREEN}http://localhost:$port${NC}"
            else
                echo -e "  ❌ $service_name: ${RED}http://localhost:$port (未启动)${NC}"
            fi
        done
    fi
    
    echo "=================================="
    echo -e "${YELLOW}💡 提示：${NC}"
    echo -e "  - 使用 Ctrl+C 停止所有服务"
    echo -e "  - 查看日志: tail -f genie-backend/genie-backend_startup.log"
    echo -e "  - 重新启动: ./start_genie_one_click.sh"
    echo "=================================="
}

# 清理函数
cleanup() {
    echo -e "\n${YELLOW}🛑 正在停止所有服务...${NC}"
    
    # 停止所有后台进程
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    fi
    
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    fi
    
    if [ ! -z "$TOOL_PID" ]; then
        kill $TOOL_PID 2>/dev/null
        echo -e "${GREEN}✅ 工具服务已停止${NC}"
    fi
    
    if [ ! -z "$MCP_PID" ]; then
        kill $MCP_PID 2>/dev/null
        echo -e "${GREEN}✅ MCP客户端服务已停止${NC}"
    fi
    
    # 清理占用端口的进程
    echo -e "${BLUE}🔍 清理占用端口的进程...${NC}"
    PORTS=(3000 8080 1601 8188)
    for port in "${PORTS[@]}"; do
        local pids=$(lsof -ti :$port 2>/dev/null)
        if [ ! -z "$pids" ]; then
            echo -e "${YELLOW}   清理端口 $port 的进程...${NC}"
            for pid in $pids; do
                echo -e "${BLUE}     停止进程 PID: $pid${NC}"
                kill -9 $pid 2>/dev/null
            done
            sleep 1
        fi
    done
    
    # 清理临时文件
    rm -f genie-backend/src/main/resources/application.yml.bak
    rm -f genie-tool/.env.bak
    
    echo -e "${GREEN}🎉 所有服务已停止${NC}"
    exit 0
}

# 设置信号处理
trap cleanup SIGINT SIGTERM

# 主函数
main() {
    echo -e "${BLUE}🚀 JoyAgent JDGenie 一键启动脚本${NC}"
    echo "=================================="
    
    # 检查依赖
    echo -e "${BLUE}🔍 检查系统依赖...${NC}"
    if ! ./check_dep_port.sh; then
        echo -e "${RED}❌ 依赖检查失败，请先安装缺失的依赖${NC}"
        exit 1
    fi
    
    # 配置检查
    setup_config
    init_setup
    
    echo "=================================="
    echo -e "${BLUE}🚀 开始启动所有服务...${NC}"
    echo "=================================="
    
    # 启动各个服务
    start_frontend
    start_backend
    start_tool_service
    start_mcp_client
    
    # 等待服务启动
    wait_for_services
    
    # 显示服务信息
    show_service_info
    
    # 保持脚本运行
    echo -e "${BLUE}⏳ 服务运行中，按 Ctrl+C 停止...${NC}"
    while true; do
        sleep 1
    done
}

# 运行主函数
main "$@" 
