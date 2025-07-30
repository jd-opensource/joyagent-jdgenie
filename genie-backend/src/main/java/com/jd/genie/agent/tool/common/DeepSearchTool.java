package com.jd.genie.agent.tool.common;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.dto.DeepSearchRequest;
import com.jd.genie.agent.dto.DeepSearchrResponse;
import com.jd.genie.agent.dto.FileRequest;
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
import java.util.Collections;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;

@Slf4j
@Data

public class DeepSearchTool implements BaseTool {

    private AgentContext agentContext;

    @Override
    public String getName() {
        return "deep_search";
    }

    @Override
    public String getDescription() {
        String desc = "这是一个搜索工具，可以通过搜索内外网知识";
        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        return genieConfig.getDeepSearchToolDesc().isEmpty() ? desc : genieConfig.getDeepSearchToolDesc();
    }

    @Override
    public Map<String, Object> toParams() {

        GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
        if (!genieConfig.getDeepSearchToolParams().isEmpty()) {
            return genieConfig.getDeepSearchToolParams();
        }

        Map<String, Object> taskParam = new HashMap<>();
        taskParam.put("type", "string");
        taskParam.put("description", "需要搜索的query");
        Map<String, Object> parameters = new HashMap<>();
        parameters.put("type", "object");
        Map<String, Object> properties = new HashMap<>();
        properties.put("query", taskParam);
        parameters.put("properties", properties);
        parameters.put("required", Collections.singletonList("query"));

        return parameters;
    }

    @Override
    public Object execute(Object input) {
        long startTime = System.currentTimeMillis();

        try {
            GenieConfig genieConfig = SpringContextHolder.getApplicationContext().getBean(GenieConfig.class);
            Map<String, Object> params = (Map<String, Object>) input;
            String query = (String) params.get("query");
            Map<String, Object> srcConfig = new HashMap<>();

            Map<String, Object> bingConfig = new HashMap<>();
            bingConfig.put("count", Integer.parseInt(genieConfig.getDeepSearchPageCount()));
            srcConfig.put("bing", bingConfig);
            DeepSearchRequest request = DeepSearchRequest.builder()
                    .request_id(agentContext.getRequestId() + ":" + StringUtil.generateRandomString(5))
                    .query(query)
                    .agent_id("1")
                    .scene_type("auto_agent")
                    .src_configs(srcConfig)
                    .stream(true)
                    .content_stream(agentContext.getIsStream())
                    .build();

            // 调用流式 API
            Future future = callDeepSearchStream(request);
            Object object = future.get();

            return object;
        } catch (Exception e) {

            log.error("{} deep_search agent error", agentContext.getRequestId(), e);
        }
        return null;
    }

