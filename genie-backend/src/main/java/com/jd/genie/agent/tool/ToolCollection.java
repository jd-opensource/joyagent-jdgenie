package com.jd.genie.agent.tool;

import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.dto.tool.McpToolInfo;
import com.jd.genie.agent.tool.mcp.McpTool;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;

import java.util.HashMap;
import java.util.Map;

/**
 * 工具集合类 - 管理可用的工具
 */
@Getter
@Setter
@Slf4j
public class ToolCollection {
    private Map<String, BaseTool> toolMap;
    private Map<String, McpToolInfo> mcpToolMap;
    private AgentContext agentContext;

    /**
     * 数字员工列表
     * task未并发的情况下
     * 1、每一个task，执行时，数字员工列表就会更新
     * TODO 并发情况下需要处理
     */
    private String currentTask;
    private JSONObject digitalEmployees;

    public ToolCollection() {
        this.toolMap = new HashMap<>();
        this.mcpToolMap = new HashMap<>();
    }

    /**
     * 添加工具
     */
    public void addTool(BaseTool tool) {
        toolMap.put(tool.getName(), tool);
    }

    /**
     * 获取工具
     */
    public BaseTool getTool(String name) {
        return toolMap.get(name);
    }

    /**
     * 添加MCP工具
     */
    public void addMcpTool(String name, String desc, String parameters, String mcpServerUrl) {
        mcpToolMap.put(name, McpToolInfo.builder()
                .name(name)
                .desc(desc)
                .parameters(parameters)
                .mcpServerUrl(mcpServerUrl)
                .build());
    }

    /**
     * 获取MCP工具
     */
    public McpToolInfo getMcpTool(String name) {
        return mcpToolMap.get(name);
    }


    /**
     * 执行工具
     */
    public Object execute(String name, Object toolInput) {
        if (toolMap.containsKey(name)) {
            BaseTool tool = getTool(name);
            return tool.execute(toolInput);
        } else if (mcpToolMap.containsKey(name)) {
            McpToolInfo toolInfo = mcpToolMap.get(name);
            McpTool mcpTool = new McpTool();
            mcpTool.setAgentContext(agentContext);
            return mcpTool.callTool(toolInfo.getMcpServerUrl(), name, toolInput);
        } else {
            log.error("Error: Unknown tool {}", name);
        }
        return null;
    }

    /**
     * 设置数字员工
     */
    public void updateDigitalEmployee(JSONObject digitalEmployee) {
        if (digitalEmployee == null) {
            log.error("requestId:{} setDigitalEmployee: {}", agentContext.getRequestId(), digitalEmployee);
        }
        setDigitalEmployees(digitalEmployee);
    }

    /**
     * 获取数字员工名称
     */
    public String getDigitalEmployee(String toolName) {
        if (StringUtils.isEmpty(toolName)) {
            return null;
        }

        if (digitalEmployees == null) {
            return null;
        }

        return (String) digitalEmployees.get(toolName);
    }
}