
package com.jd.genie.data.jdbc.catalog.doris;


import com.jd.genie.data.SimpleTable;
import com.jd.genie.data.TableColumn;
import com.jd.genie.data.exception.CatalogException;
import com.jd.genie.data.jdbc.catalog.AbstractJdbcCatalog;
import com.jd.genie.data.model.StandardColumnType;
import lombok.extern.slf4j.Slf4j;

import java.sql.*;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

@Slf4j
public class DorisCatalog extends AbstractJdbcCatalog {

    protected static final Set<String> SYS_DATABASES = new HashSet<>(4);
    private static final String SELECT_COLUMNS_SQL_TEMPLATE =
            "SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA IN  ('%s') AND TABLE_NAME ='%s' ORDER BY ORDINAL_POSITION ASC";

    static {
        SYS_DATABASES.add("information_schema");
        SYS_DATABASES.add("mysql");
        SYS_DATABASES.add("performance_schema");
        SYS_DATABASES.add("sys");
    }

    @Override
    public List<SimpleTable> listTables(Connection connection, String schema) throws CatalogException {
        String sql = "show tables ";
        try (PreparedStatement prepared = connection.prepareStatement(sql);
             ResultSet rs = prepared.executeQuery()) {
            List<SimpleTable> tables = new ArrayList<>();
            while (rs.next()) {
                SimpleTable st = new SimpleTable();
                st.setTableName(rs.getString(1));
                tables.add(st);
            }
            return tables;
        } catch (SQLException e) {
            throw new CatalogException("获取数据库表失败", e);
        }
    }

    public String typeConvertMysql(String type) {
        return switch (type) {
            case "DATE", "TIME", "TIMESTAMP" -> StandardColumnType.DATE.name();
            case "TINYINT", "SMALLINT", "INTEGER", "BIGINT", "FLOAT", "DOUBLE", "NUMERIC", "DECIMAL" ->
                    StandardColumnType.DECIMAL.name();
            default -> StandardColumnType.VARCHAR.name();
        };
    }

    @Override
    public List<TableColumn> getTableColumns(Connection connection, String tablePath, String schema) throws CatalogException {
        String sql = String.format(
                SELECT_COLUMNS_SQL_TEMPLATE, schema, tablePath);

        try (Statement prepared = connection.createStatement();
             ResultSet rs = prepared.executeQuery(sql)) {
            int i = 1;
            List<TableColumn> columnList = new ArrayList<>();
            while (rs.next()) {
                String columnName = rs.getString("COLUMN_NAME");
                String jdbcDataType = rs.getString("DATA_TYPE").toUpperCase();
                String dataType = typeConvertMysql(jdbcDataType);
                String comment = rs.getString("COLUMN_COMMENT");
                TableColumn column = TableColumn.builder().name(columnName)
                        .comment(comment)
                        .dataType(dataType)
                        .originDataType(jdbcDataType)
                        .nullable(rs.getBoolean("Is_NULLABLE"))
                        .position(i++)
                        .build();
                columnList.add(column);
            }
            return columnList;

        } catch (Exception e) {
            throw new CatalogException(
                    String.format("获取表字段信息失败 %s", tablePath), e);
        }
    }
}
