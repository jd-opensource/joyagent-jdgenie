package com.jd.genie.agent.integration;

import com.jd.genie.agent.agent.AgentContext;
import com.jd.genie.agent.dto.Memory;
import com.jd.genie.agent.dto.Message;
import com.jd.genie.agent.enums.RoleType;
import com.jd.genie.agent.llm.LLM;
import lombok.extern.slf4j.Slf4j;
import org.junit.jupiter.api.Disabled;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.SpringBootTest;

import java.util.Collections;
import java.util.concurrent.CompletableFuture;

import static org.junit.jupiter.api.Assertions.*;

@Slf4j
@SpringBootTest
@Disabled("需要真实 LLM API，默认禁用")
class ImageUrlIntegrationTest {

    /**
     * 测试使用图片 URL 分析京东 Logo
     */
    @Test
    void testAnalyzeJDLogoWithImageUrl() throws Exception {
        log.info("=== 开始测试：使用图片 URL 分析京东 Logo ===");
        
        // 1. 准备测试数据
        String imageUrl = "https://m.360buyimg.com/babel/jfs/t20280615/318148/22/9216/14627/684fdc85Fa154b4e0/0742847dfed41e81.png";
        String query = "这张图片里是什么？请描述你看到的内容。";
        
        // 2. 创建 Agent 上下文
        AgentContext context = new AgentContext();
        context.setRequestId("test-image-url-" + System.currentTimeMillis());
        
        // 3. 创建带图片 URL 的消息
        Message userMessage = Message.userMessageWithImageUrl(query, imageUrl);
        log.info("创建消息成功 - Content: {}, ImageUrl: {}", query, imageUrl);
        
        // 4. 创建 LLM 实例（使用配置中的模型）
        LLM llm = new LLM("gpt-4-vision-preview", "test-user");
        
        // 5. 调用 LLM 分析图片
        log.info("开始调用 LLM 分析图片...");
        CompletableFuture<String> future = llm.ask(
            context,
            Collections.singletonList(userMessage),
            Collections.emptyList(),
            false,
            0.7
        );
        
        // 6. 获取分析结果
        String result = future.get();
        log.info("=== LLM 分析结果 ===");
        log.info(result);
        log.info("===================");
        
        // 7. 验证结果
        assertNotNull(result, "分析结果不应为空");
        assertFalse(result.isEmpty(), "分析结果不应为空字符串");
        
        // 期望结果包含京东相关的关键词
        String resultLower = result.toLowerCase();
        boolean hasJDKeyword = resultLower.contains("jd") 
                            || resultLower.contains("京东") 
                            || resultLower.contains("logo")
                            || resultLower.contains("标志");
        
        assertTrue(hasJDKeyword, "分析结果应包含京东相关关键词，实际结果：" + result);
        
        log.info("=== 测试通过 ===");
    }

    /**
     * 测试 Memory 中的图片 URL 消息
     */
    @Test
    void testMemoryWithImageUrl() {
        log.info("=== 测试 Memory 中的图片 URL ===");
        
        Memory memory = new Memory();
        
        String imageUrl = "https://m.360buyimg.com/babel/jfs/t20280615/318148/22/9216/14627/684fdc85Fa154b4e0/0742847dfed41e81.png";
        String content = "分析这个 Logo";
        
        // 使用工厂方法创建带 URL 的消息
        Message message = Message.userMessageWithImageUrl(content, imageUrl);
        memory.addMessage(message);
        
        // 验证记忆
        assertEquals(1, memory.size(), "应该有一条记忆");
        
        Message savedMessage = memory.get(0);
        assertEquals(RoleType.USER, savedMessage.getRole(), "角色应该是 USER");
        assertEquals(content, savedMessage.getContent(), "内容应该匹配");
        assertEquals(imageUrl, savedMessage.getImageUrl(), "ImageUrl 应该匹配");
        assertNull(savedMessage.getBase64Image(), "不应该有 base64 数据");
        assertTrue(savedMessage.hasImage(), "应该识别为有图片");
        assertTrue(savedMessage.isImageUrl(), "应该识别为 URL 类型");
        
        log.info("=== Memory 测试通过 ===");
    }

}