    /**
     * 调用 DeepSearch
     */
    public CompletableFuture<String> callDeepSearchStream(DeepSearchRequest searchRequest) {
        CompletableFuture<String> future = new CompletableFuture<>();
        try {
            OkHttpClient client = new OkHttpClient.Builder()
                    .connectTimeout(60, TimeUnit.SECONDS) // 设置连接超时时间为 60 秒
                    .readTimeout(300, TimeUnit.SECONDS)    // 设置读取超时时间为 300 秒
                    .writeTimeout(300, TimeUnit.SECONDS)   // 设置写入超时时间为 300 秒
                    .callTimeout(300, TimeUnit.SECONDS)    // 设置调用超时时间为 300 秒
                    .build();

            ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
            GenieConfig genieConfig = applicationContext.getBean(GenieConfig.class);
            String url = genieConfig.getDeepSearchUrl() + "/v1/tool/deepsearch";
            RequestBody body = RequestBody.create(
                    MediaType.parse("application/json"),
                    JSONObject.toJSONString(searchRequest)
            );

            log.info("{} deep_search request {}", agentContext.getRequestId(), JSONObject.toJSONString(searchRequest));
            Request.Builder requestBuilder = new Request.Builder()
                    .url(url)
                    .post(body);
            Request request = requestBuilder.build();

            String[] interval = genieConfig.getMessageInterval().getOrDefault("search", "5,20").split(",");
            int firstInterval = Integer.parseInt(interval[0]);
            int sendInterval = Integer.parseInt(interval[1]);

            client.newCall(request).enqueue(new Callback() {
                @Override
                public void onFailure(Call call, IOException e) {
                    log.error("{} deep_search on failure", agentContext.getRequestId(), e);
                    future.completeExceptionally(e);
                }

                @Override
                public void onResponse(Call call, Response response) {

                    log.info("{} deep_search response {} {} {}", agentContext.getRequestId(), response, response.code(), response.body());
                    try (ResponseBody responseBody = response.body()) {
                        if (!response.isSuccessful() || responseBody == null) {
                            log.error("{} deep_search request error", agentContext.getRequestId());
                            future.completeExceptionally(new IOException("Unexpected response code: " + response));
                            return;
                        }

                        int index = 1;
                        StringBuilder stringBuilderIncr = new StringBuilder();
                        StringBuilder stringBuilderAll = new StringBuilder();
                        String line;
                        BufferedReader reader = new BufferedReader(new InputStreamReader(responseBody.byteStream()));
                        String digitalEmployee = agentContext.getToolCollection().getDigitalEmployee(getName());
                        String result = "搜索结果为空"; // 默认输出
                        String messageId = "";
                        while ((line = reader.readLine()) != null) {
                            if (line.startsWith("data: ")) {
                                String data = line.substring(6);
                                if (data.equals("[DONE]")) {
                                    break;
                                }
                                if (data.startsWith("heartbeat")) {
                                    continue;
                                }
                                if (index == 1 || index % 100 == 0) {
                                    log.info("{} deep_search recv data: {}", agentContext.getRequestId(), data);
                                }
                                DeepSearchrResponse searchResponse = JSONObject.parseObject(data, DeepSearchrResponse.class);
                                FileTool fileTool = new FileTool();
                                fileTool.setAgentContext(agentContext);
                                // 上传搜索内容到文件中
                                if (searchResponse.getIsFinal()) {
                                    if (agentContext.getIsStream()) {
                                        searchResponse.setAnswer(stringBuilderAll.toString());
                                    }
                                    if (searchResponse.getAnswer().isEmpty()) {
                                        log.error("{} deep search answer empty", agentContext.getRequestId());
                                        break;
                                    }
                                    String fileName = StringUtil.removeSpecialChars(searchResponse.getQuery() + "的搜索结果.md");
                                    String fileDesc = searchResponse.getAnswer()
                                            .substring(0, Math.min(searchResponse.getAnswer().length(), genieConfig.getDeepSearchToolFileDescTruncateLen())) + "...";
                                    FileRequest fileRequest = FileRequest.builder()
                                            .requestId(agentContext.getRequestId())
                                            .fileName(fileName)
                                            .description(fileDesc)
                                            .content(searchResponse.getAnswer())
                                            .build();
                                    fileTool.uploadFile(fileRequest, false, false);
                                    result = searchResponse.getAnswer().
                                            substring(0, Math.min(searchResponse.getAnswer().length(), genieConfig.getDeepSearchToolMessageTruncateLen()));

                                    agentContext.getPrinter().send(messageId, "deep_search", searchResponse, digitalEmployee, true);

                                } else {
                                    Map<String, Object> contentMap = new HashMap<>();
                                    for (int idx = 0; idx < searchResponse.getSearchResult().getQuery().size(); idx++) {
                                        contentMap.put(searchResponse.getSearchResult().getQuery().get(idx), searchResponse.getSearchResult().getDocs().get(idx));
                                    }

                                    if ("extend".equals(searchResponse.getMessageType())) {
                                        messageId = StringUtil.getUUID();
                                        searchResponse.setSearchFinish(false);
                                        agentContext.getPrinter().send(messageId, "deep_search", searchResponse, digitalEmployee, true);
                                    } else if ("search".equals(searchResponse.getMessageType())) {
                                        searchResponse.setSearchFinish(true);
                                        agentContext.getPrinter().send(messageId, "deep_search", searchResponse, digitalEmployee, true);
                                        FileRequest fileRequest = FileRequest.builder()
                                                .requestId(agentContext.getRequestId())
                                                .fileName(searchResponse.getQuery() + "_search_result.txt")
                                                .description(searchResponse.getQuery() + "...")
                                                .content(JSON.toJSONString(contentMap))
                                                .build();
                                        fileTool.uploadFile(fileRequest, false, true);
                                    } else if ("report".equals(searchResponse.getMessageType())) {
                                        if (index == 1) {
                                            messageId = StringUtil.getUUID();
                                        }
                                        stringBuilderIncr.append(searchResponse.getAnswer());
                                        stringBuilderAll.append(searchResponse.getAnswer());
                                        if (index == firstInterval || index % sendInterval == 0) {
                                            searchResponse.setAnswer(stringBuilderIncr.toString());
                                            agentContext.getPrinter().send(messageId, "deep_search", searchResponse, digitalEmployee, false);
                                            stringBuilderIncr.setLength(0);
                                        }
                                        index++;
                                    }
                                }
                            }
                        }
                        future.complete(result);

                    } catch (Exception e) {
                        log.error("{} deep_search request error", agentContext.getRequestId(), e);
                        future.completeExceptionally(e);
                    }
                }
            });
        } catch (Exception e) {
            log.error("{} deep_search request error", agentContext.getRequestId(), e);
            future.completeExceptionally(e);
        }

        return future;
    }
}