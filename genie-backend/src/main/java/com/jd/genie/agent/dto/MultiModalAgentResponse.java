package com.jd.genie.agent.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MultiModalAgentResponse {
    private String id;
    private List<Choice> choices;
    private Long created;
    private String model;
    private String object;
    private String serviceTier;
    private String systemFingerprint;
    private Usage usage;
    
    // 兼容字段，用于统一处理
    private String data;
    private Boolean isFinal;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Choice {
        private Delta delta;
        private String finishReason;
        private Integer index;
        private Object logprobs;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Delta {
        private String content;
        private Object functionCall;
        private String refusal;
        private String role;
        private Object toolCalls;
    }

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class Usage {
        private Integer promptTokens;
        private Integer completionTokens;
        private Integer totalTokens;
    }
}