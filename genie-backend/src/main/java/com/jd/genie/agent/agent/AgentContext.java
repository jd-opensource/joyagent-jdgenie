package com.jd.genie.agent.agent;

import com.jd.genie.agent.dto.File;
import com.jd.genie.agent.printer.Printer;
import com.jd.genie.agent.tool.ToolCollection;
import com.jd.genie.model.dto.FileInformation;
import com.jd.genie.model.req.AgentRequest;
import lombok.*;
import lombok.extern.slf4j.Slf4j;

import java.util.List;

@Getter
@Setter
@Builder
@Slf4j
@NoArgsConstructor
@AllArgsConstructor
public class AgentContext {
    String requestId;
    String sessionId;
    String query;
    String task;
    Printer printer;
    ToolCollection toolCollection;
    String dateInfo;
    List<File> productFiles;
    Boolean isStream;
    String streamMessageType;
    String sopPrompt;
    String basePrompt;
    Integer agentType;
    List<File> taskProductFiles;
}