package com.jd.genie.data.jdbc.connection;

import com.jd.genie.data.jdbc.catalog.JdbcCatalog;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import javax.sql.DataSource;

@Data
@Slf4j
public class DatasourceWrapper implements AutoCloseable {

    private DataSource dataSource;

    private JdbcDialect jdbcDialect;

    private JdbcCatalog catalog;

    private Long freshTime;

    /**
     * 关闭底层连接池，释放物理连接与后台线程。
     * 连接池（如 HikariDataSource）持有非内存资源，必须显式 close，不能依赖 GC。
     */
    @Override
    public void close() {
        if (dataSource instanceof AutoCloseable) {
            try {
                ((AutoCloseable) dataSource).close();
            } catch (Exception e) {
                log.warn("关闭数据源失败", e);
            }
        }
    }
}
