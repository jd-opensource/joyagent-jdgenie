package com.jd.genie.service.impl;

import okhttp3.OkHttpClient;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;

import static org.junit.jupiter.api.Assertions.*;

/**
 * OkHttpClient 集成测试
 * 验证单例模式在实际应用上下文中的表现
 */
@SpringBootTest
class OkHttpClientIntegrationTest {

    @Autowired
    private ApplicationContext applicationContext;

    @Autowired
    private OkHttpClient okHttpClient;

    @Test
    void testOkHttpClientBeanExistsInContext() {
        // 验证 Bean 存在于 Spring 上下文中
        assertTrue(applicationContext.containsBean("okHttpClient"),
                "OkHttpClient bean should exist in application context");
    }

    @Test
    void testOkHttpClientIsSingletonInContext() {
        // 从上下文获取两次，验证是同一个实例
        OkHttpClient client1 = applicationContext.getBean(OkHttpClient.class);
        OkHttpClient client2 = applicationContext.getBean(OkHttpClient.class);

        assertSame(client1, client2,
                "Multiple retrievals should return the same singleton instance");
    }

    @Test
    void testOkHttpClientSingletonAcrossMultipleInjections() {
        // 验证注入的实例与从上下文获取的实例是同一个
        OkHttpClient fromContext = applicationContext.getBean(OkHttpClient.class);

        assertSame(okHttpClient, fromContext,
                "Injected client should be the same as the one from context");
    }

    @Test
    void testConnectionPoolSharedAcrossSingleton() {
        // 验证连接池是共享的
        OkHttpClient client1 = applicationContext.getBean(OkHttpClient.class);
        OkHttpClient client2 = applicationContext.getBean(OkHttpClient.class);

        assertSame(client1.connectionPool(), client2.connectionPool(),
                "Connection pool should be shared across singleton instances");
    }

    @Test
    void testDispatcherSharedAcrossSingleton() {
        // 验证调度器是共享的
        OkHttpClient client1 = applicationContext.getBean(OkHttpClient.class);
        OkHttpClient client2 = applicationContext.getBean(OkHttpClient.class);

        assertSame(client1.dispatcher(), client2.dispatcher(),
                "Dispatcher should be shared across singleton instances");
    }

    @Test
    void testOkHttpClientConfiguration() {
        // 验证配置正确
        assertNotNull(okHttpClient.connectionPool(), "Connection pool should be configured");
        assertNotNull(okHttpClient.dispatcher(), "Dispatcher should be configured");

        // 验证超时配置
        assertTrue(okHttpClient.connectTimeoutMillis() == 60000,
                "Connect timeout should be 60 seconds");

        // 验证重试配置
        assertTrue(okHttpClient.retryOnConnectionFailure(),
                "Retry on connection failure should be enabled");
    }

    @Test
    void testConnectionPoolConfiguration() {
        // 验证连接池有合理的配置
        assertNotNull(okHttpClient.connectionPool(), "Connection pool should exist");

        // 连接池应该被正确初始化
        assertEquals(0, okHttpClient.connectionPool().connectionCount(),
                "Initially, connection count should be 0");
    }
}
