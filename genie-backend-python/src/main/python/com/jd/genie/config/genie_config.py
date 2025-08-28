"""
Genie configuration module.
"""

import os
import yaml
import json
import logging
from typing import Any, Dict, Optional, List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

try:
    from ..agent.llm.llm_settings import LLMSettings
except ImportError:
    from com.jd.genie.agent.llm.llm_settings import LLMSettings

logger = logging.getLogger(__name__)


class GenieConfig(BaseSettings):
    """Configuration settings for Genie application."""
    
    model_config = SettingsConfigDict(env_prefix="AUTOBOTS_")
    
    def __init__(self, **data):
        """Initialize configuration with YAML file support."""
        # Load from YAML file if exists
        yaml_config = self._load_yaml_config()
        if yaml_config:
            data = {**yaml_config, **data}  # Allow env overrides
        super().__init__(**data)
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        # Try multiple possible locations for the YAML file
        possible_paths = [
            'src/main/resources/application.yml',
            '../resources/application.yml',
            'application.yml',
            os.path.join(os.path.dirname(__file__), '..', '..', 'resources', 'application.yml')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        yaml_data = yaml.safe_load(f)
                        return self._parse_yaml_config(yaml_data)
                except Exception as e:
                    logger.error(f"Failed to load YAML config from {path}: {e}")
        
        return {}
    
    def _parse_yaml_config(self, yaml_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse YAML configuration to match Pydantic fields."""
        config = {}
        
        # Parse autobots configuration
        if 'autobots' in yaml_data:
            autobots = yaml_data['autobots']
            autoagent = autobots.get('autoagent', {})
            
            # Parse planner configuration
            if 'planner' in autoagent:
                planner = autoagent['planner']
                if 'system_prompt' in planner:
                    config['planner_system_prompt_map'] = json.loads(planner.get('system_prompt', '{}'))
                if 'next_step_prompt' in planner:
                    config['planner_next_step_prompt_map'] = json.loads(planner.get('next_step_prompt', '{}'))
                config['planner_model_name'] = planner.get('model_name', 'gpt-4.1')
                config['planner_max_steps'] = planner.get('max_steps', 40)
                config['plan_pre_prompt'] = planner.get('pre_prompt', '')
                config['planning_close_update'] = str(planner.get('close_update', 1))
            
            # Parse executor configuration
            if 'executor' in autoagent:
                executor = autoagent['executor']
                if 'system_prompt' in executor:
                    config['executor_system_prompt_map'] = json.loads(executor.get('system_prompt', '{}'))
                if 'next_step_prompt' in executor:
                    config['executor_next_step_prompt_map'] = json.loads(executor.get('next_step_prompt', '{}'))
                if 'sop_prompt' in executor:
                    config['executor_sop_prompt_map'] = json.loads(executor.get('sop_prompt', '{}'))
                config['executor_model_name'] = executor.get('model_name', 'gpt-4.1')
                config['executor_max_steps'] = executor.get('max_steps', 40)
                config['max_observe'] = str(executor.get('max_observe', 10000))
            
            # Parse react configuration
            if 'react' in autoagent:
                react = autoagent['react']
                if 'system_prompt' in react:
                    config['react_system_prompt_map'] = json.loads(react.get('system_prompt', '{}'))
                if 'next_step_prompt' in react:
                    config['react_next_step_prompt_map'] = json.loads(react.get('next_step_prompt', '{}'))
                config['react_model_name'] = react.get('model_name', 'gpt-4.1')
                config['react_max_steps'] = react.get('max_steps', 40)
            
            # Parse tool configuration
            if 'tool' in autoagent:
                tool = autoagent['tool']
                if 'plan_tool' in tool:
                    config['plan_tool_desc'] = tool['plan_tool'].get('desc', '')
                    config['plan_tool_params'] = json.loads(tool['plan_tool'].get('params', '{}'))
                if 'code_agent' in tool:
                    config['code_agent_desc'] = tool['code_agent'].get('desc', '')
                    config['code_agent_params'] = json.loads(tool['code_agent'].get('params', '{}'))
                if 'report_tool' in tool:
                    config['report_tool_desc'] = tool['report_tool'].get('desc', '')
                    config['report_tool_params'] = json.loads(tool['report_tool'].get('params', '{}'))
                if 'file_tool' in tool:
                    config['file_tool_desc'] = tool['file_tool'].get('desc', '')
                    config['file_tool_params'] = json.loads(tool['file_tool'].get('params', '{}'))
                    config['file_tool_content_truncate_len'] = tool['file_tool'].get('truncate_len', 30000)
                if 'deep_search_tool' in tool:
                    config['deep_search_tool_desc'] = tool['deep_search_tool'].get('desc', '')
                if 'deep_search' in tool:
                    config['deep_search_tool_params'] = json.loads(tool['deep_search'].get('params', '{}'))
                    config['deep_search_page_count'] = str(tool['deep_search'].get('page_count', 5))
                    if 'file_desc' in tool['deep_search']:
                        config['deep_search_tool_file_desc_truncate_len'] = tool['deep_search']['file_desc'].get('truncate_len', 1500)
                    if 'message' in tool['deep_search']:
                        config['deep_search_tool_message_truncate_len'] = tool['deep_search']['message'].get('truncate_len', 20000)
                config['clear_tool_message'] = str(tool.get('clear_tool_message', 1))
            
            # Parse URLs
            config['code_interpreter_url'] = autoagent.get('code_interpreter_url', 'http://127.0.0.1:1601')
            config['deep_search_url'] = autoagent.get('deep_search_url', 'http://127.0.0.1:1601')
            config['mcp_client_url'] = autoagent.get('mcp_client_url', 'http://127.0.0.1:8188')
            config['mcp_server_url_arr'] = [autoagent.get('mcp_server_url', '')]
            
            # Parse summary configuration
            if 'summary' in autoagent:
                summary = autoagent['summary']
                config['summary_system_prompt'] = summary.get('system_prompt', '')
                config['message_size_limit'] = summary.get('message_size_limit', 1500)
            
            # Parse other configurations
            config['digital_employee_prompt'] = autoagent.get('digital_employee_prompt', '')
            config['struct_parse_tool_system_prompt'] = autoagent.get('struct_parse_tool_system_prompt', '')
            config['sensitive_patterns'] = json.loads(autoagent.get('sensitive_patterns', '{}'))
            config['output_style_prompts'] = json.loads(autoagent.get('output_style_prompts', '{}'))
            config['message_interval'] = json.loads(autoagent.get('message_interval', '{}'))
        
        # Parse LLM configuration
        if 'llm' in yaml_data:
            llm = yaml_data['llm']
            if 'settings' in llm:
                settings_str = llm['settings']
                if settings_str:
                    settings_data = json.loads(settings_str)
                    llm_settings = {}
                    for model_name, model_config in settings_data.items():
                        llm_settings[model_name] = LLMSettings(**model_config)
                    config['llm_settings_map'] = llm_settings
        
        return config
    
    # Planner prompts
    planner_system_prompt_map: Dict[str, str] = Field(default_factory=dict)
    planner_next_step_prompt_map: Dict[str, str] = Field(default_factory=dict)
    
    # Executor prompts
    executor_system_prompt_map: Dict[str, str] = Field(default_factory=dict)
    executor_next_step_prompt_map: Dict[str, str] = Field(default_factory=dict)
    executor_sop_prompt_map: Dict[str, str] = Field(default_factory=dict)
    
    # React prompts
    react_system_prompt_map: Dict[str, str] = Field(default_factory=dict)
    react_next_step_prompt_map: Dict[str, str] = Field(default_factory=dict)
    
    # Model names
    planner_model_name: str = Field(default="gpt-4o-0806", alias="autoagent_planner_model_name")
    executor_model_name: str = Field(default="gpt-4o-0806", alias="autoagent_executor_model_name")
    react_model_name: str = Field(default="gpt-4o-0806", alias="autoagent_react_model_name")
    
    # Tool descriptions
    plan_tool_desc: str = Field(default="", alias="autoagent_tool_plan_tool_desc")
    code_agent_desc: str = Field(default="", alias="autoagent_tool_code_agent_desc")
    report_tool_desc: str = Field(default="", alias="autoagent_tool_report_tool_desc")
    file_tool_desc: str = Field(default="", alias="autoagent_tool_file_tool_desc")
    deep_search_tool_desc: str = Field(default="", alias="autoagent_tool_deep_search_tool_desc")
    
    # Tool parameters
    plan_tool_params: Dict[str, Any] = Field(default_factory=dict)
    code_agent_params: Dict[str, Any] = Field(default_factory=dict)
    report_tool_params: Dict[str, Any] = Field(default_factory=dict)
    file_tool_params: Dict[str, Any] = Field(default_factory=dict)
    deep_search_tool_params: Dict[str, Any] = Field(default_factory=dict)
    
    # Truncation lengths
    file_tool_content_truncate_len: int = Field(default=5000, alias="autoagent_tool_file_tool_truncate_len")
    deep_search_tool_file_desc_truncate_len: int = Field(default=500, alias="autoagent_tool_deep_search_file_desc_truncate_len")
    deep_search_tool_message_truncate_len: int = Field(default=500, alias="autoagent_tool_deep_search_message_truncate_len")
    
    # Prompts
    plan_pre_prompt: str = Field(default="分析问题并制定计划：", alias="autoagent_planner_pre_prompt")
    task_pre_prompt: str = Field(default="参考对话历史回答，", alias="autoagent_task_pre_prompt")
    
    # Settings
    clear_tool_message: str = Field(default="1", alias="autoagent_tool_clear_tool_message")
    planning_close_update: str = Field(default="1", alias="autoagent_planner_close_update")
    deep_search_page_count: str = Field(default="5", alias="autoagent_deep_search_page_count")
    
    # Tool lists
    multi_agent_tool_list_map: Dict[str, str] = Field(default_factory=dict)
    
    # LLM Settings
    llm_settings_map: Dict[str, LLMSettings] = Field(default_factory=dict)
    
    # Max steps
    planner_max_steps: int = Field(default=40, alias="autoagent_planner_max_steps")
    executor_max_steps: int = Field(default=40, alias="autoagent_executor_max_steps")
    react_max_steps: int = Field(default=40, alias="autoagent_react_max_steps")
    
    # Other settings
    max_observe: str = Field(default="10000", alias="autoagent_executor_max_observe")
    code_interpreter_url: str = Field(default="", alias="autoagent_code_interpreter_url")
    deep_search_url: str = Field(default="", alias="autoagent_deep_search_url")
    mcp_client_url: str = Field(default="", alias="autoagent_mcp_client_url")
    mcp_server_url_arr: List[str] = Field(default_factory=list, alias="autoagent_mcp_server_url")
    
    # Summary settings
    summary_system_prompt: str = Field(default="", alias="autoagent_summary_system_prompt")
    digital_employee_prompt: str = Field(default="", alias="autoagent_digital_employee_prompt")
    message_size_limit: int = Field(default=1000, alias="autoagent_summary_message_size_limit")
    
    # Patterns and styles
    sensitive_patterns: Dict[str, str] = Field(default_factory=dict)
    output_style_prompts: Dict[str, str] = Field(default_factory=dict)
    message_interval: Dict[str, str] = Field(default_factory=dict)
    struct_parse_tool_system_prompt: str = Field(default="", alias="autoagent_struct_parse_tool_system_prompt")
    
    # SSE Client settings
    sse_client_read_timeout: int = Field(default=1800, alias="multiagent_sseClient_readTimeout")
    sse_client_connect_timeout: int = Field(default=1800, alias="multiagent_sseClient_connectTimeout")
    
    # User setting
    user_name: str = Field(default="")
    default_model_name: str = Field(default="gpt-4o-0806")
    
    # Prompts
    genie_sop_prompt: str = Field(default="", alias="autoagent_genie_sop_prompt")
    genie_base_prompt: str = Field(default="", alias="autoagent_genie_base_prompt")
    struct_pre_post_prompt_config: str = Field(default="{}", alias="autoagent_struct_pre_post_prompt_config")
    open_think_function_call_split: str = Field(default="{}", alias="autoagent_open_think_function_call_split")
    
    def get_server_config(self) -> Dict[str, Any]:
        """Get server configuration."""
        return {
            'port': 8080,
            'debug': False
        }
    
    def get_output_style_prompts(self) -> Dict[str, str]:
        """Get output style prompts."""
        return self.output_style_prompts
    
    @classmethod
    def from_env(cls) -> 'GenieConfig':
        """
        Create a configuration instance from environment variables.
        
        Returns:
            GenieConfig instance initialized from environment
        """
        return cls()
    
    def get_planner_system_prompt(self, key: str = 'default') -> str:
        """Get planner system prompt by key."""
        return self.planner_system_prompt_map.get(key, '')
    
    def get_planner_next_step_prompt(self, key: str = 'default') -> str:
        """Get planner next step prompt by key."""
        return self.planner_next_step_prompt_map.get(key, '')
    
    def get_executor_system_prompt(self, key: str = 'default') -> str:
        """Get executor system prompt by key."""
        return self.executor_system_prompt_map.get(key, '')
    
    def get_executor_next_step_prompt(self, key: str = 'default') -> str:
        """Get executor next step prompt by key."""
        return self.executor_next_step_prompt_map.get(key, '')
    
    def get_executor_sop_prompt(self, key: str = 'default') -> str:
        """Get executor SOP prompt by key."""
        return self.executor_sop_prompt_map.get(key, '')
    
    def get_react_system_prompt(self, key: str = 'default') -> str:
        """Get react system prompt by key."""
        return self.react_system_prompt_map.get(key, '')
    
    def get_react_next_step_prompt(self, key: str = 'default') -> str:
        """Get react next step prompt by key."""
        return self.react_next_step_prompt_map.get(key, '')
    
    def get_multi_agent_tool_list_map(self) -> Dict[str, str]:
        """Get multi-agent tool list map."""
        if not self.multi_agent_tool_list_map:
            return {'default': 'search,code,report'}
        return self.multi_agent_tool_list_map
    
    def get_mcp_server_url_arr(self) -> List[str]:
        """Get MCP server URL array."""
        return self.mcp_server_url_arr if self.mcp_server_url_arr else []
    
    def get_llm_settings(self, model_name: str) -> Optional[LLMSettings]:
        """Get LLM settings by model name."""
        return self.llm_settings_map.get(model_name)
    
    def get_plan_tool_params_json(self) -> str:
        """Get plan tool parameters as JSON string."""
        return json.dumps(self.plan_tool_params)
    
    def get_code_agent_params_json(self) -> str:
        """Get code agent parameters as JSON string."""
        return json.dumps(self.code_agent_params)
    
    def get_report_tool_params_json(self) -> str:
        """Get report tool parameters as JSON string."""
        return json.dumps(self.report_tool_params)
    
    def get_file_tool_params_json(self) -> str:
        """Get file tool parameters as JSON string."""
        return json.dumps(self.file_tool_params)
    
    def get_deep_search_tool_params_json(self) -> str:
        """Get deep search tool parameters as JSON string."""
        return json.dumps(self.deep_search_tool_params)