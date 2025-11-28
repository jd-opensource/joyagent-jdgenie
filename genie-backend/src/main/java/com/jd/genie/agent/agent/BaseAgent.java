package com.jd.genie.agent.agent;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.jd.genie.agent.dto.Memory;
import com.jd.genie.agent.dto.Message;
import com.jd.genie.agent.dto.tool.ToolCall;
import com.jd.genie.agent.enums.AgentState;
import com.jd.genie.agent.enums.RoleType;
import com.jd.genie.agent.llm.LLM;
import com.jd.genie.agent.printer.Printer;
import com.jd.genie.agent.tool.ToolCollection;
import com.jd.genie.agent.util.ThreadUtil;
import com.jd.genie.util.JacksonUtil;
import lombok.Data;
import lombok.experimental.Accessors;
import lombok.extern.slf4j.Slf4j;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;

/**
 * 代理基类 - 管理代理状态和执行的基础类
 */
@Slf4j
@Data
@Accessors(chain = true)
public abstract class BaseAgent {

    // 核心属性
    private String name;
    private String description;
    private String systemPrompt;
    private String nextStepPrompt;
    public ToolCollection availableTools = new ToolCollection();
    private Memory memory = new Memory();
    protected LLM llm;
    protected AgentContext context;

    // 执行控制
    private AgentState state = AgentState.IDLE;
    private int maxSteps = 10;
    private int currentStep = 0;
    private int duplicateThreshold = 2;

    // emitter
    Printer printer;

    // digital employee prompt
    private String digitalEmployeePrompt;

    /**
     * 执行单个步骤
     */
    public abstract String step();

    /**
     * 运行代理主循环
     */
    public String run(String query) {
        setState(AgentState.IDLE);

        if (!query.isEmpty()) {
            updateMemory(RoleType.USER, query, null);
        }

        List<String> results = new ArrayList<>();
        try {
            while (currentStep < maxSteps && state != AgentState.FINISHED) {
                currentStep++;
                log.info("{} {} Executing step {}/{}", context.getRequestId(), getName(), currentStep, maxSteps);
                String stepResult = step();
                results.add(stepResult);
            }

            if (currentStep >= maxSteps) {
                currentStep = 0;
                state = AgentState.IDLE;
                results.add("Terminated: Reached max steps (" + maxSteps + ")");
            }
        } catch (Exception e) {
            state = AgentState.ERROR;
            throw e;
        }

        return results.isEmpty() ? "No steps executed" : results.get(results.size() - 1);
    }

    /**
     * 更新代理记忆
     */
    public void updateMemory(RoleType role, String content, String base64Image, Object... args) {
        Message message;
        switch (role) {
            case USER:
                message = Message.userMessage(content, base64Image);
                break;
            case SYSTEM:
                message = Message.systemMessage(content, base64Image);
                break;
            case ASSISTANT:
                message = Message.assistantMessage(content, base64Image);
                break;
            case TOOL:
                message = Message.toolMessage(content, (String) args[0], base64Image);
                break;
            default:
                throw new IllegalArgumentException("Unsupported role type: " + role);
        }
        memory.addMessage(message);
    }

    public String executeTool(ToolCall command) {
        if (command == null || command.getFunction() == null || command.getFunction().getName() == null) {
            return "Error: Invalid function call format";
        }

        String name = command.getFunction().getName();
        try {
            // 解析参数
            ObjectMapper mapper = JacksonUtil.getObjectMapper();
            Object args = mapper.readValue(command.getFunction().getArguments(), Object.class);

            // 执行工具
            Object result = availableTools.execute(name, args);
            log.info("{} execute tool: {} {} result {}", context.getRequestId(), name, args, result);
            // 格式化结果
            if (Objects.nonNull(result)) {
                return (String) result;
            }
        } catch (Exception e) {
            log.error("{} execute tool {} failed ", context.getRequestId(), name, e);
        }
        return "Tool" + name + " Error.";
    }

    /**
     * 并发执行多个工具调用命令并返回执行结果
     *
     * @param commands 工具调用命令列表
     * @return 返回工具执行结果映射，key为工具ID，value为执行结果
     */
    public Map<String, String> executeTools(List<ToolCall> commands) {
        Map<String, String> result = new ConcurrentHashMap<>();
        CountDownLatch taskCount = ThreadUtil.getCountDownLatch(commands.size());
        for (ToolCall tooCall : commands) {
            ThreadUtil.execute(() -> {
                String toolResult = executeTool(tooCall);
                result.put(tooCall.getId(), toolResult);
                taskCount.countDown();
            });
        }
        ThreadUtil.await(taskCount);
        return result;
    }



}