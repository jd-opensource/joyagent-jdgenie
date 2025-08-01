package com.jd.genie.agent.tool.common;

import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.dto.CodeInterpreterRequest;
import com.jd.genie.agent.dto.CodeInterpreterResponse;
import com.jd.genie.agent.dto.File;
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
import java.util.stream.Collectors;

@Slf4j
@Data

public class ReportTool implements BaseTool {
    private AgentContext agentContext;

    @Override
    public String getName() {
        return "report_tool";
    }

    @Override
    public String getDescription() {
        String desc = "这是一个报告工具，可以通过编写HTML、MarkDown报告";
        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        return genieConfig.getReportToolDesc().isEmpty() ? desc : genieConfig.getReportToolDesc();
    }

    @Override
    public Map<String, Object> toParams() {

        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        if (!genieConfig.getReportToolParams().isEmpty()) {
            return genieConfig.getReportToolParams();
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
        long startTime = System.currentTimeMillis();

        try {
            Map<String, Object> params = (Map<String, Object>) input;
            String task = (String) params.get("task");
            String fileDescription = (String) params.get("fileDescription");
            String fileName = (String) params.get("fileName");
            String fileType = (String) params.get("fileType");


            if (fileName.isEmpty()) {
                String errMessage = "文件名参数为空，无法生成报告。";
                log.error("{} {}", agentContext.getRequestId(), errMessage);
                return null;
            }

            List<String> fileNames = agentContext.getProductFiles().stream().map(File::getFileName).collect(Collectors.toList());
            Map<String, Object> streamMode = new HashMap<>();
            streamMode.put("mode", "token");
            streamMode.put("token", 10);
            CodeInterpreterRequest request = CodeInterpreterRequest.builder()
                    .requestId(agentContext.getSessionId()) // 适配多轮对话
                    .query(agentContext.getQuery())
                    .task(task)
                    .fileNames(fileNames)
                    .fileName(fileName)
                    .fileDescription(fileDescription)
                    .stream(true)
                    .contentStream(agentContext.getIsStream())
                    .streamMode(streamMode)
                    .fileType(fileType)
                    .build();
            // 调用流式 API
            Future future = callCodeAgentStream(request);
            Object object = future.get();

            return object;
        } catch (Exception e) {
            log.error("{} report_tool error", agentContext.getRequestId(), e);

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
                    .connectTimeout(60, TimeUnit.SECONDS) // 设置连接超时时间为 1 分钟
                    .readTimeout(600, TimeUnit.SECONDS)    // 设置读取超时时间为 10 分钟
                    .writeTimeout(600, TimeUnit.SECONDS)   // 设置写入超时时间为 10 分钟
                    .callTimeout(600, TimeUnit.SECONDS)    // 设置调用超时时间为 10 分钟
                    .build();

            ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
            GenieConfig genieConfig = applicationContext.getBean(GenieConfig.class);
            String url = genieConfig.getCodeInterpreterUrl() + "/v1/tool/report";
            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    JSONObject.toJSONString(codeRequest)
            );

            log.info("{} report_tool request {}", agentContext.getRequestId(), JSONObject.toJSONString(codeRequest));
            Request.Builder requestBuilder = new Request.Builder()
                    .url(url)
                    .post(body);
            Request request = requestBuilder.build();

            String[] interval = genieConfig.getMessageInterval().getOrDefault("report", "1,4").split(",");
            int firstInterval = Integer.parseInt(interval[0]);
            int sendInterval = Integer.parseInt(interval[1]);
            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    log.error("{} report_tool on failure", agentContext.getRequestId(), e);
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) {

                    log.info("{} report_tool response {} {} {}", agentContext.getRequestId(), response, response.code(), response.body());
                    CodeInterpreterResponse codeResponse = CodeInterpreterResponse.builder()
                            .codeOutput("report_tool 执行失败") // 默认输出
                            .build();
                    try {
                        ResponseBody responseBody = response.body();
                        if (!response.isSuccessful() || responseBody == null) {
                            log.error("{} report_tool request error.", agentContext.getRequestId());
                            future.completeExceptionally(new IOException("Unexpected response code: " + response));
                            return;
                        }

                        int index = 1;
                        StringBuilder stringBuilderIncr = new StringBuilder();
                        String line;
                        String messageId = StringUtil.getUUID();
                        // 获取数字人名称
                        String digitalEmployee = agentContext.getToolCollection().getDigitalEmployee(getName());
                        BufferedReader reader = new BufferedReader(new InputStreamReader(responseBody.byteStream()));
                        while ((line = reader.readLine()) != null) {
                            if (line.startsWith("data: ")) {
                                String data = line.substring(6);
                                if (data.equals("[DONE]")) {
                                    break;
                                }
                                if (index == 1 || index % 100 == 0) {
                                    log.info("{} report_tool recv data: {}", agentContext.getRequestId(), data);
                                }
                                if (data.startsWith("heartbeat")) {
                                    continue;
                                }
                                codeResponse = JSONObject.parseObject(data, CodeInterpreterResponse.class);
                                if (codeResponse.getIsFinal()) {
                                    // report_tool 只会输出一个文件，使用模型输出的文件名和描述
                                    if (Objects.nonNull(codeResponse.getFileInfo())) {
                                        for (CodeInterpreterResponse.FileInfo fileInfo : codeResponse.getFileInfo()) {
                                            File file = File.builder()
                                                    .fileName(codeRequest.getFileName())
                                                    .fileSize(fileInfo.getFileSize())
                                                    .ossUrl(fileInfo.getOssUrl())
                                                    .domainUrl(fileInfo.getDomainUrl())
                                                    .description(codeRequest.getFileDescription())
                                                    .isInternalFile(false)
                                                    .build();
                                            agentContext.getProductFiles().add(file);
                                            agentContext.getTaskProductFiles().add(file);
                                        }
                                    }
                                    agentContext.getPrinter().send(messageId, codeRequest.getFileType(), codeResponse, digitalEmployee, true);
                                } else {
                                    stringBuilderIncr.append(codeResponse.getData());
                                    if (index == firstInterval || index % sendInterval == 0) {
                                        codeResponse.setData(stringBuilderIncr.toString());
                                        agentContext.getPrinter().send(messageId, codeRequest.getFileType(), codeResponse, digitalEmployee, false);
                                        stringBuilderIncr.setLength(0);
                                    }
                                }
                                index++;
                            }
                        }
                    } catch (Exception e) {
                        log.error("{} report_tool request error", agentContext.getRequestId(), e);
                        future.completeExceptionally(e);
                        return;
                    }
                    // 统一使用data字段，兼容历史codeOutput逻辑
                    String result = Objects.nonNull(codeResponse.getData()) && !codeResponse.getData().isEmpty() ? codeResponse.getData() : codeResponse.getCodeOutput();
                    future.complete(result);
                }
            });
        } catch (Exception e) {
            log.error("{} report_tool request error", agentContext.getRequestId(), e);
            future.completeExceptionally(e);
        }

        return future;
    }
}