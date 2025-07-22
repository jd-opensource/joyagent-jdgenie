package com.jd.genie.agent.llm;

import com.jd.genie.agent.util.SpringContextHolder;
import com.jd.genie.config.GenieConfig;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.config.YamlPropertiesFactoryBean;
import org.springframework.context.ApplicationContext;
import org.springframework.core.io.ClassPathResource;
import org.springframework.core.io.Resource;

import java.util.Objects;
import java.util.Properties;


/**
 * 配置工具类
 */
@Slf4j
public class Config {
    /**
     * 获取 LLM 配置
     */
    public static LLMSettings getLLMConfig(String modelName) {
        ApplicationContext applicationContext = SpringContextHolder.getApplicationContext();
        GenieConfig genieConfig = applicationContext.getBean(GenieConfig.class);
        if (Objects.nonNull(genieConfig.getLlmSettingsMap())) {
            return genieConfig.getLlmSettingsMap().getOrDefault(modelName, getDefaultConfig());
        }
        return getDefaultConfig();
    }

    /**
     * 加载 LLM 配置
     */
    private static LLMSettings getDefaultConfig() {

        Resource resource = new ClassPathResource("application.yml");
        YamlPropertiesFactoryBean yamlFactory = new YamlPropertiesFactoryBean();
        yamlFactory.setResources(resource);
        Properties props = yamlFactory.getObject();

        // 创建默认配置
        return LLMSettings.builder()
                .model(props.getProperty("llm.default.model", "gpt-4o-0806"))
                .maxTokens(Integer.parseInt(props.getProperty("llm.default.max_tokens", "16384")))
                .temperature(Double.parseDouble(props.getProperty("llm.default.temperature", "0")))
                .apiType(props.getProperty("llm.default.api_type", "openai"))
                .baseUrl(props.getProperty("llm.default.base_url", ""))
                .interfaceUrl(props.getProperty("llm.default.interface_url", "/v1/chat/completions"))
                .functionCallType(props.getProperty("llm.default.function_call_type", "function_call"))
                .apiKey(props.getProperty("llm.default.apikey", ""))
                .apiVersion(props.getProperty("llm.default.api_version", "2025-01-01-preview"))
                .maxInputTokens(Integer.parseInt(props.getProperty("llm.default.max_input_tokens", "100000")))
                .build();
    }
}
