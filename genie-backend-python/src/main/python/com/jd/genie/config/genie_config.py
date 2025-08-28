"""
Genie configuration module.
"""

import json
import logging
from typing import Any, Dict, Optional

from pydantic import BaseSettings, Field
from pydantic_settings import SettingsConfigDict

from ..agent.llm.llm_settings import LLMSettings

logger = logging.getLogger(__name__)


class GenieConfig(BaseSettings):
    """Configuration settings for Genie application."""
    
    model_config = SettingsConfigDict(env_prefix="AUTOBOTS_")
    
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
    mcp_server_url_arr: list[str] = Field(default_factory=list, alias="autoagent_mcp_server_url")
    
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
    
    # Genie specific prompts
    genie_sop_prompt: str = Field(default="", alias="autoagent_genie_sop_prompt")
    genie_base_prompt: str = Field(default="", alias="autoagent_genie_base_prompt")
    task_complete_desc: str = Field(default="当前task完成，请将当前task标记为 completed", alias="autoagent_tool_task_complete_desc")
    
    def __init__(self, **kwargs):
        """Initialize configuration with custom parsing for JSON fields."""
        super().__init__(**kwargs)
        self._parse_json_fields()
    
    def _parse_json_fields(self) -> None:
        """Parse JSON string fields into dictionaries."""
        json_fields = [
            'planner_system_prompt_map',
            'planner_next_step_prompt_map', 
            'executor_system_prompt_map',
            'executor_next_step_prompt_map',
            'executor_sop_prompt_map',
            'react_system_prompt_map',
            'react_next_step_prompt_map',
            'plan_tool_params',
            'code_agent_params',
            'report_tool_params',
            'file_tool_params',
            'deep_search_tool_params',
            'multi_agent_tool_list_map',
            'llm_settings_map',
            'sensitive_patterns',
            'output_style_prompts',
            'message_interval'
        ]
        
        for field_name in json_fields:
            field_value = getattr(self, field_name, {})
            if isinstance(field_value, str) and field_value:
                try:
                    parsed_value = json.loads(field_value)
                    setattr(self, field_name, parsed_value)
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse JSON for field {field_name}: {e}")
                    setattr(self, field_name, {})
    
    @classmethod
    def from_env(cls) -> "GenieConfig":
        """Create configuration from environment variables."""
        return cls()
    
    def get_output_style_prompts(self) -> Dict[str, str]:
        """Get output style prompts."""
        return self.output_style_prompts
    
    def get_multi_agent_tool_list_map(self) -> Dict[str, str]:
        """Get multi-agent tool list map."""
        return self.multi_agent_tool_list_map
    
    def get_mcp_server_url_arr(self) -> list[str]:
        """Get MCP server URL array."""
        return self.mcp_server_url_arr