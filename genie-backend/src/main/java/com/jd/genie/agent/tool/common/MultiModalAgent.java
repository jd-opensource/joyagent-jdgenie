package com.jd.genie.agent.tool.common;

import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.dto.FileRequest;
import com.jd.genie.agent.dto.MultiModalAgentRequest;
import com.jd.genie.agent.dto.MultiModalAgentResponse;
import com.jd.genie.agent.tool.BaseTool;
import com.jd.genie.agent.util.SpringContextHolder;
import com.jd.genie.agent.util.StringUtil;
import com.jd.genie.config.GenieConfig;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.context.ApplicationContext;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

@Slf4j
@Data
public class MultiModalAgent implements BaseTool {
    private AgentContext agentContext;

    @Override
    public String getName() {
        return "multimodalagent_tool";
    }

    @Override
    public String getDescription() {
        String desc = "本工具用于查询与用户相关的知识，作为在线知识的补充。支持文本和图像等多模态数据检索，能够高效访问和获取用户专属的知识信息。";
        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        return genieConfig.getMultiModalAgentDesc().isEmpty() ? desc : genieConfig.getMultiModalAgentDesc();
    }

    @Override
    public Map<String, Object> toParams() {
        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        if (!genieConfig.getMultiModalAgentPamras().isEmpty()) {
            return genieConfig.getMultiModalAgentPamras();
        }

        Map<String, Object> questionParam = new HashMap<>();
        questionParam.put("type", "string");
        questionParam.put("description", "查询所需要的question，需要在知识库中进行检索的检索短语或句子。");
        Map<String, Object> parameters = new HashMap<>();
        parameters.put("type", "object");
        Map<String, Object> properties = new HashMap<>();
        properties.put("question", questionParam);
        parameters.put("properties", properties);
        parameters.put("required", Collections.singletonList("question"));

        return parameters;
    }

    @Override
    public Object execute(Object input) {
        try {
            Map<String, Object> params = (Map<String, Object>) input;
            String question = (String) params.get("question");

            if (question == null || question.isEmpty()) {
                String errMessage = "question 为空无法调用知识库查询。";
                log.error("{} {}", agentContext.getRequestId(), errMessage);
                return null;
            }

            Map<String, Object> streamMode = new HashMap<>();
            streamMode.put("mode", "token");
            streamMode.put("token", 10);
            
            MultiModalAgentRequest request = MultiModalAgentRequest.builder()
                    .requestId(agentContext.getSessionId()) // 适配多轮对话
                    .question(question)
                    .query(agentContext.getQuery())
                    .stream(true)
                    .contentStream(agentContext.getIsStream())
                    .streamMode(streamMode)
                    .build();
            
            // 调用流式 API
            Future future = callKnowledgeAgentStream(request);
            Object object = future.get();
            return object;
        } catch (Exception e) {
            log.error("{} knowledge_tool error", agentContext.getRequestId(), e);
        }

        return null;
    }

