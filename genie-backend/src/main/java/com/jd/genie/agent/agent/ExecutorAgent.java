package com.jd.genie.agent.agent;

import com.alibaba.fastjson.JSON;
import com.jd.genie.agent.dto.Message;
import com.jd.genie.agent.dto.tool.ToolCall;
import com.jd.genie.agent.dto.tool.ToolChoice;
import com.jd.genie.agent.enums.AgentState;
import com.jd.genie.agent.enums.RoleType;
import com.jd.genie.agent.llm.LLM;
import com.jd.genie.agent.prompt.ToolCallPrompt;
import com.jd.genie.agent.tool.BaseTool;
import com.jd.genie.agent.util.FileUtil;
import com.jd.genie.agent.util.SpringContextHolder;
import com.jd.genie.config.GenieConfig;
import com.jd.genie.model.response.AgentResponse;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.ApplicationContext;

import java.util.*;
import java.util.concurrent.CompletableFuture;

/**
 * 工具调用代理 - 处理工具/函数调用的基础代理类
 */
@Data
@Slf4j
@EqualsAndHashCode(callSuper = true)
public class ExecutorAgent extends ReActAgent {

    private List<ToolCall> toolCalls;
    private Integer maxObserve;
    private String systemPromptSnapshot;
    private String nextStepPromptSnapshot;

    private Integer taskId;

    public ExecutorAgent(AgentContext context) {
        setName("executor");
        setDescription("an agent that can execute tool calls.");
        ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
        GenieConfig genieConfig = applicationContext.getBean(GenieConfig.class);

        StringBuilder toolPrompt = new StringBuilder();
        for (BaseTool tool : context.getToolCollection().getToolMap().values()) {
            toolPrompt.append(String.format("工具名：%s 工具描述：%s\n", tool.getName(), tool.getDescription()));
        }

        String promptKey = "default";
        String sopPromptKey = "default";
        String nextPromptKey = "default";
        setSystemPrompt(genieConfig.getExecutorSystemPromptMap().getOrDefault(promptKey, ToolCallPrompt.SYSTEM_PROMPT)
                .replace("{{tools}}", toolPrompt.toString())
                .replace("{{query}}", context.getQuery())
                .replace("{{date}}", context.getDateInfo())
                .replace("{{sopPrompt}}", context.getSopPrompt())
                .replace("{{executorSopPrompt}}", genieConfig.getExecutorSopPromptMap().getOrDefault(sopPromptKey, "")));
        setNextStepPrompt(genieConfig.getExecutorNextStepPromptMap().getOrDefault(nextPromptKey, ToolCallPrompt.NEXT_STEP_PROMPT)
                .replace("{{tools}}", toolPrompt.toString())
                .replace("{{query}}", context.getQuery())
                .replace("{{date}}", context.getDateInfo())
                .replace("{{sopPrompt}}", context.getSopPrompt())
                .replace("{{executorSopPrompt}}", genieConfig.getExecutorSopPromptMap().getOrDefault(sopPromptKey, "")));

        setSystemPromptSnapshot(getSystemPrompt());
        setNextStepPromptSnapshot(getNextStepPrompt());

        setPrinter(context.printer);
        setMaxSteps(genieConfig.getPlannerMaxSteps());
        setLlm(new LLM(genieConfig.getExecutorModelName(), ""));

        setContext(context);
        setMaxObserve(Integer.parseInt(genieConfig.getMaxObserve()));

        // 初始化工具集合
        availableTools = context.getToolCollection();
        setDigitalEmployeePrompt(genieConfig.getDigitalEmployeePrompt());

        setTaskId(0);
    }

