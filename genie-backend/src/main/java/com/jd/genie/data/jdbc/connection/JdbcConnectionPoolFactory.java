package com.jd.genie.data.jdbc.connection;

import com.jd.genie.data.exception.JdbcBizException;
import com.jd.genie.data.jdbc.JdbcConnectionConfig;
import com.jd.genie.data.jdbc.catalog.JdbcCatalog;
import com.jd.genie.data.jdbc.catalog.JdbcCatalogLoader;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;
import com.jd.genie.data.jdbc.dialect.JdbcDialectLoader;
import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;
import lombok.extern.slf4j.Slf4j;

import javax.sql.DataSource;
import java.io.Serializable;
import java.util.Properties;

@Slf4j
public class JdbcConnectionPoolFactory implements Serializable {

    private static final long serialVersionUID = 8831447217680924931L;


    public static final String CONNECTION_POOL_PREFIX = "dataAgent-connection-pool-";


    public DatasourceWrapper createPooledDatasource(JdbcConnectionConfig connConfig) {
        JdbcDialect jdbcDialect = JdbcDialectLoader.load(connConfig.getUrl());
        DatasourceWrapper datasourceWrapper = new DatasourceWrapper();
        datasourceWrapper.setJdbcDialect(jdbcDialect);
        JdbcCatalog catalog = JdbcCatalogLoader.load(jdbcDialect.dialectName());
        datasourceWrapper.setCatalog(catalog);
        datasourceWrapper.setFreshTime(connConfig.getFreshTimestamp());

        //set jdbc dialect
        connConfig.setJdbcDialect(jdbcDialect.dialectName());
        switch (connConfig.getJdbcDialect()) {
            case MYSQL:
            case H2:
            case DORIS:
            case CLICKHOUSE:
                datasourceWrapper.setDataSource(createHikariDatasource(connConfig, jdbcDialect));
                break;
            default:
                throw new JdbcBizException(String.format("%s 暂不支持", connConfig.getJdbcDialect()));
        }
        return datasourceWrapper;
    }

    private DataSource createHikariDatasource(JdbcConnectionConfig connConfig, JdbcDialect jdbcDialect) {
        HikariConfig config = new HikariConfig();
        config.setPoolName(CONNECTION_POOL_PREFIX + connConfig.getKey());
        config.setDriverClassName(jdbcDialect.driverName());
        config.setUsername(connConfig.getUserName());
        config.setPassword(connConfig.getPassword());
        config.setJdbcUrl(connConfig.getUrl());

        if (connConfig.getReadOnly() != null) {
            config.setReadOnly(connConfig.getReadOnly());
        }
        if (connConfig.getConnectionTimeout() != null) {
            config.setConnectionTimeout((connConfig.getConnectionTimeout()));
        }
        if (connConfig.getIdleTimeout() != null) {
            config.setIdleTimeout(connConfig.getIdleTimeout());

        }
        if (connConfig.getMaxLifetime() != null) {
            config.setMaxLifetime(connConfig.getMaxLifetime());
        }
        if (connConfig.getMaxPoolSize() != null) {
            config.setMaximumPoolSize(connConfig.getMaxPoolSize());
        }
        if (connConfig.getMinIdle() != null) {
            config.setMinimumIdle(connConfig.getMinIdle());
        }
        if (connConfig.getKeepAliveTime() != null) {
            config.setKeepaliveTime(connConfig.getKeepAliveTime());
        }
        //方言配置
        config.setConnectionTestQuery(jdbcDialect.testSql());
        Properties properties = jdbcDialect.defaultProperties();
        if (properties != null) {
            for (String name : properties.stringPropertyNames()) {
                config.addDataSourceProperty(name, properties.getProperty(name));
            }
        }
        //jdbc 数据库配置
        Properties extConfig = connConfig.getExtConfig();
        if (extConfig != null) {
            for (String name : extConfig.stringPropertyNames()) {
                config.addDataSourceProperty(name, extConfig.getProperty(name));
            }
        }
        return new HikariDataSource(config);
    }
}
