package com.jd.genie.data.jdbc.connection;

import com.jd.genie.data.jdbc.JdbcConnectionConfig;
import com.zaxxer.hikari.HikariDataSource;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotSame;
import static org.junit.jupiter.api.Assertions.assertTrue;

class JdbcConnectionPoolsTest {

    /**
     * issue #407: 刷新数据源后，被替换的旧连接池必须被显式关闭，
     * 否则 HikariCP 持有的 housekeeping 线程和空闲连接会一直泄漏。
     */
    @Test
    void refreshDatasourceShouldCloseReplacedPool() {
        JdbcConnectionPools pools = JdbcConnectionPools.getInstance();

        JdbcConnectionConfig config = new JdbcConnectionConfig();
        config.setKey("issue-407-test");
        config.setUrl("jdbc:h2:mem:issue407;DB_CLOSE_DELAY=-1");
        config.setUserName("sa");
        config.setPassword("");
        config.setCachePools(true);

        // 第一次获取：创建连接池
        config.setFreshTimestamp(1000L);
        DatasourceWrapper first = pools.getOrCreateConnectionPool(config);
        assertTrue(first.getDataSource() instanceof HikariDataSource);
        assertFalse(((HikariDataSource) first.getDataSource()).isClosed());

        // freshTimestamp 变化触发刷新：返回新连接池，旧的应被关闭
        config.setFreshTimestamp(2000L);
        DatasourceWrapper second = pools.getOrCreateConnectionPool(config);

        assertNotSame(first, second);
        assertFalse(((HikariDataSource) second.getDataSource()).isClosed());
        assertTrue(((HikariDataSource) first.getDataSource()).isClosed());
        assertEquals(second.getFreshTime(), Long.valueOf(2000L));
    }
}
