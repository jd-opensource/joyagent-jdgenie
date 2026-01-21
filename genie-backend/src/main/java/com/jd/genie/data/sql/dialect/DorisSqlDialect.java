package com.jd.genie.data.sql.dialect;

import org.apache.calcite.sql.SqlDialect;
import org.apache.calcite.sql.dialect.MysqlSqlDialect;
import org.checkerframework.checker.nullness.qual.Nullable;

public class DorisSqlDialect extends MysqlCustomSqlDialect {

    public static final SqlDialect DEFAULT = new DorisSqlDialect();

    private DorisSqlDialect() {
        super(DEFAULT_CONTEXT);
    }

    // Doris 有特殊语法，可以 override 方法
}

