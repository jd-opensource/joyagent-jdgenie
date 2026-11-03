package com.jd.genie.data.jdbc.connection;

import com.jd.genie.data.jdbc.catalog.JdbcCatalog;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import javax.sql.DataSource;

@Slf4j
@Data
public class DatasourceWrapper implements AutoCloseable {

    private DataSource dataSource;

    private JdbcDialect jdbcDialect;

    private JdbcCatalog catalog;

    private Long freshTime;

    @Override
    public void close() {
        if (dataSource instanceof AutoCloseable) {
            try {
                ((AutoCloseable) dataSource).close();
            } catch (Exception e) {
                log.warn("关闭 DataSource 失败", e);
            }
        }
    }
}
