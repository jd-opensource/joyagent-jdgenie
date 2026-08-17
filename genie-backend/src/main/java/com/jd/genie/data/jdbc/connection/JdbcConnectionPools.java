package com.jd.genie.data.jdbc.connection;

import com.jd.genie.data.jdbc.JdbcConnectionConfig;
import lombok.extern.slf4j.Slf4j;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;

@Slf4j
public class JdbcConnectionPools {

    private static final int DEFAULT_INITIAL_CAPACITY = 16;

    private static JdbcConnectionPoolFactory jdbcConnectionPoolFactory;
    private final Map<String, DatasourceWrapper> pools;
    private final ReentrantReadWriteLock lock = new ReentrantReadWriteLock();

    private JdbcConnectionPools() {
        this.pools = new ConcurrentHashMap<>(DEFAULT_INITIAL_CAPACITY);
    }

    private static class SingletonHolder {
        private static final JdbcConnectionPools INSTANCE;

        static {
            try {
                jdbcConnectionPoolFactory = new JdbcConnectionPoolFactory();
                INSTANCE = new JdbcConnectionPools();
                log.info("JdbcConnectionPools 初始化完成");
            } catch (Exception e) {
                log.error("JdbcConnectionPools 初始化失败", e);
                throw new ExceptionInInitializerError(e);
            }
        }
    }

    public static JdbcConnectionPools getInstance() {
        return SingletonHolder.INSTANCE;
    }

    public DatasourceWrapper getOrCreateConnectionPool(JdbcConnectionConfig config) {

        if (!config.isCachePools()) {
            log.info("创建无缓存的数据源连接池");
            return createNewDatasource(config);
        }

        String poolId = config.getKey();

        // 先尝试读锁获取
        lock.readLock().lock();
        try {
            DatasourceWrapper existingWrapper = pools.get(poolId);
            if (existingWrapper != null && noNeedsRefresh(existingWrapper, config.getFreshTimestamp())) {
                log.info("从缓存获取连接池 poolId {}", poolId);
                return existingWrapper;
            }
        } finally {
            lock.readLock().unlock();
        }

        lock.writeLock().lock();
        try {
            DatasourceWrapper existingWrapper = pools.get(poolId);
            if (existingWrapper != null && noNeedsRefresh(existingWrapper, config.getFreshTimestamp())) {
                log.info("再次从缓存获取连接池 poolId {}", poolId);
                return existingWrapper;
            }

            log.info("连接池需要刷新或创建，poolId: {}", poolId);
            return refreshDatasource(config);
        } finally {
            lock.writeLock().unlock();
        }
    }

    private boolean noNeedsRefresh(DatasourceWrapper wrapper, Long freshTimestamp) {
        if (freshTimestamp == null) {
            return true;
        }

        Long oldFreshTime = wrapper.getFreshTime();
        boolean needRefresh = oldFreshTime == null || oldFreshTime < freshTimestamp;

        if (needRefresh) {
            log.info("数据连接需要更新. old-time: {}, new-time: {}", oldFreshTime, freshTimestamp);
        }

        return !needRefresh;
    }


    private DatasourceWrapper refreshDatasource(JdbcConnectionConfig config) {
        String poolId = config.getKey();

        // 创建新的数据源
        DatasourceWrapper newWrapper = createNewDatasource(config);
        DatasourceWrapper oldWrapper = pools.put(poolId, newWrapper);

        // 关闭被替换的旧连接池，避免物理连接与线程泄漏
        if (oldWrapper != null && oldWrapper != newWrapper) {
            oldWrapper.close();
        }

        log.info("数据源刷新完成 poolId {}", poolId);
        return newWrapper;
    }

    private DatasourceWrapper createNewDatasource(JdbcConnectionConfig config) {
        try {
            return jdbcConnectionPoolFactory.createPooledDatasource(config);
        } catch (Exception e) {
            log.error("创建数据源失败, config: {}", config, e);
            throw new RuntimeException("创建数据源失败", e);
        }
    }
}
