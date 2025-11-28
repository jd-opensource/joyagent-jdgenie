package com.jd.genie.config;

import jakarta.annotation.PreDestroy;
import lombok.extern.slf4j.Slf4j;
import okhttp3.ConnectionPool;
import okhttp3.OkHttpClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.concurrent.TimeUnit;

/**
 * OkHttpClient 配置类
 * 将 OkHttpClient 作为单例 Bean 管理，避免重复创建，提高性能和资源利用率
 */
@Slf4j
@Configuration
public class OkHttpClientConfig {

    @Autowired
    private GenieConfig genieConfig;

    private OkHttpClient okHttpClient;

    /**
     * 创建单例 OkHttpClient Bean
     * 
     * 优化点：
     * 1. 使用单例模式，避免每次请求都创建新的 client
     * 2. 配置连接池，支持连接复用（HTTP Keep-Alive）
     * 3. 统一超时配置管理
     * 
     * @return OkHttpClient 实例
     */
    @Bean
    public OkHttpClient okHttpClient() {
        log.info("Initializing OkHttpClient singleton bean");
        
        // 配置连接池：最多保持 10 个空闲连接，每个连接最多保活 5 分钟
        ConnectionPool connectionPool = new ConnectionPool(
                10,                    // 最大空闲连接数
                5,                     // 连接保活时间
                TimeUnit.MINUTES       // 时间单位
        );

        okHttpClient = new OkHttpClient.Builder()
                .connectTimeout(60, TimeUnit.SECONDS)
                .readTimeout(genieConfig.getSseClientReadTimeout(), TimeUnit.SECONDS)
                .writeTimeout(1800, TimeUnit.SECONDS)
                .callTimeout(genieConfig.getSseClientConnectTimeout(), TimeUnit.SECONDS)
                .connectionPool(connectionPool)
                .retryOnConnectionFailure(true)  // 连接失败时自动重试
                .build();

        log.info("OkHttpClient initialized successfully with connection pool (max idle: 10, keep-alive: 5min)");
        return okHttpClient;
    }

    /**
     * 应用关闭时优雅关闭 OkHttpClient
     * 释放连接池、线程池等资源
     */
    @PreDestroy
    public void destroy() {
        if (okHttpClient != null) {
            log.info("Shutting down OkHttpClient resources...");
            
            // 关闭连接池
            okHttpClient.connectionPool().evictAll();
            
            // 关闭调度器线程池
            if (okHttpClient.dispatcher() != null && okHttpClient.dispatcher().executorService() != null) {
                okHttpClient.dispatcher().executorService().shutdown();
            }
            
            log.info("OkHttpClient resources released successfully");
        }
    }
}
