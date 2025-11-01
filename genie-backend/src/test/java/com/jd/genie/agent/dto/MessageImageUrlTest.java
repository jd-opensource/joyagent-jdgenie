package com.jd.genie.agent.dto;

import com.jd.genie.agent.enums.RoleType;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Message 图片 URL 支持测试
 */
class MessageImageUrlTest {

    @Test
    void testUserMessageWithImageUrl() {
        // 测试创建带 URL 图片的用户消息
        String content = "请分析这张图片";
        String imageUrl = "https://example.com/result.jpg";
        Message msg = Message.userMessageWithImageUrl(content, imageUrl);
        
        assertNotNull(msg, "Message should not be null");
        assertEquals(RoleType.USER, msg.getRole(), "Role should be USER");
        assertEquals(content, msg.getContent(), "Content should match");
        assertEquals(imageUrl, msg.getImageUrl(), "ImageUrl should match");
        assertNull(msg.getBase64Image(), "Base64Image should be null");
    }

    @Test
    void testAssistantMessageWithImageUrl() {
        // 测试创建带 URL 图片的助手消息
        String content = "这是分析结果";
        String imageUrl = "https://example.com/result.jpg";
        
        Message msg = Message.assistantMessageWithImageUrl(content, imageUrl);
        
        assertEquals(RoleType.ASSISTANT, msg.getRole());
        assertEquals(imageUrl, msg.getImageUrl());
    }

    @Test
    void testHasImage_withImageUrl() {
        // 测试 hasImage() 方法 - URL 方式
        Message msg = Message.userMessageWithImageUrl("test", "https://example.com/img.jpg");
        assertTrue(msg.hasImage(), "Should have image");
    }

    @Test
    void testHasImage_withBase64() {
        // 测试 hasImage() 方法 - Base64 方式
        Message msg = Message.userMessage("test", "base64String");
        
        assertTrue(msg.hasImage(), "Should have image");
    }

    @Test
    void testHasImage_withoutImage() {
        // 测试 hasImage() 方法 - 无图片
        Message msg = Message.userMessage("test", null);
        
        assertFalse(msg.hasImage(), "Should not have image");
    }

    @Test
    void testIsImageUrl_true() {
        // 测试 isImageUrl() 方法 - 返回 true
        Message msg = Message.userMessageWithImageUrl("test", "https://example.com/img.jpg");
        
        assertTrue(msg.isImageUrl(), "Should be image URL");
    }

    @Test
    void testIsImageUrl_false() {
        // 测试 isImageUrl() 方法 - 返回 false
        Message msg = Message.userMessage("test", "base64String");
        
        assertFalse(msg.isImageUrl(), "Should not be image URL");
    }

    @Test
    void testBackwardCompatibility_base64() {
        // 测试向后兼容性 - base64 方式仍然可用
        String content = "旧代码";
        String base64 = "iVBORw0KGgoAAAANS...";
        
        Message msg = Message.userMessage(content, base64);
        
        assertEquals(RoleType.USER, msg.getRole());
        assertEquals(content, msg.getContent());
        assertEquals(base64, msg.getBase64Image());
        assertNull(msg.getImageUrl(), "ImageUrl should be null for old API");
        assertTrue(msg.hasImage(), "Should have image");
        assertFalse(msg.isImageUrl(), "Should not be URL type");
    }

    @Test
    void testBothImageTypes() {
        // 测试同时设置两种图片（通过 builder）
        String content = "测试";
        String base64 = "base64String";
        String imageUrl = "https://example.com/img.jpg";
        
        Message msg = Message.builder()
                .role(RoleType.USER)
                .content(content)
                .base64Image(base64)
                .imageUrl(imageUrl)
                .build();
        
        assertTrue(msg.hasImage(), "Should have image");
        assertTrue(msg.isImageUrl(), "Should be URL type (URL takes precedence)");
        assertEquals(imageUrl, msg.getImageUrl());
        assertEquals(base64, msg.getBase64Image());
    }

    @Test
    void testEmptyImageUrl() {
        // 测试空字符串 URL
        Message msg = Message.builder()
                .role(RoleType.USER)
                .content("test")
                .imageUrl("")
                .build();
        
        assertFalse(msg.hasImage(), "Empty URL should not count as image");
        assertFalse(msg.isImageUrl(), "Empty URL should return false");
    }

    @Test
    void testNullImageUrl() {
        // 测试 null URL
        Message msg = Message.builder()
                .role(RoleType.USER)
                .content("test")
                .imageUrl(null)
                .build();
        
        assertFalse(msg.hasImage(), "Null URL should not count as image");
        assertFalse(msg.isImageUrl(), "Null URL should return false");
    }
}