    /**
     * 调用知识查询流式API
     */
    public CompletableFuture<String> callKnowledgeAgentStream(MultiModalAgentRequest multiModalAgentRequest) {
        CompletableFuture<String> future = new CompletableFuture<>();
        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(60, TimeUnit.SECONDS) // 设置连接超时时间为 1 分钟
                    .readTimeout(600, TimeUnit.SECONDS)    // 设置读取超时时间为 10 分钟
                    .writeTimeout(600, TimeUnit.SECONDS)   // 设置写入超时时间为 10 分钟
                    .callTimeout(600, TimeUnit.SECONDS)    // 设置调用超时时间为 10 分钟
                    .build();

            ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
            GenieConfig genieConfig = applicationContext.getBean(GenieConfig.class);
            String url = genieConfig.getMultiModalAgentUrl() + "/v1/tool/mragQuery";
            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    JSONObject.toJSONString(multiModalAgentRequest)
            );
            log.info("==== {} knowledge_tool request {} ====", agentContext.getRequestId(), JSONObject.toJSONString(multiModalAgentRequest));
            Request.Builder requestBuilder = new Request.Builder()
                    .url(url)
                    .post(body)
                    .addHeader("Content-Type", "application/json");
            Request request = requestBuilder.build();
            // log.info("{} knowledge_tool recv data: {}", agentContext.getRequestId(), data);
            String[] interval = genieConfig.getMessageInterval().getOrDefault("knowledge", "1,4").split(",");
            int firstInterval = Integer.parseInt(interval[0]);
            int sendInterval = Integer.parseInt(interval[1]);
            
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    log.error("{} knowledge_tool on failure", agentContext.getRequestId(), e);
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) {
                    log.info("{} knowledge_tool response {} {} {}", agentContext.getRequestId(), response, response.code(), response.body());
                    MultiModalAgentResponse multiModalAgentResponse = MultiModalAgentResponse.builder()
                            .data("knowledge_tool 执行失败") // 默认输出
                            .build();
                    // 在方法开始处定义StringBuilder，确保在所有代码路径中都可访问
                    StringBuilder stringBuilderIncr = new StringBuilder(); // 用于阶段性发送
                    StringBuilder allTokensBuilder = new StringBuilder(); // 用于累加所有token，不会被清空
                    try {
                        ResponseBody responseBody = response.body();
                        if (!response.isSuccessful() || responseBody == null) {
                            log.error("{} knowledge_tool request error.", agentContext.getRequestId());
                            future.completeExceptionally(new IOException("Unexpected response code: " + response));
                            return;
                        }

                        int index = 1;
                        String line;
                        String messageId = StringUtil.getUUID();
                        BufferedReader reader = new BufferedReader(new InputStreamReader(responseBody.byteStream()));
                        String digitalEmployee = agentContext.getToolCollection().getDigitalEmployee(getName());
                        while ((line = reader.readLine()) != null) {
                            if (line.startsWith("data: ")) {
                                String data = line.substring(6);
                                if (data.equals("[DONE]")) {
                                    break;
                                }
//                                if (index == 1 || index % 100 == 0) {
                                log.info("{} knowledge_tool recv data: {}", agentContext.getRequestId(), data);
//                                }
                                if (data.startsWith("heartbeat")) {
                                    continue;
                                }
                                
                                try {
                                    // 尝试解析为标准OpenAI格式响应
                                    MultiModalAgentResponse streamResponse = JSONObject.parseObject(data, MultiModalAgentResponse.class);
                                    FileTool fileTool = new FileTool();
                                    fileTool.setAgentContext(agentContext);
                                    // 处理标准OpenAI格式响应
                                    if (streamResponse.getChoices() != null && !streamResponse.getChoices().isEmpty()) {
                                        MultiModalAgentResponse.Choice choice = streamResponse.getChoices().get(0);
                                        if (choice.getDelta() != null && choice.getDelta().getContent() != null) {
                                            String content = choice.getDelta().getContent();
                                            
                                            // 特殊处理图片内容
                                            if (content.contains("![图片]")) {
                                                log.info("{} knowledge_tool received image content: {}", agentContext.getRequestId(), content);
                                            }
                                            
                                            stringBuilderIncr.append(content);
                                            allTokensBuilder.append(content); // 累加所有token，不会被清空
                                            
                                            if (index == firstInterval || index % sendInterval == 0) {
                                                multiModalAgentResponse.setData(stringBuilderIncr.toString()); // 使用阶段性累加的token
                                                multiModalAgentResponse.setIsFinal(false);
                                                // agentContext.getPrinter().send(messageId, "knowledge", multiModalAgentResponse, digitalEmployee, false);
                                                // log.info(" ==== limit knowledge_tool recv data: {} ====", stringBuilderIncr.toString());
                                                stringBuilderIncr.setLength(0);
                                            }
                                            
                                            // 检查是否为最终响应
                                            if ("stop".equals(choice.getFinishReason())) {
                                                // 最终响应时才使用所有累加的token
                                                multiModalAgentResponse.setData(allTokensBuilder.toString());
                                                multiModalAgentResponse.setIsFinal(true);
                                                log.info(" ### ==== all knowledge_tool recv data: {} ====", allTokensBuilder.toString());
                                                agentContext.getPrinter().send(messageId, "markdown", multiModalAgentResponse, digitalEmployee, true);

                                                String fileName = StringUtil.removeSpecialChars(  agentContext.getQuery() + "的多模态检索结果.md");
                                                String fileDesc = allTokensBuilder.toString()
                                                        .substring(0, Math.min(allTokensBuilder.toString().length(), genieConfig.getDeepSearchToolFileDescTruncateLen())) + "...";
                                                FileRequest fileRequest = FileRequest.builder()
                                                        .requestId(agentContext.getRequestId())
                                                        .fileName(fileName)
                                                        .description(fileDesc)
                                                        .content(allTokensBuilder.toString())
                                                        .build();
                                                fileTool.uploadFile(fileRequest, false, false);

                                            }
                                        }
                                    }
                                } catch (Exception e) {
                                    // 尝试解析为自定义格式响应（包含data和isFinal字段）
                                    try {
                                        MultiModalAgentResponse streamResponse = JSONObject.parseObject(data, MultiModalAgentResponse.class);
                                        
                                        // 判断是否为最终响应
                                        if (streamResponse.getIsFinal() != null && streamResponse.getIsFinal()) {
                                            multiModalAgentResponse.setData(streamResponse.getData());
                                            multiModalAgentResponse.setIsFinal(true);
                                            // agentContext.getPrinter().send(messageId, "knowledge", knowledgeResponse, digitalEmployee, true);
                                        } else {
                                            // 处理流式响应
                                            if (index == 1) {
                                                messageId = StringUtil.getUUID();
                                            }

                                            String content = streamResponse.getData();
                                            if (content != null && !content.isEmpty()) {
                                                stringBuilderIncr.append(content);
                                                allTokensBuilder.append(content); // 累加所有token，不会被清空

                                                if (index == firstInterval || index % sendInterval == 0) {
                                                    multiModalAgentResponse.setData(stringBuilderIncr.toString()); // 使用阶段性累加的token
                                                    multiModalAgentResponse.setIsFinal(false);
                                                    agentContext.getPrinter().send(messageId, "knowledge", multiModalAgentResponse, digitalEmployee, false);
                                                    log.info(" ==== limit knowledge_tool recv data: {} ====", stringBuilderIncr.toString());
                                                    stringBuilderIncr.setLength(0);
                                                }
                                            }
                                        }
                                    } catch (Exception ex) {
                                        log.error("{} knowledge_tool failed to parse response: {}", agentContext.getRequestId(), data, ex);
                                    }
                                }
                                index++;
                            }
                        }
                    } catch (Exception e) {
                        log.error("{} knowledge_tool request error", agentContext.getRequestId(), e);
                        future.completeExceptionally(e);
                        return;
                    }

                    // 使用allTokensBuilder作为最终结果
                    String result = allTokensBuilder.length() > 0 ? allTokensBuilder.toString() : "knowledge_tool 执行完成";
                    log.info(" ==== knowledge_tool recv data: {} ====", result);
                    future.complete(result);
                }
            });
        } catch (Exception e) {
            log.error("{} knowledge_tool request error", agentContext.getRequestId(), e);
            future.completeExceptionally(e);
        }

        return future;
    }
}
