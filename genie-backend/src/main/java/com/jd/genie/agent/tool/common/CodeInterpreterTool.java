package com.jd.genie.agent.tool.common;

import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.dto.CodeInterpreterRequest;
import com.jd.genie.agent.dto.CodeInterpreterResponse;
import com.jd.genie.agent.dto.File;
import com.jd.genie.agent.tool.BaseTool;
import com.jd.genie.agent.util.SpringContextHolder;
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
import java.util.stream.Collectors;

@Slf4j
@Data
public class CodeInterpreterTool implements BaseTool {

    private AgentContext agentContext;

    @Override
    public String getName() {
        return "code_interpreter";
    }

    @Override
    public String getDescription() {
        String desc = "这是一个代码工具，可以通过编写代码完成数据处理、数据分析、图表生成等任务";
        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        return genieConfig.getCodeAgentDesc().isEmpty() ? desc : genieConfig.getCodeAgentDesc();
    }

    @Override
    public Map<String, Object> toParams() {

        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        if (!genieConfig.getCodeAgentParams().isEmpty()) {
            return genieConfig.getCodeAgentParams();
        }

        Map<String, Object> taskParam = new HashMap<>();
        taskParam.put("type", "string");
        taskParam.put("description", "需要完成的任务以及完成任务需要的数据，需要尽可能详细");
        Map<String, Object> parameters = new HashMap<>();
        parameters.put("type", "object");
        Map<String, Object> properties = new HashMap<>();
        properties.put("task", taskParam);
        parameters.put("properties", properties);
        parameters.put("required", Collections.singletonList("task"));

        return parameters;
    }

    @Override
    public Object execute(Object input) {
        try {
            Map<String, Object> params = (Map<String, Object>) input;
            String task = (String) params.get("task");
            List<String> fileNames = agentContext.getProductFiles().stream().map(File::getFileName).collect(Collectors.toList());
            CodeInterpreterRequest request = CodeInterpreterRequest.builder()
                    .requestId(agentContext.getSessionId()) // 适配多轮对话
                    .query(agentContext.getQuery())
                    .task(task)
                    .fileNames(fileNames)
                    .stream(true)
                    .build();

            // 调用流式 API
            Future future = callCodeAgentStream(request);
            Object object = future.get();

            return object;
        } catch (Exception e) {
            log.error("{} code agent error", agentContext.getRequestId(), e);
        }
        return null;
    }

    /**
     * 调用 CodeAgent
     */
    public CompletableFuture<String> callCodeAgentStream(CodeInterpreterRequest codeRequest) {
        CompletableFuture<String> future = new CompletableFuture<>();
        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(60, TimeUnit.SECONDS) // 设置连接超时时间为 60 秒
                    .readTimeout(300, TimeUnit.SECONDS)    // 设置读取超时时间为 60 秒
                    .writeTimeout(300, TimeUnit.SECONDS)   // 设置写入超时时间为 60 秒
                    .callTimeout(300, TimeUnit.SECONDS)    // 设置调用超时时间为 60 秒
                    .build();

            ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
            GenieConfig genieConfig = applicationContext.getBean(GenieConfig.class);
            String url = genieConfig.getCodeInterpreterUrl() + "/v1/tool/code_interpreter";
            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    JSONObject.toJSONString(codeRequest)
            );

            log.info("{} code_interpreter request {}", agentContext.getRequestId(), JSONObject.toJSONString(codeRequest));
            Request.Builder requestBuilder = new Request.Builder()
                    .url(url)
                    .post(body);
            Request request = requestBuilder.build();

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    log.error("{} code_interpreter on failure", agentContext.getRequestId(), e);
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) {

                    log.info("{} code_interpreter response {} {} {}", agentContext.getRequestId(), response, response.code(), response.body());
                    CodeInterpreterResponse codeResponse = CodeInterpreterResponse.builder()
                            .codeOutput("code_interpreter执行失败") // 默认输出
                            .build();
                    try (ResponseBody responseBody = response.body()) {
                        if (!response.isSuccessful() || responseBody == null) {
                            log.error("{} code_interpreter request error", agentContext.getRequestId());
                            future.completeExceptionally(new IOException("Unexpected response code: " + response));
                            return;
                        }

                        String line;
                        BufferedReader reader = new BufferedReader(new InputStreamReader(responseBody.byteStream()));
                        while ((line = reader.readLine()) != null) {
                            if (line.startsWith("data: ")) {
                                String data = line.substring(6);
                                if (data.equals("[DONE]")) {
                                    break;
                                }
                                if (data.startsWith("heartbeat")) {
                                    continue;
                                }
                                log.info("{} code_interpreter recv data: {}", agentContext.getRequestId(), data);
                                codeResponse = JSONObject.parseObject(data, CodeInterpreterResponse.class);
                                if (Objects.nonNull(codeResponse.getFileInfo()) && !codeResponse.getFileInfo().isEmpty()) {
                                    for (CodeInterpreterResponse.FileInfo fileInfo : codeResponse.getFileInfo()) {
                                        File file = File.builder()
                                                .fileName(fileInfo.getFileName())
                                                .ossUrl(fileInfo.getOssUrl())
                                                .domainUrl(fileInfo.getDomainUrl())
                                                .fileSize(fileInfo.getFileSize())
                                                .description(fileInfo.getFileName()) // fileName用作描述
                                                .isInternalFile(false)
                                                .build();
                                        agentContext.getProductFiles().add(file);
                                        agentContext.getTaskProductFiles().add(file);
                                    }
                                }
                                String digitalEmployee = agentContext.getToolCollection().getDigitalEmployee(getName());
                                log.info("requestId:{} task:{} toolName:{} digitalEmployee:{}", agentContext.getRequestId(),
                                        agentContext.getToolCollection().getCurrentTask(), getName(), digitalEmployee);
                                agentContext.getPrinter().send("code", codeResponse, digitalEmployee);
                            }
                        }

                    } catch (Exception e) {
                        log.error("{} code_interpreter request error", agentContext.getRequestId(), e);
                        future.completeExceptionally(e);
                        return;
                    }
                    /**
                     * {{输出内容}}
                     * \n\n
                     * 其中保存了文件：
                     * {{文件名}}
                     */
                    StringBuilder output = new StringBuilder();
                    output.append(codeResponse.getCodeOutput());
                    if (Objects.nonNull(codeResponse.getFileInfo()) && !codeResponse.getFileInfo().isEmpty()) {
                        output.append("\n\n其中保存了文件: ");
                        for (CodeInterpreterResponse.FileInfo fileInfo : codeResponse.getFileInfo()) {
                            output.append(fileInfo.getFileName()).append("\n");
                        }
                    }
                    future.complete(output.toString());
                }
            });
        } catch (Exception e) {
            log.error("{} code_interpreter request error", agentContext.getRequestId(), e);
            future.completeExceptionally(e);
        }

        return future;
    }
}