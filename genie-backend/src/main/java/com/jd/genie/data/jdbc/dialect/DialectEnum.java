package com.jd.genie.data.jdbc.dialect;

import lombok.Getter;
import org.apache.commons.lang3.StringUtils;

@Getter
public enum DialectEnum {
    MYSQL("MySql", "jdbc:mysql://", "/", ""),
    H2("h2", "jdbc:h2:mem", ":", ";MODE=MySQL"),
    CLICKHOUSE("ClickHouse", "jdbc:clickhouse://", "/", ""),
    DORIS("Doris", "jdbc:mysql://", "/", "");

    private final String name;
    private final String urlPrefix;
    private final String suffixDelimiter;
    private final String urlEndWith;

    DialectEnum(String name, String urlPrefix, String suffixDelimiter, String urlEndWith) {
        this.name = name;
        this.urlPrefix = urlPrefix;
        this.suffixDelimiter = suffixDelimiter;
        this.urlEndWith = urlEndWith;
    }

    public static DialectEnum of(String dialectName) {
        DialectEnum[] dialectEnums = DialectEnum.class.getEnumConstants();

        for (DialectEnum dialectEnum : dialectEnums) {
            if (StringUtils.equalsIgnoreCase(dialectName, dialectEnum.name)) {
                return dialectEnum;
            }
        }

        throw new IllegalArgumentException("不支持的数据源类型:" + dialectName);
    }

}
