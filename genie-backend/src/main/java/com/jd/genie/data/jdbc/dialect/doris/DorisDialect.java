package com.jd.genie.data.jdbc.dialect.doris;



import com.jd.genie.data.jdbc.dialect.DialectEnum;
import com.jd.genie.data.jdbc.dialect.mysql.MysqlDialect;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;
import java.util.Properties;

public class DorisDialect extends MysqlDialect {
    
    @Override
    public DialectEnum dialectName() {
        return DialectEnum.DORIS;
    }

    @Override
    public String driverName() {
        return "com.mysql.jdbc.Driver";
    }

    @Override
    public Properties defaultProperties() {
        Properties properties = super.defaultProperties();
        
        // 保留MySQL的基础配置
        properties.setProperty("remarks", "true");
        properties.setProperty("useInformationSchema", "true");
        
        // 添加Doris特有优化
        properties.setProperty("connectTimeout", "10000");
        properties.setProperty("socketTimeout", "30000");
        properties.setProperty("zeroDateTimeBehavior", "convertToNull");
        
        // 性能优化
        properties.setProperty("useServerPrepStmts", "false");
        properties.setProperty("rewriteBatchedStatements", "true");
        properties.setProperty("cachePrepStmts", "true");
        
        return properties;
    }
    @Override
    public String testSql() {
        return "SELECT 1";
    }
    
    
    
}