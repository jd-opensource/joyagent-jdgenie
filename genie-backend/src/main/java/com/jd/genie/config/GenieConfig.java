package com.jd.genie.config;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.TypeReference;
import com.jd.genie.agent.llm.LLMSettings;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.Map;

@Slf4j
@Getter
@Configuration
public class GenieConfig {

    private Map<String, String> plannerSystemPromptMap = new HashMap<>();
    @Value("${autobots.autoagent.planner.system_prompt:{}}")
    public void setPlannerSystemPromptMap(String list) {
        plannerSystemPromptMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> plannerNextStepPromptMap = new HashMap<>();
    @Value("${autobots.autoagent.planner.next_step_prompt:{}}")
    public void setPlannerNextStepPromptMap(String list) {
        plannerNextStepPromptMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> executorSystemPromptMap = new HashMap<>();
    @Value("${autobots.autoagent.executor.system_prompt:{}}")
    public void setExecutorSystemPromptMap(String list) {
        executorSystemPromptMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> executorNextStepPromptMap = new HashMap<>();
    @Value("${autobots.autoagent.executor.next_step_prompt:{}}")
    public void setExecutorNextStepPromptMap(String list) {
        executorNextStepPromptMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> executorSopPromptMap = new HashMap<>();
    @Value("${autobots.autoagent.executor.sop_prompt:{}}")
    public void setExecutorSopPromptMap(String list) {
        executorSopPromptMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> reactSystemPromptMap = new HashMap<>();
    @Value("${autobots.autoagent.react.system_prompt:{}}")
    public void setReactSystemPromptMap(String list) {
        reactSystemPromptMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> reactNextStepPromptMap = new HashMap<>();
    @Value("${autobots.autoagent.react.next_step_prompt:{}}")
    public void setReactNextStepPromptMap(String list) {
        reactNextStepPromptMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    @Value("${autobots.autoagent.planner.model_name:gpt-4o-0806}")
    private String plannerModelName;

    @Value("${autobots.autoagent.executor.model_name:gpt-4o-0806}")
    private String executorModelName;

    @Value("${autobots.autoagent.react.model_name:gpt-4o-0806}")
    private String reactModelName;

    @Value("${autobots.autoagent.tool.plan_tool.desc:}")
    private String planToolDesc;

    @Value("${autobots.autoagent.tool.code_agent.desc:}")
    private String codeAgentDesc;

    @Value("${autobots.autoagent.tool.report_tool.desc:}")
    private String reportToolDesc;

    @Value("${autobots.autoagent.tool.file_tool.desc:}")
    private String fileToolDesc;

    @Value("${autobots.autoagent.tool.deep_search_tool.desc:}")
    private String deepSearchToolDesc;

    /**
     * planTool 配置
     */
    private Map<String, Object> planToolParams = new HashMap<>();
    @Value("${autobots.autoagent.tool.plan_tool.params:{}}")
    public void setPlanToolParams(String jsonStr) {
        this.planToolParams = JSON.parseObject(jsonStr, Map.class);
    }

    /**
     * codeAgent 配置
     */
    private Map<String, Object> codeAgentPamras = new HashMap<>();
    @Value("${autobots.autoagent.tool.code_agent.params:{}}")
    public void setCodeAgentPamras(String jsonStr) {
        this.codeAgentPamras = JSON.parseObject(jsonStr, Map.class);
    }

    /**
     * reportTool 配置
     */
    private Map<String, Object> reportToolPamras = new HashMap<>();
    @Value("${autobots.autoagent.tool.report_tool.params:{}}")
    public void setHtmlToolPamras(String jsonStr) {
        this.reportToolPamras = JSON.parseObject(jsonStr, Map.class);
    }

    /**
     * fileTool 配置
     */
    private Map<String, Object> fileToolPamras = new HashMap<>();
    @Value("${autobots.autoagent.tool.file_tool.params:{}}")
    public void setFileoolPamras(String jsonStr) {
        this.fileToolPamras = JSON.parseObject(jsonStr, Map.class);
    }

    /**
     * DeepSearchTool 配置
     */
    private Map<String, Object> deepSearchToolPamras = new HashMap<>();
    @Value("${autobots.autoagent.tool.deep_search.params:{}}")
    public void setDeepSearchToolPamras(String jsonStr) {
        this.deepSearchToolPamras = JSON.parseObject(jsonStr, Map.class);
    }

    @Value("${autobots.autoagent.tool.file_tool.truncate_len:5000}")
    private Integer fileToolContentTruncateLen;

    @Value("${autobots.autoagent.tool.deep_search.file_desc.truncate_len:500}")
    private Integer deepSearchToolFileDescTruncateLen;

    @Value("${autobots.autoagent.tool.deep_search.message.truncate_len:500}")
    private Integer deepSearchToolMessageTruncateLen;

    @Value("${autobots.autoagent.planner.pre_prompt:分析问题并制定计划：}")
    private String planPrePrompt;

    @Value("${autobots.autoagent.task.pre_prompt:参考对话历史回答，}")
    private String taskPrePrompt;

    @Value("${autobots.autoagent.tool.clear_tool_message:1}")
    private String clearToolMessage;

    @Value("${autobots.autoagent.planner.close_update:1}")
    private String planningCloseUpdate;

    @Value("${autobots.autoagent.deep_search_page_count:5}")
    private String deepSearchPageCount;

    private Map<String, String> multiAgentToolListMap = new HashMap<>();
    @Value("${autobots.autoagent.tool_list:{}}")
    public void setMultiAgentToolList(String list) {
        multiAgentToolListMap = JSONObject.parseObject(list, new TypeReference<Map<String, String>>() {
        });
    }

    /**
     * LLM Settings
     */
    private Map<String, LLMSettings> llmSettingsMap;
    @Value("${llm.settings:{}}")
    public void setLLMSettingsMap(String jsonStr) {
        this.llmSettingsMap = JSON.parseObject(jsonStr, new TypeReference<Map<String, LLMSettings>>() {
        });
    }

    @Value("${autobots.autoagent.planner.max_steps:40}")
    private Integer plannerMaxSteps;

    @Value("${autobots.autoagent.executor.max_steps:40}")
    private Integer executorMaxSteps;

    @Value("${autobots.autoagent.react.max_steps:40}")
    private Integer reactMaxSteps;;

    @Value("${autobots.autoagent.executor.max_observe:10000}")
    private String maxObserve;

    @Value("${autobots.autoagent.code_interpreter_url:}")
    private String CodeInterpreterUrl;

    @Value("${autobots.autoagent.deep_search_url:}")
    private String DeepSearchUrl;

    @Value("${autobots.autoagent.mcp_client_url:}")
    private String mcpClientUrl;

    @Value("${autobots.autoagent.mcp_server_url:}")
    private String[] mcpServerUrlArr;

    @Value("${autobots.autoagent.summary.system_prompt:}")
    private String summarySystemPrompt;

    @Value("${autobots.autoagent.digital_employee_prompt:}")
    private String digitalEmployeePrompt;

    @Value("${autobots.autoagent.summary.message_size_limit:1000}")
    private Integer messageSizeLimit;

    private Map<String, String> sensitivePatterns = new HashMap<>();
    @Value("${autobots.autoagent.sensitive_patterns:{}}")
    public void setSensitivePatterns(String jsonStr) {
        this.sensitivePatterns = JSON.parseObject(jsonStr, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> outputStylePrompts = new HashMap<>();
    @Value("${autobots.autoagent.output_style_prompts:{}}")
    public void setOutputStylePrompts(String jsonStr) {
        this.outputStylePrompts = JSON.parseObject(jsonStr, new TypeReference<Map<String, String>>() {
        });
    }

    private Map<String, String> messageInterval = new HashMap<>();
    @Value("${autobots.autoagent.message_interval:{}}")
    public void setMessageInterval(String jsonStr) {
        this.messageInterval = JSON.parseObject(jsonStr, new TypeReference<Map<String, String>>() {
        });
    }

    private String structParseToolSystemPrompt = "";
    @Value("${autobots.autoagent.struct_parse_tool_system_prompt:}")
    public void setStructParseToolSystemPrompt(String str) {
        this.structParseToolSystemPrompt = str;
    }

	@Value("${autobots.multiagent.sseClient.readTimeout:1800}")
	private Integer sseClientReadTimeout;

	@Value("${autobots.multiagent.sseClient.connectTimeout:1800}")
	private Integer sseClientConnectTimeout;

	@Value("${autobots.autoagent.genie_sop_prompt:}")
	private String genieSopPrompt;

    @Value("${autobots.autoagent.genie_base_prompt:}")
    private String genieBasePrompt;

    @Value("${autobots.autoagent.tool.task_complete_desc:当前task完成，请将当前task标记为 completed}")
    private String taskCompleteDesc;

    @Value("${server.ip:127.0.0.1}")
    private String serverIp;
    public String getServerIp() {
        return serverIp;
    }

    @Value("${server.port:8080}")
    private Integer serverPort;
    public Integer getServerPort() {
        return serverPort;
    }

}
