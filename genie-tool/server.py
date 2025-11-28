# -*- coding: utf-8 -*-
# =====================
# 
# 
# Author: liumin.423
# Date:   2025/7/7
# =====================
import os
from optparse import OptionParser
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from loguru import logger
from starlette.middleware.cors import CORSMiddleware

from genie_tool.util.middleware_util import UnknownException, HTTPProcessTimeMiddleware
from genie_tool.db.db_engine import init_db

load_dotenv()


def print_logo():
    from pyfiglet import Figlet
    f = Figlet(font="slant")
    print(f.renderText("Genie Tool"))


def log_setting():
    log_path = os.getenv("LOG_PATH", Path(__file__).resolve().parent / "logs" / "server.log")
    log_format = "{time:YYYY-MM-DD HH:mm:ss.SSS} {level} {module}.{function} {message}"
    logger.add(log_path, format=log_format, rotation="200 MB")


def create_app() -> FastAPI:
    _app = FastAPI(
        on_startup=[log_setting, print_logo]
    )

    register_middleware(_app)
    register_router(_app)

    return _app

def register_middleware(app: FastAPI):
    app.add_middleware(UnknownException)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.add_middleware(HTTPProcessTimeMiddleware)


def register_router(app: FastAPI):
    from genie_tool.api import api_router
    app.include_router(api_router)


app = create_app()


if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--host", dest="host", type="string", default="0.0.0.0")
    parser.add_option("--port", dest="port", type="int", default=1601)
    parser.add_option("--workers", dest="workers", type="int", default=10)
    (options, args) = parser.parse_args()

    print(f"Start params: {options}")
    init_db()

    uvicorn.run(
        app="server:app",
        host=options.host,
        port=options.port,
        workers=options.workers,
        reload=os.getenv("ENV", "local") == "local",
    )
