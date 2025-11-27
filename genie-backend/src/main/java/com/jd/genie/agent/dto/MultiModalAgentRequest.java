package com.jd.genie.agent.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class MultiModalAgentRequest {
    private String requestId;
    private String question;
    private String query;
    private Boolean stream;
    private Boolean contentStream;
    private Map<String, Object> streamMode;
}
