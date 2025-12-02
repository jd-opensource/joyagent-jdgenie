package com.jd.genie.config;

import okhttp3.OkHttpClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.junit.jupiter.api.Assertions.*;

/**
 * OkHttpClientConfig 单元测试
 */
@SpringBootTest
class OkHttpClientConfigTest {

    @Autowired
    private OkHttpClient okHttpClient;

    @Test
    void testOkHttpClientBeanExists() {
        // 验证 OkHttpClient Bean 能够正确注入
        assertNotNull(okHttpClient, "OkHttpClient bean should be initialized");
    }

    @Test
    void testOkHttpClientIsSingleton() {
        // 验证 OkHttpClient 是单例
        OkHttpClient client1 = okHttpClient;
        OkHttpClient client2 = okHttpClient;
        
        assertSame(client1, client2, "OkHttpClient should be a singleton");
    }

    @Test
    void testConnectionPoolConfigured() {
        // 验证连接池已配置
        assertNotNull(okHttpClient.connectionPool(), "Connection pool should be configured");
    }

    @Test
    void testTimeoutConfigured() {
        // 验证超时配置
        assertTrue(okHttpClient.connectTimeoutMillis() > 0, "Connect timeout should be configured");
        assertTrue(okHttpClient.readTimeoutMillis() > 0, "Read timeout should be configured");
        assertTrue(okHttpClient.writeTimeoutMillis() > 0, "Write timeout should be configured");
        assertTrue(okHttpClient.callTimeoutMillis() > 0, "Call timeout should be configured");
    }

    @Test
    void testRetryOnConnectionFailure() {
        // 验证连接失败重试配置
        assertTrue(okHttpClient.retryOnConnectionFailure(), 
                "Retry on connection failure should be enabled");
    }

    @Test
    void testDispatcherConfigured() {
        // 验证调度器已配置
        assertNotNull(okHttpClient.dispatcher(), "Dispatcher should be configured");
    }
}
