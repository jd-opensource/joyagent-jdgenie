package com.jd.genie.service.impl;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import com.jd.genie.agent.enums.AgentType;
import com.jd.genie.agent.enums.AutoBotsResultStatus;
import com.jd.genie.agent.enums.ResponseTypeEnum;
import com.jd.genie.config.GenieConfig;
import com.jd.genie.handler.AgentResponseHandler;
import com.jd.genie.model.dto.AutoBotsResult;
import com.jd.genie.model.multi.EventResult;
import com.jd.genie.model.req.AgentRequest;
import com.jd.genie.model.req.GptQueryReq;
import com.jd.genie.model.response.AgentResponse;
import com.jd.genie.model.response.GptProcessResult;
import com.jd.genie.service.IMultiAgentService;
import com.jd.genie.util.ChateiUtils;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.*;
import java.util.concurrent.TimeUnit;

@Slf4j
@Component
public class MultiAgentServiceImpl implements IMultiAgentService {
    @Autowired
    private GenieConfig genieConfig;
    @Autowired
    private Map<AgentType, AgentResponseHandler> handlerMap;

    @Override
    public AutoBotsResult searchForAgentRequest(GptQueryReq gptQueryReq, SseEmitter sseEmitter) {
        AgentRequest agentRequest = buildAgentRequest(gptQueryReq);
        log.info("{} start handle Agent request: {}", gptQueryReq.getRequestId(), JSON.toJSONString(agentRequest));
        try {
            handleMultiAgentRequest(agentRequest, sseEmitter);
        } catch (Exception e) {
            log.error("{}, error in requestMultiAgent, deepThink: {}, errorMsg: {}", gptQueryReq.getRequestId(), gptQueryReq.getDeepThink(), e.getMessage(), e);
            throw e;
        } finally {
            log.info("{}, agent.query.web.singleRequest end, requestId: {}", gptQueryReq.getRequestId(), JSON.toJSONString(gptQueryReq));
        }

        return ChateiUtils.toAutoBotsResult(agentRequest, AutoBotsResultStatus.loading.name());
    }

    public void handleMultiAgentRequest(AgentRequest autoReq,SseEmitter sseEmitter) {
        long startTime = System.currentTimeMillis();
        Request request = buildHttpRequest(autoReq);
        log.info("{} agentRequest:{}", autoReq.getRequestId(), JSON.toJSONString(request));
        OkHttpClient client = new OkHttpClient.Builder()
                .connectTimeout(60, TimeUnit.SECONDS) // 设置连接超时时间为 60 秒
                .readTimeout(genieConfig.getSseClientReadTimeout(), TimeUnit.SECONDS)    // 设置读取超时时间为 60 秒
                .writeTimeout(1800, TimeUnit.SECONDS)   // 设置写入超时时间为 60 秒
                .callTimeout(genieConfig.getSseClientConnectTimeout(), TimeUnit.SECONDS)    // 设置调用超时时间为 60 秒
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                log.error("onFailure {}", e.getMessage(), e);
            }

            @Override
            public void onResponse(Call call, Response response) {
                List<AgentResponse> agentRespList = new ArrayList<>();
                EventResult eventResult = new EventResult();
                ResponseBody responseBody = response.body();
                if (responseBody == null) {
                    log.error("{} auto agent empty response body", autoReq.getRequestId());
                    return;
                }

                try {
                    if (!response.isSuccessful()) {
                        log.error("{}, response body is failed: {}", autoReq.getRequestId(), responseBody.string());
                        return;
                    }

                    String line;
                    BufferedReader reader = new BufferedReader(
                            new InputStreamReader(responseBody.byteStream())
                    );

                    while ((line = reader.readLine()) != null) {
                        if (!line.startsWith("data:")) {
                            continue;
                        }

                        String data = line.substring(5);
                        if (data.equals("[DONE]")) {
                            log.info("{} data equals with [DONE] {}:", autoReq.getRequestId(), data);
                            break;
                        }

                        if (data.startsWith("heartbeat")) {
                            GptProcessResult result = buildHeartbeatData(autoReq.getRequestId());
                            sseEmitter.send(result);
                            log.info("{} heartbeat-data: {}", autoReq.getRequestId(), data);
                            continue;
                        }

                        log.info("{} recv from autocontroller: {}", autoReq.getRequestId(), data);
                        AgentResponse agentResponse = JSON.parseObject(data, AgentResponse.class);
                        AgentType agentType = AgentType.fromCode(autoReq.getAgentType());
                        AgentResponseHandler handler = handlerMap.get(agentType);
                        GptProcessResult result = handler.handle(autoReq, agentResponse,agentRespList, eventResult);
                        sseEmitter.send(result);
                        if (result.isFinished()) {
                            // 记录任务执行时间
                            log.info("{} task total cost time:{}ms", autoReq.getRequestId(), System.currentTimeMillis() - startTime);
                            sseEmitter.complete();
                        }
                    }
                }catch (Exception e) {
                    log.error("", e);
                }
            }
        });
    }

    private Request buildHttpRequest(AgentRequest autoReq) {
        String reqId = autoReq.getRequestId();
        autoReq.setRequestId(autoReq.getRequestId());
        String url = "http://" + genieConfig.getServerIp() + ":" + genieConfig.getServerPort() + "/AutoAgent";
        RequestBody body = RequestBody.create(
                MediaType.parse("application/json"),
                JSONObject.toJSONString(autoReq)
        );
        autoReq.setRequestId(reqId);
        return new Request.Builder().url(url).post(body).build();
    }

    private GptProcessResult buildDefaultAutobotsResult(AgentRequest autoReq, String errMsg) {
        GptProcessResult result = new GptProcessResult();
        boolean isRouter = AgentType.ROUTER.getValue().equals(autoReq.getAgentType());
        if (isRouter) {
            result.setStatus("success");
            result.setFinished(true);
            result.setResponse(errMsg);
            result.setTraceId(autoReq.getRequestId());
        } else {
            result.setResultMap(new HashMap<>());
            result.setStatus("failed");
            result.setFinished(true);
            result.setErrorMsg(errMsg);
        }
        return result;
    }

    private AgentRequest buildAgentRequest(GptQueryReq req) {
        AgentRequest request = new AgentRequest();
        request.setRequestId(req.getTraceId());
        request.setSessionId(req.getSessionId());
        request.setErp(req.getUser());
        request.setQuery(req.getQuery());
        request.setAgentType(req.getDeepThink() == 0 ? 5: 3);
        request.setSopPrompt(request.getAgentType() == 3 ? genieConfig.getGenieSopPrompt(): "");
        request.setBasePrompt(request.getAgentType() == 5 ? genieConfig.getGenieBasePrompt() : "");
        request.setIsStream(true);
        request.setOutputStyle(req.getOutputStyle());

        return request;
    }


    private GptProcessResult buildHeartbeatData(String requestId) {
        GptProcessResult result = new GptProcessResult();
        result.setFinished(false);
        result.setStatus("success");
        result.setResponseType(ResponseTypeEnum.text.name());
        result.setResponse("");
        result.setResponseAll("");
        result.setUseTimes(0);
        result.setUseTokens(0);
        result.setReqId(requestId);
        result.setPackageType("heartbeat");
        result.setEncrypted(false);
        return result;
    }
}
