# -*- coding: utf-8 -*-
# =====================
# 
# 
# Author: liumin.423
# Date:   2025/7/7
# =====================
import importlib

import yaml


def get_prompt(prompt_file):
    return yaml.safe_load(importlib.resources.files("genie_tool.prompt").joinpath(f"{prompt_file}.yaml").read_text(encoding="utf-8"))