    @Override
    public boolean think() {
        // 获取文件内容
        String filesStr = FileUtil.formatFileInfo(context.getProductFiles(), true);
        setSystemPrompt(getSystemPromptSnapshot().replace("{{files}}", filesStr));
        setNextStepPrompt(getNextStepPromptSnapshot().replace("{{files}}", filesStr));

        if (!getMemory().getLastMessage().getRole().equals(RoleType.USER)) {
            Message userMsg = Message.userMessage(getNextStepPrompt(), null);
            getMemory().addMessage(userMsg);
        }

        try {
            // 获取带工具选项的响应
            log.info("{} executor ask tool {}", context.getRequestId(), JSON.toJSONString(availableTools));
            CompletableFuture<LLM.ToolCallResponse> future = getLlm().askTool(
                    context,
                    getMemory().getMessages(),
                    Message.systemMessage(getSystemPrompt(), null),
                    availableTools,
                    ToolChoice.AUTO, null, false, 300
            );

            LLM.ToolCallResponse response = future.get();
            setToolCalls(response.getToolCalls());

            // 记录响应信息
            if (response.getContent() != null && !response.getContent().trim().isEmpty()) {
                String thinkResult = response.getContent();
                String subType = "taskThought";
                if (toolCalls.isEmpty()) {
                    Map<String, Object> taskSummary = new HashMap<>();
                    taskSummary.put("taskSummary", response.getContent());
                    taskSummary.put("fileList", context.getTaskProductFiles());
                    thinkResult = JSON.toJSONString(taskSummary);
                    subType = "taskSummary";
                    printer.send("task_summary", taskSummary);
                } else {
                    printer.send("tool_thought", response.getContent());
                }

            }

            // 创建并添加助手消息
            Message assistantMsg = response.getToolCalls() != null && !response.getToolCalls().isEmpty() && !"struct_parse".equals(llm.getFunctionCallType()) ?
                    Message.fromToolCalls(response.getContent(), response.getToolCalls()) :
                    Message.assistantMessage(response.getContent(), null);
            getMemory().addMessage(assistantMsg);

        } catch (Exception e) {

            log.error("Oops! The " + getName() + "'s thinking process hit a snag: " + e.getMessage());
            getMemory().addMessage(Message.assistantMessage(
                    "Error encountered while processing: " + e.getMessage(), null));
            setState(AgentState.FINISHED);
            return false;
        }
        return true;
    }

    @Override
    public String act() {
        if (toolCalls.isEmpty()) {
            GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
            setState(AgentState.FINISHED);
            // 删除工具结果
            if ("1".equals(genieConfig.getClearToolMessage())) {
                getMemory().clearToolContext();
            }
            // 返回固定话术
            if (!genieConfig.getTaskCompleteDesc().isEmpty()) {
                return genieConfig.getTaskCompleteDesc();
            }
            return getMemory().getLastMessage().getContent();
        }

        Map<String, String> toolResults = executeTools(toolCalls);
        List<String> results = new ArrayList<>();
        for (ToolCall command : toolCalls) {
            String result = toolResults.get(command.getId());
            if (!Arrays.asList("code_interpreter_tool", "report_tool", "file_tool", "deep_search").contains(command.getFunction().getName())) {
                String toolName = command.getFunction().getName();
                printer.send("tool_result", AgentResponse.ToolResult.builder()
                                .toolName(toolName)
                                .toolParam(JSON.parseObject(command.getFunction().getArguments(), Map.class))
                                .toolResult(result)
                                .build(), null);
            }
            if (maxObserve != null) {
                result = result.substring(0, Math.min(result.length(), maxObserve));
            }

            // 添加工具响应到记忆
            if ("struct_parse".equals(llm.getFunctionCallType())) {
                String content = getMemory().getLastMessage().getContent();
                getMemory().getLastMessage().setContent(content + "\n 工具执行结果为:\n" + result);
            } else { // function_call
                Message toolMsg = Message.toolMessage(
                        result,
                        command.getId(),
                        null
                );
                getMemory().addMessage(toolMsg);
            }
            results.add(result);
        }
        return String.join("\n\n", results);
    }

    @Override
    public String run(String request) {
        generateDigitalEmployee(request);
        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        request = genieConfig.getTaskPrePrompt() + request;
        // 更新当前task
        context.setTask(request);
        return super.run(request);
    }

}