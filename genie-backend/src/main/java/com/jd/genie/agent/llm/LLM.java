package com.jd.genie.agent.llm;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.alibaba.fastjson.TypeReference;
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.dto.Message;
import com.jd.genie.agent.dto.tool.McpToolInfo;
import com.jd.genie.agent.dto.tool.ToolCall;
import com.jd.genie.agent.dto.tool.ToolChoice;
import com.jd.genie.agent.tool.BaseTool;
import com.jd.genie.agent.tool.ToolCollection;
import com.jd.genie.agent.util.SpringContextHolder;
import com.jd.genie.agent.util.StringUtil;
import com.jd.genie.config.GenieConfig;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.apache.commons.lang3.StringUtils;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * LLM 类
 */
@Slf4j
@Data
public class LLM {
    private static final Map<String, LLM> instances = new ConcurrentHashMap<>();

    private final String model;
    private final String llmErp;
    private final int maxTokens;
    private final double temperature;
    private final String apiKey;
    private final String baseUrl;
    private final String interfaceUrl;
    private final String functionCallType;
    private final TokenCounter tokenCounter;
    private final ObjectMapper objectMapper;
    private final Map<String, Object> extParams;

    private int totalInputTokens;
    private Integer maxInputTokens;

    public LLM(String modelName, String llmErp) {
        this.llmErp = llmErp;

        LLMSettings config = Config.getLLMConfig(modelName);
        this.model = config.getModel();
        this.maxTokens = config.getMaxTokens();
        this.temperature = config.getTemperature();
        this.apiKey = config.getApiKey();
        this.baseUrl = config.getBaseUrl();
        this.interfaceUrl = StringUtils.isNotEmpty(config.getInterfaceUrl()) ? config.getInterfaceUrl() : "/v1/chat/completions";
        this.functionCallType = config.getFunctionCallType();
        // 初始化 token 计数相关属性
        this.totalInputTokens = 0;
        this.maxInputTokens = config.getMaxInputTokens();
        this.extParams = config.getExtParams();

        // 初始化 tokenizer
        this.tokenCounter = new TokenCounter();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * 格式化消息
     */
    public static List<Map<String, Object>> formatMessages(List<Message> messages, boolean isClaude) {
        List<Map<String, Object>> formattedMessages = new ArrayList<>();

        for (Message message : messages) {
            Map<String, Object> messageMap = new HashMap<>();
            // 处理 base64 图像
            if (message.getBase64Image() != null && !message.getBase64Image().isEmpty()) {
                List<Map<String, Object>> multimodalContent = new ArrayList<>();
                // 创建内层的 image_url Map
                Map<String, String> imageUrlMap = new HashMap<>();
                imageUrlMap.put("url", "data:image/jpeg;base64," + message.getBase64Image());
                // 创建外层的 Map
                Map<String, Object> outerMap = new HashMap<>();
                outerMap.put("type", "image_url");
                outerMap.put("image_url", imageUrlMap);
                // 将创建好的 Map 添加到 multimodalContent 中
                multimodalContent.add(outerMap);

                Map<String, Object> contentMap = new HashMap<>();
                outerMap.put("type", "text");
                outerMap.put("text", message.getContent());
                multimodalContent.add(contentMap);

                messageMap.put("role", message.getRole().getValue());
                messageMap.put("content", multimodalContent);

            } else if (message.getToolCalls() != null && !message.getToolCalls().isEmpty()) {
                if (isClaude) {
                    // Claude格式的工具调用处理
                    messageMap.put("role", message.getRole().getValue());
                    List<Map<String, Object>> claudeToolCalls = new ArrayList<>();
                    for (ToolCall toolCall : message.getToolCalls()) {
                        Map<String, Object> claudeToolCall = new HashMap<>();
                        claudeToolCall.put("type", "tool_use");
                        claudeToolCall.put("id", toolCall.getId());
                        claudeToolCall.put("name", toolCall.getFunction().getName());
                        claudeToolCall.put("input", JSON.parseObject(toolCall.getFunction().getArguments()));
                        claudeToolCalls.add(claudeToolCall);
                    }
                    messageMap.put("content", claudeToolCalls);
                } else {
                    messageMap.put("role", message.getRole().getValue());
                    List<Map<String, Object>> toolCallsMap = JSON.parseObject(JSON.toJSONString(message.getToolCalls()),
                            new TypeReference<List<Map<String, Object>>>() {
                            });
                    messageMap.put("tool_calls", toolCallsMap);
                }
            } else if (message.getToolCallId() != null && !message.getToolCallId().isEmpty()) {
                // 敏感词过滤
                GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
                String content = StringUtil.textDesensitization(message.getContent(), genieConfig.getSensitivePatterns());
                if (isClaude) {
                    // Claude格式的工具调用结果处理
                    messageMap.put("role", "user");
                    List<Map<String, Object>> claudeToolCalls = new ArrayList<>();
                    Map<String, Object> claudeToolCall = new HashMap<>();
                    claudeToolCall.put("type", "tool_result");
                    claudeToolCall.put("tool_use_id", message.getToolCallId());
                    claudeToolCall.put("content", content);
                    claudeToolCalls.add(claudeToolCall);
                    messageMap.put("content", claudeToolCalls);
                } else {
                    messageMap.put("role", message.getRole().getValue());
                    messageMap.put("content", content);
                    messageMap.put("tool_call_id", message.getToolCallId());
                }
            } else {
                messageMap.put("role", message.getRole().getValue());
                messageMap.put("content", message.getContent());
            }

            formattedMessages.add(messageMap);
        }

        return formattedMessages;
    }

    public List<Map<String, Object>> truncateMessage(AgentContext context, List<Map<String, Object>> messages, int maxInputTokens) {
        if (messages.isEmpty() || maxInputTokens < 0) {
            return messages;
        }
        log.info("{} before truncate {}", context.getRequestId(), JSON.toJSONString(messages));
        List<Map<String, Object>> truncatedMessages = new ArrayList<>();
        int remainingTokens = maxInputTokens;
        Map<String, Object> system = messages.get(0);
        if ("system".equals(system.getOrDefault("role", ""))) {
            remainingTokens -= tokenCounter.countMessageTokens(system);
        }

        for (int i = messages.size() - 1; i >= 0; i--) {
            Map<String, Object> message = messages.get(i);
            int messageToken = tokenCounter.countMessageTokens(message);
            if (remainingTokens >= messageToken) {
                truncatedMessages.add(0, message);
                remainingTokens -= messageToken;
            } else {
                break;
            }
        }
        // use assistant 保证完整性
        Iterator<Map<String, Object>> iterator = truncatedMessages.iterator();
        while (iterator.hasNext()) {
            Map<String, Object> message = iterator.next();
            if (!"user".equals(message.getOrDefault("role", ""))) {
                iterator.remove(); // 安全删除当前元素
            } else {
                break;
            }
        }

        if ("system".equals(system.getOrDefault("role", ""))) {
            truncatedMessages.add(0, system);
        }
        log.info("{} after truncate {}", context.getRequestId(), JSON.toJSONString(truncatedMessages));

        return truncatedMessages;
    }

    /**
     * 向 LLM 发送请求并获取响应
     */
    public CompletableFuture<String> ask(
            AgentContext context,
            List<Message> messages,
            List<Message> systemMsgs,
            boolean stream,
            Double temperature
    ) {
        try {
            List<Map<String, Object>> formattedMessages;
            // 格式化系统和用户消息
            if (systemMsgs != null && !systemMsgs.isEmpty()) {
                List<Map<String, Object>> formattedSystemMsgs = formatMessages(systemMsgs, false);
                formattedMessages = new ArrayList<>(formattedSystemMsgs);
                formattedMessages.addAll(formatMessages(messages, model.contains("claude")));
            } else {
                formattedMessages = formatMessages(messages, model.contains("claude"));
            }

            // 准备请求参数
            Map<String, Object> params = new HashMap<>();
            params.put("model", model);
            if (StringUtils.isNotEmpty(llmErp)) {
                params.put("erp", llmErp);
            }
            params.put("messages", formattedMessages);

            // 根据模型设置不同的参数
            params.put("max_tokens", maxTokens);
            params.put("temperature", temperature != null ? temperature : this.temperature);
            if (Objects.nonNull(extParams)) {
                params.putAll(extParams);
            }

            log.info("{} call llm ask request {}", context.getRequestId(), JSONObject.toJSONString(params));
            // 处理非流式请求
            if (!stream) {
                params.put("stream", false);

                // 调用 API
                CompletableFuture<String> future = callOpenAI(params);

                return future.thenApply(response -> {
                    try {
                        // 解析响应
                        log.info("{} call llm response {}", context.getRequestId(), response);
                        JsonNode jsonResponse = objectMapper.readTree(response);
                        JsonNode choices = jsonResponse.get("choices");

                        if (choices == null || choices.isEmpty() || choices.get(0).get("message").get("content") == null) {
                            throw new IllegalArgumentException("Empty or invalid response from LLM");
                        }

                        return choices.get(0).get("message").get("content").asText();
                    } catch (IOException e) {
                        throw new CompletionException(e);
                    }
                });
            } else {
                // 处理流式请求
                params.put("stream", true);
                // 调用流式 API
                return callOpenAIStream(params);
            }
        } catch (Exception e) {
            log.error("{} Unexpected error in ask: {}", e.getMessage(), e);
            CompletableFuture<String> future = new CompletableFuture<>();
            future.completeExceptionally(e);
            return future;
        }
    }

    public <T> T deepCopy(T original) {
        try {
            // 序列化为 JSON 字节数组
            byte[] jsonBytes = objectMapper.writeValueAsBytes(original);

            // 从 JSON 反序列化为新对象
            return objectMapper.readValue(jsonBytes,
                    objectMapper.getTypeFactory().constructType(original.getClass()));
        } catch (Exception e) {
            throw new RuntimeException("深拷贝失败", e);
        }
    }


    /**
     * 将OpenAI GPT工具定义转换为Claude工具格式
     *
     * @param gptTools OpenAI GPT格式的工具定义列表
     * @return Claude格式的工具定义列表
     */
    public List<Map<String, Object>> gptToClaudeTool(List<Map<String, Object>> gptTools) {
        List<Map<String, Object>> newGptTools = deepCopy(gptTools);
        List<Map<String, Object>> claudeTools = new ArrayList<>();
        for (Map<String, Object> gptToolWrapper : newGptTools) {
            // 提取function对象
            Map<String, Object> gptTool = (Map<String, Object>) gptToolWrapper.get("function");
            Map<String, Object> claudeTool = new HashMap<>();
            claudeTool.put("name", gptTool.get("name"));
            claudeTool.put("description", gptTool.get("description"));
            // parameters
            Map<String, Object> parameters = (Map<String, Object>) gptTool.get("parameters");
            // require
            ArrayList<String> newRequired = new ArrayList<>();
            newRequired.add("function_name");
            if (parameters.containsKey("required") && Objects.nonNull(parameters.get("required"))) {
                newRequired.addAll((List<String>) parameters.get("required"));
            }
            parameters.put("required", newRequired);
            // properties
            Map<String, Object> newProperties = new HashMap<>();
            Map<String, Object> functionNameMap = new HashMap<>();
            functionNameMap.put("description", "默认值为工具名: " + gptTool.get("name"));
            functionNameMap.put("type", "string");
            newProperties.put("function_name", functionNameMap);
            if (parameters.containsKey("properties") && Objects.nonNull(parameters.get("properties"))) {
                newProperties.putAll((Map<String, Object>) parameters.get("properties"));
            }
            parameters.put("properties", newProperties);

            // 提取参数结构
            claudeTool.put("input_schema", gptTool.get("parameters"));
            claudeTools.add(claudeTool);
        }
        return claudeTools;
    }


    private Map<String, Object> addFunctionNameParam(Map<String, Object> parameters, String toolName) {
        Map<String, Object> newParameters = deepCopy(parameters);
        // require
        ArrayList<String> newRequired = new ArrayList<>();
        newRequired.add("function_name");
        if (parameters.containsKey("required") && Objects.nonNull(parameters.get("required"))) {
            newRequired.addAll((List<String>) parameters.get("required"));
        }
        newParameters.put("required", newRequired);

        // properties
        Map<String, Object> newProperties = new HashMap<>();
        Map<String, Object> functionNameMap = new HashMap<>();
        functionNameMap.put("description", "默认值为工具名: " + toolName);
        functionNameMap.put("type", "string");
        newProperties.put("function_name", functionNameMap);
        if (parameters.containsKey("properties") && Objects.nonNull(parameters.get("properties"))) {
            newProperties.putAll((Map<String, Object>) parameters.get("properties"));
        }
        newParameters.put("properties", newProperties);
        return newParameters;
    }

    /**
     * 向 LLM 发送工具请求并获取响应
     */
    public CompletableFuture<ToolCallResponse> askTool(
            AgentContext context,
            List<Message> messages,
            Message systemMsgs,
            ToolCollection tools,
            ToolChoice toolChoice,
            Double temperature,
            boolean stream,
            int timeout
    ) {
        try {
            // 验证 toolChoice
            if (!ToolChoice.isValid(toolChoice)) {
                throw new IllegalArgumentException("Invalid tool_choice: " + toolChoice);
            }
            long startTime = System.currentTimeMillis();

            // 设置 API 请求
            Map<String, Object> params = new HashMap<>();

            // tools
            StringBuilder stringBuilder = new StringBuilder();
            List<Map<String, Object>> formattedTools = new ArrayList<>();
            if ("struct_parse".equals(functionCallType)) {
                GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
                stringBuilder.append(genieConfig.getStructParseToolSystemPrompt());
                // base tool
                for (BaseTool tool : tools.getToolMap().values()) {
                    Map<String, Object> functionMap = new HashMap<>();
                    functionMap.put("name", tool.getName());
                    functionMap.put("description", tool.getDescription());
                    functionMap.put("parameters", addFunctionNameParam(tool.toParams(), tool.getName()));
                    stringBuilder.append(String.format("- `%s`\n```json %s ```\n", tool.getName(), JSON.toJSONString(functionMap)));
                }
                // mcp tool
                for (McpToolInfo tool : tools.getMcpToolMap().values()) {
                    Map<String, Object> parameters = JSON.parseObject(tool.getParameters(), new TypeReference<Map<String, Object>>() {});
                    Map<String, Object> functionMap = new HashMap<>();
                    functionMap.put("name", tool.getName());
                    functionMap.put("description", tool.getDesc());
                    functionMap.put("parameters", addFunctionNameParam(parameters, tool.getName()));
                    stringBuilder.append(String.format("- `%s`\n```json %s ```\n", tool.getName(), JSON.toJSONString(functionMap)));
                }

            } else { // function_call
                // base tool
                for (BaseTool tool : tools.getToolMap().values()) {
                    Map<String, Object> functionMap = new HashMap<>();
                    functionMap.put("name", tool.getName());
                    functionMap.put("description", tool.getDescription());
                    functionMap.put("parameters", tool.toParams());
                    Map<String, Object> toolMap = new HashMap<>();
                    toolMap.put("type", "function");
                    toolMap.put("function", functionMap);
                    formattedTools.add(toolMap);
                }
                // mcp tool
                for (McpToolInfo tool : tools.getMcpToolMap().values()) {
                    Map<String, Object> parameters = JSON.parseObject(tool.getParameters(), new TypeReference<Map<String, Object>>() {});
                    Map<String, Object> functionMap = new HashMap<>();
                    functionMap.put("name", tool.getName());
                    functionMap.put("description", tool.getDesc());
                    functionMap.put("parameters", parameters);
                    Map<String, Object> toolMap = new HashMap<>();
                    toolMap.put("type", "function");
                    toolMap.put("function", functionMap);
                    formattedTools.add(toolMap);
                }

                if (model.contains("claude")) {
                    formattedTools = gptToClaudeTool(formattedTools);
                }
            }

            // 格式化消息
            List<Map<String, Object>> formattedMessages = new ArrayList<>();
            if (Objects.nonNull(systemMsgs)) {
                if ("struct_parse".equals(functionCallType)) {
                    systemMsgs.setContent(systemMsgs.getContent() + "\n" + stringBuilder);
                }
                if (model.contains("claude")) {
                    params.put("system", systemMsgs.getContent());
                } else {
                    formattedMessages.addAll(formatMessages(List.of(systemMsgs), model.contains("claude")));
                }
            }
            formattedMessages.addAll(formatMessages(messages, model.contains("claude")));

            params.put("model", model);
            if (StringUtils.isNotEmpty(llmErp)) {
                params.put("erp", llmErp);
            }
            params.put("messages", formattedMessages);

            if (!"struct_parse".equals(functionCallType)) {
                params.put("tools", formattedTools);
                params.put("tool_choice", toolChoice.getValue());
            }

            // 添加模型特定参数
            params.put("max_tokens", maxTokens);
            params.put("temperature", temperature != null ? temperature : this.temperature);
            if (Objects.nonNull(extParams)) {
                params.putAll(extParams);
            }

            log.info("{} call llm request {}", context.getRequestId(), JSONObject.toJSONString(params));
            if (!stream) {
                params.put("stream", false);
                // 调用 API
                CompletableFuture<String> future = callOpenAI(params, timeout);
                return future.thenApply(responseJson -> {
                    try {
                        // 解析响应
                        log.info("{} call llm response {}", context.getRequestId(), responseJson);
                        JsonNode jsonResponse = objectMapper.readTree(responseJson);
                        JsonNode choices = jsonResponse.get("choices");

                        if (choices == null || choices.isEmpty() || choices.get(0).get("message") == null) {
                            log.error("{} Invalid response: {}", context.getRequestId(), responseJson);
                            throw new IllegalArgumentException("Invalid or empty response from LLM");
                        }

                        // 提取响应内容
                        JsonNode message = choices.get(0).get("message");
                        String content = message.has("content") && !"null".equals(message.get("content").asText()) ? message.get("content").asText() : null;

                        // 提取工具调用
                        List<ToolCall> toolCalls = new ArrayList<>();
                        if ("struct_parse".equals(functionCallType)) {
                            // 匹配方式: 直接匹配 ```json ... ``` 代码块
                            String pattern = "```json\\s*([\\s\\S]*?)\\s*```";
                            List<String> matches = findMatches(content, pattern);
                            if (!matches.isEmpty()) {
                                for (String match : matches) {
                                    ToolCall oneToolCall = parseToolCall(context, match);
                                    if (Objects.nonNull(oneToolCall)) {
                                        toolCalls.add(oneToolCall);
                                    }
                                }
                            }
                            int stopPos = content.indexOf("```json");
                            content = content.substring(0, stopPos > 0 ? stopPos : content.length());
                        } else { // function call
                            if (message.has("tool_calls")) {
                                JsonNode toolCallsNode = message.get("tool_calls");
                                for (JsonNode toolCall : toolCallsNode) {
                                    String id = toolCall.get("id").asText();
                                    String type = toolCall.get("type").asText();

                                    // 提取函数信息
                                    JsonNode functionNode = toolCall.get("function");
                                    String name = functionNode.get("name").asText();
                                    String arguments = functionNode.get("arguments").asText();
                                    toolCalls.add(new ToolCall(id, type, new ToolCall.Function(name, arguments)));
                                }
                            }
                        }
                        // 提取其他信息
                        String finishReason = choices.get(0).get("finish_reason").asText();
                        int totalTokens = jsonResponse.get("usage").get("total_tokens").asInt();

                        long endTime = System.currentTimeMillis();
                        long duration = endTime - startTime;
                        return new ToolCallResponse(content, toolCalls, finishReason, totalTokens, duration);
                    } catch (IOException e) {
                        throw new CompletionException(e);
                    }
                });
            } else {
                // 处理流式请求
                params.put("stream", true);

                if (model.contains("claude")) {
                    return callClaudeFunctionCallStream(context, params);
                }
                // 调用流式 API
                return callOpenAIFunctionCallStream(context, params);
            }

        } catch (Exception e) {
            log.error("{} Unexpected error in askTool: {}", context.getRequestId(), e.getMessage(), e);
            CompletableFuture<ToolCallResponse> future = new CompletableFuture<>();
            future.completeExceptionally(e);
            return future;
        }
    }

    /**
     * 调用 OpenAI API（抽象方法，实际实现需要在子类中提供）
     */
    protected CompletableFuture<String> callOpenAI(Map<String, Object> params) {
        return callOpenAI(params, 300); // 默认超时时间为 300 秒
    }

    /**
     * 调用 OpenAI API（抽象方法，实际实现需要在子类中提供）
     */
    protected CompletableFuture<String> callOpenAI(Map<String, Object> params, int timeout) {
        CompletableFuture<String> future = new CompletableFuture<>();

        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(timeout, TimeUnit.SECONDS)
                    .readTimeout(timeout, TimeUnit.SECONDS)
                    .writeTimeout(timeout, TimeUnit.SECONDS)
                    .build();

            String apiEndpoint = baseUrl + interfaceUrl;

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    objectMapper.writeValueAsString(params)
            );

            Request.Builder requestBuilder = new Request.Builder()
                    .url(apiEndpoint)
                    .post(body);

            // 添加适当的认证头
            requestBuilder.addHeader("Authorization", "Bearer " + apiKey);

            Request request = requestBuilder.build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    try (ResponseBody responseBody = response.body()) {
                        if (!response.isSuccessful()) {
                            future.completeExceptionally(
                                    new IOException("Unexpected response code: " + response)
                            );
                        } else {
                            future.complete(responseBody.string());
                        }
                    }
                }
            });
        } catch (Exception e) {
            future.completeExceptionally(e);
        }

        return future;
    }

    /**
     * 调用 OpenAI 流式 API（抽象方法，实际实现需要在子类中提供）
     */
    public CompletableFuture<ToolCallResponse> callOpenAIFunctionCallStream(AgentContext context, Map<String, Object> params) {
        CompletableFuture<ToolCallResponse> future = new CompletableFuture<>();
        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(300, TimeUnit.SECONDS)
                    .readTimeout(300, TimeUnit.SECONDS)
                    .writeTimeout(300, TimeUnit.SECONDS)
                    .build();

            String apiEndpoint = baseUrl + interfaceUrl;
            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    objectMapper.writeValueAsString(params)
            );
            Request.Builder requestBuilder = new Request.Builder()
                    .url(apiEndpoint)
                    .post(body);
            // 添加适当的认证头
            requestBuilder.addHeader("Authorization", "Bearer " + apiKey);
            Request request = requestBuilder.build();

            GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
            String[] interval = genieConfig.getMessageInterval().getOrDefault("llm", "1,3").split(",");
            int firstInterval = "struct_parse".equals(functionCallType) ? Math.max(3, Integer.parseInt(interval[0])) : Integer.parseInt(interval[0]);
            int sendInterval = Integer.parseInt(interval[1]);

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) {
                    boolean isFirstToken = true;
                    boolean isContent = true;
                    try (ResponseBody responseBody = response.body()) {
                        if (!response.isSuccessful() || responseBody == null) {
                            log.error("{} ask tool stream response error or empty", context.getRequestId());
                            future.completeExceptionally(new IOException("Unexpected response code: " + response));
                            return;
                        }

                        String messageId = StringUtil.getUUID();
                        StringBuilder stringBuilder = new StringBuilder();
                        StringBuilder stringBuilderAll = new StringBuilder();
                        int index = 1;
                        Map<Integer, OpenAIToolCall> openToolCallsMap = new HashMap<>();
                        String line;
                        BufferedReader reader = new BufferedReader(
                                new InputStreamReader(responseBody.byteStream())
                        );
                        while ((line = reader.readLine()) != null) {
                            if (line.startsWith("data: ")) {
                                String data = line.substring(6);
                                if (data.equals("[DONE]")) {
                                    break;
                                }
                                if (isFirstToken) {
                                    isFirstToken = false;
                                }
                                try {
                                    JsonNode chunk = objectMapper.readTree(data);
                                    if (chunk.has("choices") && !chunk.get("choices").isEmpty()) {
                                        for (JsonNode element : chunk.get("choices")) {
                                            OpenAIChoice choice = objectMapper.convertValue(element, OpenAIChoice.class);
                                            // content
                                            if (Objects.nonNull(choice.delta.content)) {
                                                String content = choice.delta.content;
                                                // log.info("{} recv content data: >>{}<<", context.getRequestId(), content);
                                                if (!isContent) { // 忽略json内容
                                                    stringBuilderAll.append(content);
                                                    continue;
                                                }
                                                stringBuilder.append(content);
                                                stringBuilderAll.append(content);
                                                if ("struct_parse".equals(functionCallType)) {
                                                    if (stringBuilderAll.toString().contains("```json")) {
                                                        isContent = false;
                                                    }
                                                }
                                                if (index == firstInterval || index % sendInterval == 0) {
                                                    context.getPrinter().send(messageId, context.getStreamMessageType(), stringBuilder.toString(), false);
                                                    stringBuilder.setLength(0);
                                                }
                                                index++;
                                            }
                                            // tool call
                                            if (Objects.nonNull(choice.delta.tool_calls)) {
                                                List<OpenAIToolCall> openAIToolCalls = choice.delta.tool_calls;
                                                // log.info("{} recv tool call data: {}", context.getRequestId(), openAIToolCalls);
                                                for (OpenAIToolCall toolCall : openAIToolCalls) {
                                                    OpenAIToolCall currentToolCall = openToolCallsMap.get(toolCall.index);
                                                    if (Objects.isNull(currentToolCall)) {
                                                        currentToolCall = new OpenAIToolCall();
                                                        currentToolCall.function = new OpenAIFunction();
                                                        currentToolCall.function.arguments = "";
                                                    }
                                                    // [{"index":0,"id":"call_j74R8JMFWTC4rW5wHJ0TtmNU","type":"function","function":{"name":"planning","arguments":""}}]
                                                    if (Objects.nonNull(toolCall.id)) {
                                                        currentToolCall.id = toolCall.id;
                                                    }
                                                    if (Objects.nonNull(toolCall.type)) {
                                                        currentToolCall.type = toolCall.type;
                                                    }
                                                    if (Objects.nonNull(toolCall.function)) {
                                                        if (Objects.nonNull(toolCall.function.name)) {
                                                            currentToolCall.function.name = toolCall.function.name;
                                                        }
                                                        if (Objects.nonNull(toolCall.function.arguments)) {
                                                            currentToolCall.function.arguments += toolCall.function.arguments;
                                                        }
                                                    }
                                                    openToolCallsMap.put(toolCall.index, currentToolCall);
                                                }
                                            }
                                        }
                                    }
                                } catch (Exception e) {
                                    log.error("{} process response error", context.getRequestId(), e);
                                }
                            }
                        }

                        String contentAll = stringBuilderAll.toString();
                        if ("struct_parse".equals(functionCallType)) {
                            int stopPos = stringBuilder.indexOf("```json");
                            context.getPrinter().send(messageId, context.getStreamMessageType(),
                                    stringBuilder.substring(0, stopPos >= 0 ? stopPos : stringBuilder.length()),
                                    false);
                            stopPos = stringBuilderAll.indexOf("```json");
                            contentAll = stringBuilderAll.substring(0, stopPos >= 0 ? stopPos : stringBuilderAll.length());
                            if (!contentAll.isEmpty()) {
                                context.getPrinter().send(messageId, context.getStreamMessageType(), contentAll, true);
                            }
                        } else { // function_call
                            if (!contentAll.isEmpty()) {
                                context.getPrinter().send(messageId, context.getStreamMessageType(), stringBuilder.toString(), false);
                                context.getPrinter().send(messageId, context.getStreamMessageType(), stringBuilderAll.toString(), true);
                            }
                        }

                        List<ToolCall> toolCalls = new ArrayList<>();
                        if ("struct_parse".equals(functionCallType)) {
                            // 匹配方式: 直接匹配 ```json ... ``` 代码块
                            String pattern = "```json\\s*([\\s\\S]*?)\\s*```";
                            List<String> matches = findMatches(stringBuilderAll.toString(), pattern);
                            if (!matches.isEmpty()) {
                                for (String match : matches) {
                                    ToolCall oneToolCall = parseToolCall(context, match);
                                    if (Objects.nonNull(oneToolCall)) {
                                        toolCalls.add(oneToolCall);
                                    }
                                }
                            }
                        } else { // function call
                            for (OpenAIToolCall toolCall : openToolCallsMap.values()) {
                                toolCalls.add(ToolCall.builder()
                                        .id(toolCall.id)
                                        .type(toolCall.type)
                                        .function(ToolCall.Function.builder()
                                                .name(toolCall.function.name)
                                                .arguments(toolCall.function.arguments)
                                                .build())
                                        .build());
                            }
                        }

                        log.info("{} call llm stream response {} {}", context.getRequestId(), stringBuilderAll, JSON.toJSONString(toolCalls));

                        ToolCallResponse fullResponse = ToolCallResponse.builder()
                                .toolCalls(toolCalls)
                                .content(contentAll)
                                .build();
                        future.complete(fullResponse);

                    } catch (Exception e) {
                        log.error("{} ask tool stream error", context.getRequestId(), e);
                        future.completeExceptionally(e);
                    }
                }
            });

        } catch (Exception e) {
            log.error("{} ask tool stream error", context.getRequestId(), e);
            future.completeExceptionally(e);
        }

        return future;
    }

    /**
     * 调用 OpenAI 流式 API（抽象方法，实际实现需要在子类中提供）
     */
    public CompletableFuture<ToolCallResponse> callClaudeFunctionCallStream(AgentContext context, Map<String, Object> params) {
        CompletableFuture<ToolCallResponse> future = new CompletableFuture<>();
        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(300, TimeUnit.SECONDS)
                    .readTimeout(300, TimeUnit.SECONDS)
                    .writeTimeout(300, TimeUnit.SECONDS)
                    .build();

            String apiEndpoint = baseUrl + interfaceUrl;
            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    objectMapper.writeValueAsString(params)
            );
            Request.Builder requestBuilder = new Request.Builder()
                    .url(apiEndpoint)
                    .post(body);
            // 添加适当的认证头
            requestBuilder.addHeader("Authorization", "Bearer " + apiKey);
            Request request = requestBuilder.build();

            GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
            String[] interval = genieConfig.getMessageInterval().getOrDefault("llm", "1,3").split(",");
            int firstInterval = "struct_parse".equals(functionCallType) ? Math.max(3, Integer.parseInt(interval[0])) : Integer.parseInt(interval[0]);
            int sendInterval = Integer.parseInt(interval[1]);

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) {
                    boolean isFirstToken = true;
                    boolean isContent = true;
                    try (ResponseBody responseBody = response.body()) {
                        if (!response.isSuccessful() || responseBody == null) {
                            log.error("{} ask tool stream response error or empty", context.getRequestId());
                            future.completeExceptionally(new IOException("Unexpected response code: " + response));
                            return;
                        }

                        String messageId = StringUtil.getUUID();
                        StringBuilder stringBuilder = new StringBuilder();
                        StringBuilder stringBuilderAll = new StringBuilder();
                        StringBuilder stringBuilderTool = new StringBuilder();

                        Integer index = 1;
                        Map<Integer, OpenAIToolCall> openToolCallsMap = new HashMap<>();
                        String line;
                        BufferedReader reader = new BufferedReader(
                                new InputStreamReader(responseBody.byteStream())
                        );
                        String id = "";
                        while ((line = reader.readLine()) != null) {
                            if (line.startsWith("data: ")) {
                                String data = line.substring(6);
                                if (data.equals("[DONE]")) {
                                    break;
                                }

                                try {
                                    // log.info("{} recv data: >>{}<<", context.getRequestId(), data);
                                    JsonNode chunk = objectMapper.readTree(data);
                                    ClaudeResponse claudeResponse = objectMapper.convertValue(chunk, ClaudeResponse.class);

                                    if (Objects.isNull(claudeResponse.delta)) {
                                        continue;
                                    }

                                    if (isFirstToken) {
                                        isFirstToken = false;
                                    }

                                    // content
                                    if ("text_delta".equals(claudeResponse.delta.type)) {
                                        String content = claudeResponse.delta.text;

                                        if (!isContent) { // 忽略json内容
                                            stringBuilderAll.append(content);
                                            continue;
                                        }
                                        // log.info("{} recv content data: >>{}<<", context.getRequestId(), content);
                                        stringBuilder.append(content);
                                        stringBuilderAll.append(content);
                                        if ("struct_parse".equals(functionCallType)) {
                                            if (stringBuilderAll.toString().contains("```json")) {
                                                isContent = false;
                                            }
                                        }
                                        if (index == firstInterval || index % sendInterval == 0) {
                                            context.getPrinter().send(messageId, context.getStreamMessageType(), stringBuilder.toString(), false);
                                            stringBuilder.setLength(0);
                                        }
                                        index++;
                                    }
                                    // tool call
                                    if ("input_json_delta".equals(claudeResponse.delta.type)) {
                                        String content = claudeResponse.delta.partial_json;
                                        // log.info("{} recv tool call data: >>{}<<", context.getRequestId(), content);
                                        stringBuilderTool.append(content);
                                    }
                                    // id
                                    id = claudeResponse.id;

                                } catch (Exception e) {
                                    log.error("{} process response error", context.getRequestId(), e);
                                }
                            }
                        }

                        String contentAll = stringBuilderAll.toString();
                        if ("struct_parse".equals(functionCallType)) {
                            int stopPos = stringBuilder.indexOf("```json");
                            context.getPrinter().send(messageId, context.getStreamMessageType(),
                                    stringBuilder.substring(0, stopPos >= 0 ? stopPos : stringBuilder.length()),
                                    false);
                            stopPos = stringBuilderAll.indexOf("```json");
                            contentAll = stringBuilderAll.substring(0, stopPos >= 0 ? stopPos : stringBuilderAll.length());
                            if (!contentAll.isEmpty()) {
                                context.getPrinter().send(messageId, context.getStreamMessageType(), contentAll, true);
                            }
                        } else { // function call
                            if (!contentAll.isEmpty()) {
                                context.getPrinter().send(messageId, context.getStreamMessageType(), stringBuilder.toString(), false);
                                context.getPrinter().send(messageId, context.getStreamMessageType(), stringBuilderAll.toString(), true);
                            }
                        }
                        List<ToolCall> toolCalls = new ArrayList<>();
                        if ("struct_parse".equals(functionCallType)) {
                            // 匹配方式: 直接匹配 ```json ... ``` 代码块
                            String pattern = "```json\\s*([\\s\\S]*?)\\s*```";
                            List<String> matches = findMatches(stringBuilderAll.toString(), pattern);
                            if (!matches.isEmpty()) {
                                for (String match : matches) {
                                    ToolCall oneToolCall = parseToolCall(context, match);
                                    if (Objects.nonNull(oneToolCall)) {
                                        toolCalls.add(oneToolCall);
                                    }
                                }
                            }
                        } else { // function_call
                            JsonNode arguments = objectMapper.readTree(stringBuilderTool.toString());
                            if (!stringBuilderTool.toString().isEmpty() && arguments.hasNonNull("function_name")) {
                                OpenAIToolCall currentToolCall = new OpenAIToolCall();
                                currentToolCall.id = id;
                                currentToolCall.type = "function";
                                currentToolCall.function = new OpenAIFunction();
                                currentToolCall.function.name = arguments.get("function_name").asText();
                                currentToolCall.function.arguments = stringBuilderTool.toString();
                                openToolCallsMap.put(0, currentToolCall); // claude only call one function
                                for (OpenAIToolCall toolCall : openToolCallsMap.values()) {
                                    toolCalls.add(ToolCall.builder()
                                            .id(toolCall.id)
                                            .type(toolCall.type)
                                            .function(ToolCall.Function.builder()
                                                    .name(toolCall.function.name)
                                                    .arguments(toolCall.function.arguments)
                                                    .build())
                                            .build());
                                }
                            }
                        }

                        log.info("{} call llm stream response {} tool calls {}", context.getRequestId(), stringBuilderAll, JSON.toJSONString(toolCalls));

                        future.complete(ToolCallResponse.builder()
                                .content(contentAll)
                                .toolCalls(toolCalls)
                                .build());

                    } catch (Exception e) {
                        log.error("{} ask tool stream error", context.getRequestId(), e);
                        future.completeExceptionally(e);
                    }
                }
            });

        } catch (Exception e) {
            log.error("{} ask tool stream error", context.getRequestId(), e);
            future.completeExceptionally(e);
        }

        return future;
    }

    /**
     * 调用 OpenAI 流式 API（抽象方法，实际实现需要在子类中提供）
     */
    protected CompletableFuture<String> callOpenAIStream(Map<String, Object> params) {
        // 这里是一个简化的流式请求实现示例
        CompletableFuture<String> future = new CompletableFuture<>();
        StringBuilder collectedMessages = new StringBuilder();

        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(300, TimeUnit.SECONDS)
                    .readTimeout(300, TimeUnit.SECONDS)
                    .writeTimeout(300, TimeUnit.SECONDS)
                    .build();

            String apiEndpoint = baseUrl + interfaceUrl;

            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    objectMapper.writeValueAsString(params)
            );

            Request.Builder requestBuilder = new Request.Builder()
                    .url(apiEndpoint)
                    .post(body);

            // 添加适当的认证头
            requestBuilder.addHeader("Authorization", "Bearer " + apiKey);

            Request request = requestBuilder.build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) throws IOException {
                    try (ResponseBody responseBody = response.body()) {
                        if (!response.isSuccessful()) {
                            future.completeExceptionally(
                                    new IOException("Unexpected response code: " + response)
                            );
                            return;
                        }

                        if (responseBody != null) {
                            String line;

                            BufferedReader reader = new BufferedReader(
                                    new InputStreamReader(responseBody.byteStream())
                            );

                            while ((line = reader.readLine()) != null) {
                                if (line.startsWith("data: ")) {
                                    String data = line.substring(6);
                                    if (data.equals("[DONE]")) {
                                        break;
                                    }

                                    try {
                                        JsonNode chunk = objectMapper.readTree(data);
                                        if (chunk.has("choices") && !chunk.get("choices").isEmpty()) {
                                            JsonNode choice = chunk.get("choices").get(0);
                                            if (choice.has("delta") && choice.get("delta").has("content")) {
                                                String content = choice.get("delta").get("content").asText();
                                                collectedMessages.append(content);
                                                log.info("recv data: {}", content);
                                            }
                                        }
                                    } catch (Exception e) {
                                        // 忽略非 JSON 数据
                                    }
                                }
                            }

                            String fullResponse = collectedMessages.toString().trim();

                            if (fullResponse.isEmpty()) {
                                future.completeExceptionally(
                                        new IllegalArgumentException("Empty response from streaming LLM")
                                );
                            } else {
                                future.complete(fullResponse);
                            }
                        } else {
                            future.completeExceptionally(
                                    new IOException("Empty response body")
                            );
                        }
                    }
                }
            });
        } catch (Exception e) {
            future.completeExceptionally(e);
        }

        return future;
    }


    /**
     * 查找匹配的工具调用
     */
    private List<String> findMatches(String text, String pattern) {
        Pattern r = Pattern.compile(pattern);
        Matcher m = r.matcher(text);
        List<String> matches = new ArrayList<>();
        while (m.find()) {
            matches.add(m.group(1));
        }
        return matches;
    }

    /**
     * 解析工具调用JSON
     */
    private ToolCall parseToolCall(AgentContext context, String jsonContent) {
        try {
            JSONObject jsonObj = JSON.parseObject(jsonContent);
            String toolName = jsonObj.getString("function_name");
            jsonObj.remove("function_name");
            return ToolCall.builder()
                    .id(StringUtil.getUUID())
                    .function(ToolCall.Function.builder()
                            .name(toolName)
                            .arguments(JSON.toJSONString(jsonObj))
                            .build())
                    .build();
        } catch (Exception e) {
            log.error("{} parse tool call error {}", context.getRequestId(), jsonContent);
        }
        return null;
    }

    /**
     * LLM 响应类
     */
    @Data
    @Builder
    @AllArgsConstructor
    @NoArgsConstructor
    public static class ToolCallResponse {
        private String content;
        private List<ToolCall> toolCalls;
        private String finishReason;
        private Integer totalTokens;
        private long duration;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class OpenAIChoice {
        private Integer index;
        private OpenAIDelta delta;
        private Object logprobs;
        private String finish_reason;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class OpenAIDelta {
        private String content;
        private List<OpenAIToolCall> tool_calls;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class OpenAIToolCall {
        private Integer index;
        private String id;
        private String type;
        private OpenAIFunction function;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class OpenAIFunction {
        private String name;
        private String arguments;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ClaudeResponse {
        private ClaudeDelta delta;
        private String arguments;
        private String id;
    }

    @Data
    @JsonIgnoreProperties(ignoreUnknown = true)
    public static class ClaudeDelta {
        private String text;
        private String partial_json;
        private String type;
    }


}
