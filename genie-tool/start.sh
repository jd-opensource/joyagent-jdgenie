#!/usr/bin/env bash

# 激活虚拟环境
if [ -f ".venv/Scripts/activate" ]; then
    . .venv/Scripts/activate; # Windows 环境
elif [ -f ".venv/bin/activate" ]; then
    . .venv/bin/activate; # Linux/Mac 环境
else
    echo -e "❌ 虚拟环境激活脚本不存在${NC}"
    return 1
fi

# 运行Python服务器
python server.py
