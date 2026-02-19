package com.jd.genie.data.sql.dialect;

import com.jd.genie.data.jdbc.dialect.DialectEnum;
import org.apache.calcite.sql.SqlDialect;

public class SqlDialectUtil {

    public static SqlDialect fromDialectString(String dialectString) {
        DialectEnum dialectEnum = DialectEnum.of(dialectString);
        return switch (dialectEnum) {
            case H2,MYSQL -> MysqlCustomSqlDialect.DEFAULT;
            case CLICKHOUSE -> ClickHouseSqlDialect2.DEFAULT;
            case DORIS -> DorisSqlDialect.DEFAULT;
        };
    }
}
