package com.jd.genie.data.sql;

import com.jd.genie.data.jdbc.dialect.DialectEnum;
import com.jd.genie.data.model.*;
import com.jd.genie.data.sql.dialect.ClickHouseSqlDialect2;
import com.jd.genie.data.sql.dialect.MysqlCustomSqlDialect;
import com.jd.genie.data.sql.dialect.SqlDialectUtil;
import lombok.NonNull;
import lombok.extern.slf4j.Slf4j;
import org.apache.calcite.avatica.util.Casing;
import org.apache.calcite.sql.*;
import org.apache.calcite.sql.fun.SqlLikeOperator;
import org.apache.calcite.sql.parser.SqlParseException;
import org.apache.calcite.sql.parser.SqlParser;
import org.apache.calcite.sql.util.SqlBasicVisitor;
import org.apache.calcite.sql.validate.SqlConformanceEnum;
import org.apache.commons.collections4.CollectionUtils;
import org.apache.commons.lang3.StringUtils;

import java.util.*;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
public class SqlParserUtils {

    public static final String DOT = "\\.";

    public static final String OR = "OR";
    public static final String AND = "AND";

    private SqlParserUtils() {
        throw new IllegalStateException("Utility class");
    }

    private static SqlParser.Config parserConfig(@NonNull String dialectString) {
        DialectEnum dialectEnum = DialectEnum.of(dialectString);
        return switch (dialectEnum) {
            case H2, MYSQL,DORIS -> MysqlCustomSqlDialect.DEFAULT.configureParser(SqlParser.config())
                    .withConformance(SqlConformanceEnum.MYSQL_5);
            case CLICKHOUSE -> ClickHouseSqlDialect2.DEFAULT.configureParser(SqlParser.config())
                    .withConformance(SqlConformanceEnum.LENIENT);
        };
    }

    public static SqlParser.Config parserConfigWithoutQuoted(@NonNull String dialectString) {
        return parserConfig(dialectString)
                .withQuotedCasing(Casing.UNCHANGED)
                .withUnquotedCasing(Casing.UNCHANGED)
                .withCaseSensitive(false);
    }

    public static boolean isSelectSql(String sql, String dialect) {
        SqlParser parser = SqlParser.create(sql, parserConfigWithoutQuoted(dialect));
        try {
            SqlNode node = parser.parseStmt();
            return isSelectNode(node);
        } catch (SqlParseException e) {
            log.error("sql parse error:", e);
            return false;
        }
    }

    public static boolean isAggregator(SqlBasicCall sqlBasicCall) {
        HasAggVisitor aggVisitor = new HasAggVisitor();
        sqlBasicCall.accept(aggVisitor);
        return aggVisitor.isAgg();
    }

    private static List<ModelColumn> parseSelectColumn(SqlSelect select, String dialect) {
        List<ModelColumn> list = new ArrayList<>(16);
        select.getSelectList().forEach(colum -> {
            ModelColumn modelColumn = new ModelColumn();
            if (SqlKind.AS.equals(colum.getKind())) {
                SqlBasicCall basicCall = (SqlBasicCall) colum;
                SqlNode leftNode = basicCall.getOperandList().get(0);
                if (leftNode instanceof SqlBasicCall) {
                    SqlBasicCall leftNodeCall = (SqlBasicCall) leftNode;
                    modelColumn.setAggregator(isAggregator(leftNodeCall));
                    if (SqlKind.OTHER_FUNCTION.equals(leftNode.getKind())) {
                        modelColumn.setFunctionName(leftNodeCall.getOperator().getName());
                        List<String> functionArgList = new ArrayList<>();
                        for (SqlNode sqlNode : leftNodeCall.getOperandList()) {
                            functionArgList.add(sqlNode.toString());
                        }
                        modelColumn.setFunctionArgList(functionArgList);
                    }
                }
                modelColumn.setColumnKind(leftNode.getKind().name());
                if (SqlKind.IDENTIFIER.equals(leftNode.getKind())) {
                    modelColumn.setColumnName(leftNode.toString());
                } else {
                    modelColumn.setColumnName(toSqlString(leftNode, dialect));
                }
                modelColumn.setColumnAlias(basicCall.getOperandList().get(1).toString());
            } else if (SqlKind.IDENTIFIER.equals(colum.getKind())) {
                modelColumn.setColumnName(colum.toString());
                modelColumn.setColumnKind(SqlKind.IDENTIFIER.name());
                SqlIdentifier identifier = (SqlIdentifier) colum;
                if (identifier.isStar()) {
                    modelColumn.setStar(true);
                    if (identifier.names.size() > 1) {
                        modelColumn.setTableAlias(identifier.names.get(0));
                    }
                } else {
                    String[] split = colum.toString().split(DOT);
                    modelColumn.setColumnAlias(split[split.length - 1]);
                }
            } else {
                modelColumn.setColumnName(toSqlString(colum, dialect));
                modelColumn.setColumnKind(colum.getKind().name());
            }
            list.add(modelColumn);
        });
        return list;
    }


    private static boolean isSelectNode(SqlNode node) {
        if (node.getKind() == SqlKind.ORDER_BY) {
            SqlOrderBy orderBy = (SqlOrderBy) node;
            return orderBy.query instanceof SqlSelect;
        } else {
            return node.getKind() == SqlKind.SELECT || node.getKind() == SqlKind.UNION;
        }
    }

    private static FromTable singleFromTable(SqlNode from) {
        FromTable table = new FromTable();
        if (SqlKind.AS.equals(from.getKind())) {
            SqlBasicCall basicCall = (SqlBasicCall) from;
            SqlNode tableNode = basicCall.getOperandList().get(0);
            if (isSelectNode(tableNode)) {
                table.setFromTableType(FromTableType.INNER_SQL);
            }
            table.setTableName(tableNode.toString());
            table.setTableAlias(basicCall.getOperandList().get(1).toString());
        } else {
            table.setFromTableType(FromTableType.TABLE);
            table.setTableName(from.toString());
        }
        return table;
    }

    public static WhereCondition parseSelectWhere(SqlNode node, String dialect) {
        WhereCondition whereCondition = new WhereCondition();
        SqlKind kind = node.getKind();
        if (node instanceof SqlBasicCall) {
            SqlBasicCall call = (SqlBasicCall) node;
            switch (kind) {
                case AND:
                case OR:
                    List<WhereCondition> whereConditionList = new ArrayList<>(call.getOperandList().size());
                    for (SqlNode operand : call.getOperandList()) {
                        whereConditionList.add(parseSelectWhere(operand, dialect));
                    }
                    whereCondition.setOperator(call.getOperator().getName());
                    whereCondition.setConditionList(whereConditionList);
                    break;
                case GREATER_THAN:
                case LESS_THAN:
                case GREATER_THAN_OR_EQUAL:
                case LESS_THAN_OR_EQUAL:
                case EQUALS:
                case NOT_EQUALS:
                case RLIKE:
                    if (call.getOperator() instanceof SqlLikeOperator && ((SqlLikeOperator) call.getOperator()).isNegated()) {
                        whereCondition.setNegaed(true);
                    }
                case LIKE:
                    if (call.getOperator() instanceof SqlLikeOperator && ((SqlLikeOperator) call.getOperator()).isNegated()) {
                        whereCondition.setNegaed(true);
                    }

                case IN:
                case NOT_IN:
                case IS_NULL:
                case IS_NOT_NULL:
                case BETWEEN:
                    SqlOperator comparison = call.getOperator();
                    whereCondition.setComparison(comparison.getName());
                    whereCondition.setComparisonType(comparison.getKind().toString());
                    List<SqlNode> operandList = call.getOperandList();
                    SqlNode leftNode = operandList.get(0);
                    if (SqlKind.IDENTIFIER.equals(leftNode.getKind())) {
                        whereCondition.setIdentifier(leftNode.toString());
                    } else if (SqlKind.LITERAL.equals(leftNode.getKind())) {
                        whereCondition.setIdentifier(((SqlLiteral) leftNode).toValue());
                    } else {
                        whereCondition.setIdentifier(toSqlString(leftNode, dialect));
                    }
                    whereCondition.setIdentifierKind(leftNode.getKind().name());
                    if (operandList.size() > 1) {
                        SqlNode rightNode = operandList.get(1);
                        whereCondition.setValueKind(rightNode.getKind().name());
                        if (rightNode instanceof SqlNodeList) {
                            List<String> valueList = new ArrayList<>();
                            for (SqlNode sqlNode : ((SqlNodeList) rightNode).getList()) {
                                if (SqlKind.LITERAL.equals(sqlNode.getKind())) {
                                    SqlLiteral rightValue = (SqlLiteral) sqlNode;
                                    whereCondition.setNumericValue(SqlLiteralUtil.isNumericValue(rightValue.getTypeName()));
                                    valueList.add(rightValue.toValue());
                                } else {
                                    valueList.add(toSqlString(rightNode, dialect));
                                }
                            }
                            whereCondition.setValueList(valueList);
                        } else {
                            if (SqlKind.LITERAL.equals(rightNode.getKind())) {
                                SqlLiteral rightValue = (SqlLiteral) rightNode;
                                whereCondition.setNumericValue(SqlLiteralUtil.isNumericValue(rightValue.getTypeName()));
                                whereCondition.setValue(rightValue.toValue());
                            } else if (SqlKind.IDENTIFIER.equals(rightNode.getKind())) {
                                whereCondition.setValue(rightNode.toString());
                            } else {
                                whereCondition.setValue(toSqlString(rightNode, dialect));
                            }
                        }
                        if (operandList.size() > 2) {
                            SqlNode thirdNode = operandList.get(2);
                            String secondValue;
                            whereCondition.setSecondValueKind(thirdNode.getKind().name());
                            if (SqlKind.LITERAL.equals(thirdNode.getKind())) {
                                secondValue = ((SqlLiteral) thirdNode).toValue();
                            } else {
                                secondValue = toSqlString(thirdNode, dialect);
                            }
                            whereCondition.setValueList(Arrays.asList(whereCondition.getValue(), secondValue));
                            whereCondition.setValue(null);
                        }
                    }
                    break;
                default:
                    whereCondition.setComparisonType(node.getKind().toString());
                    whereCondition.setValue(toSqlString(node, dialect));
            }
        } else {
            whereCondition.setComparisonType(node.getKind().toString());
            whereCondition.setIdentifier(toSqlString(node, dialect));
        }
        return whereCondition;
    }

    public static String toSqlString(SqlNode sqlNode, String dialect) {
        final String ba = "BETWEEN ASYMMETRIC";
        String sql = sqlNode.toSqlString(SqlDialectUtil.fromDialectString(dialect)).toString();
        if (StringUtils.containsIgnoreCase(sql, ba)) {
            return sql.replace(ba, "BETWEEN");
        }
        return sql;
    }

    private static FromTable parseSelectFromTable(SqlNode from) {
        if (SqlKind.IDENTIFIER.equals(from.getKind())) {
            return singleFromTable(from);
        }
        List<FromTable> parseList = new ArrayList<>();
        if(SqlKind.AS.equals(from.getKind())){
            SqlBasicCall basicCall = (SqlBasicCall) from;
            SqlNode tableNode = basicCall.getOperandList().get(0);
            if (isSelectNode(tableNode)) {
                SqlSelect selectNode = (SqlSelect) tableNode;
                parseList.add(parseSelectFromTable(selectNode.getFrom()));
            }else{
                return singleFromTable(from);
            }
        }

        from.accept(new SqlBasicVisitor<String>() {
            @Override
            public String visit(SqlCall call) {
                SqlKind kind = call.getKind();
                if (SqlKind.JOIN.equals(kind)) {
                    SqlJoin join = (SqlJoin) call;

                    SqlNode right = join.getRight();
                    FromTable rightTable = singleFromTable(right);
                    rightTable.setJoinType(join.getJoinType());
                    if (join.getCondition() != null) {
                        rightTable.setCondition(join.getCondition().toString());
                    }
                    rightTable.setJoinConditionType(join.getConditionType());
                    if (CollectionUtils.isNotEmpty(parseList)) {
                        rightTable.setRightTable(parseList.get(parseList.size() - 1));
                    }
                    rightTable.setFromTableType(FromTableType.JOIN_SQL);
                    parseList.add(rightTable);
                    if (!join.getLeft().getKind().equals(SqlKind.JOIN)) {
                        SqlNode left = join.getLeft();
                        FromTable leftTable = singleFromTable(left);
                        leftTable.setRightTable(parseList.get(parseList.size() - 1));
                        parseList.add(leftTable);
                    }
                }
                if (SqlKind.UNION.equals(kind)) {
                    SqlNode leftNode = call.getOperandList().get(0);
                    parseList.add(singleFromTable(leftNode));
                }
                if(SqlKind.SELECT.equals(kind)){
                    SqlSelect selectNode = (SqlSelect) call;
                    parseList.add(parseSelectFromTable(selectNode.getFrom()));
                }
                return call.getOperator().acceptCall(this, call);
            }
        });
        Collections.reverse(parseList);
        return parseList.get(0);
    }

    private static List<DataOrderBy> parseSelectOrderBy(SqlNodeList nodeList, String dialect) {
        List<DataOrderBy> list = new ArrayList<>();
        for (SqlNode node : nodeList) {
            DataOrderBy orderBy = new DataOrderBy();
            orderBy.setColumnKind(node.getKind().name());
            if (SqlKind.DESCENDING.equals(node.getKind())) {
                SqlBasicCall nodeCall = (SqlBasicCall) node;
                SqlOperator operator = nodeCall.getOperator();
                orderBy.setOrderType(OrderByType.valueOf(operator.getName()));
                SqlNode leftNode = nodeCall.getOperandList().get(0);
                if (SqlKind.IDENTIFIER.equals(leftNode.getKind())) {
                    orderBy.setColumnName(leftNode.toString());
                } else {
                    orderBy.setColumnName(toSqlString(leftNode, dialect));
                }
            } else if (SqlKind.IDENTIFIER.equals(node.getKind())) {
                orderBy.setOrderType(OrderByType.ASC);
                orderBy.setColumnName(node.toString());
            } else {
                orderBy.setOrderType(OrderByType.ASC);
                orderBy.setColumnName(toSqlString(node, dialect));
            }
            list.add(orderBy);

        }
        return list;
    }


    private static void resetOrderByColumnKind(List<DataOrderBy> orderByList, List<ModelColumn> columnList) {
        if (CollectionUtils.isEmpty(columnList) || CollectionUtils.isEmpty(orderByList)) {
            return;
        }
        //处理order by中使用字段是否为原始字段还是复合字段
        for (DataOrderBy orderBy : orderByList) {
            Optional<ModelColumn> columnFind = columnList.stream().filter(f ->
                            StringUtils.contains(
                                    StringUtils.lowerCase(f.getColumnName()), StringUtils.lowerCase(orderBy.getColumnName()))
                    )
                    .findAny();

            Optional<ModelColumn> aliasFind = columnList.stream().filter(f ->
                            StringUtils.equalsIgnoreCase(
                                    StringUtils.lowerCase(f.getColumnAlias()), StringUtils.lowerCase(orderBy.getColumnName()))
                    )
                    .findAny();


            if (!columnFind.isPresent() && !aliasFind.isPresent()) {
                continue;
            }
            //order by 内容和字段一致 则取字段类型
            columnFind.ifPresent(p -> orderBy.setColumnKind(p.getColumnKind()));
            //如果时别名，则默认identifier
            aliasFind.ifPresent(p -> orderBy.setColumnKind(SqlKind.IDENTIFIER.name()));

        }
    }


    private static String cleanSql(String sql, String dialect) {
        String semicolon = ";";
        if (StringUtils.endsWith(sql, semicolon)) {
            sql = StringUtils.substringBeforeLast(sql, semicolon);
        }
        return sql;
    }

    private static String hintParse(SqlModel sqlModel, String sql) {
        String regex = "(/\\*\\+)(.*?)(\\*/)";
        Pattern pattern = Pattern.compile(regex, Pattern.DOTALL);
        Matcher matcher = pattern.matcher(sql);
        if (matcher.find()) {
            sqlModel.setHint(matcher.group(2));
            return matcher.replaceAll("$1" + SqlModel.HINT_TAG + "$3");
        }
        return sql;
    }

    public static SqlModel parseSelectSql(String sql, String dialect) throws SqlParseException {
        log.debug("待解析sql:{}", sql);
        sql = cleanSql(sql, dialect);
        SqlModel sqlModel = new SqlModel();
        sql = hintParse(sqlModel, sql);

        if (!isSelectSql(sql, dialect)) {
            throw new RuntimeException("请检查sql是否正确");
        }


        sqlModel.setDialect(dialect);
        SqlNode sqlNode = SqlParser.create(sql, parserConfigWithoutQuoted(dialect)).parseQuery();
        SqlSelect selectNode = null;
        sqlModel.setSelectType(sqlNode.getKind().name());
        if (SqlKind.SELECT.equals(sqlNode.getKind())) {
            selectNode = (SqlSelect) sqlNode;
            if (selectNode.getFetch() != null) {
                sqlModel.setFetch(selectNode.getFetch().toString());
            }
        }
        if (SqlKind.ORDER_BY.equals(sqlNode.getKind())) {
            SqlOrderBy orderBy = (SqlOrderBy) sqlNode;
            selectNode = (SqlSelect) orderBy.query;
            List<DataOrderBy> orderByList = parseSelectOrderBy(orderBy.orderList, dialect);
            sqlModel.setOrderByList(orderByList);
            if (orderBy.fetch != null) {
                sqlModel.setFetch(orderBy.fetch.toString());
            }
        }
        if (SqlKind.UNION.equals(sqlNode.getKind())) {
            SqlBasicCall unionNode = (SqlBasicCall) sqlNode;
            selectNode = (SqlSelect) unionNode.getOperandList().get(unionNode.operandCount() - 1);
        }
        if (selectNode == null) {
            throw new RuntimeException("解析sql失败");
        }
        if (selectNode.getHaving() != null) {
            sqlModel.setHaving(selectNode.getHaving().toString());
        }

        List<ModelColumn> modelColumns = parseSelectColumn(selectNode, dialect);

        resetOrderByColumnKind(sqlModel.getOrderByList(), modelColumns);

        sqlModel.setColumnList(modelColumns);
        if (selectNode.getFrom() != null) {
            FromTable fromTable = parseSelectFromTable(selectNode.getFrom());
            sqlModel.setFromTable(fromTable);
        }
        if (selectNode.getWhere() != null) {
            WhereCondition whereCondition = parseSelectWhere(selectNode.getWhere(), dialect);
            List<WhereCondition> whereConditionList = flattenConditions(whereCondition, "AND".equalsIgnoreCase(whereCondition.getOperator()));
            sqlModel.setWhereConditionList(whereConditionList);
        }
        if (selectNode.getGroup() != null) {
            List<ModelColumn> groupList = new ArrayList<>();
            for (SqlNode groupByItem : selectNode.getGroup().getList()) {
                ModelColumn column = new ModelColumn();
                assert groupByItem != null;
                if (SqlKind.IDENTIFIER.equals(groupByItem.getKind())) {
                    column.setColumnName(groupByItem.toString());
                } else {
                    column.setColumnName(toSqlString(groupByItem, dialect));
                }
                column.setColumnKind(groupByItem.getKind().name());
                groupList.add(column);
            }
            sqlModel.setGroupList(groupList);
        }
        return sqlModel;
    }


    private static List<WhereCondition> flattenConditions(WhereCondition condition, boolean isAnd) {
        List<WhereCondition> flatConditions = new ArrayList<>();
        if (condition.getOperator() == null) {
            flatConditions.add(condition);
        } else {
            if (condition.getOperator().equalsIgnoreCase(AND)) {
                for (WhereCondition operand : condition.getConditionList()) {
                    flatConditions.addAll(flattenConditions(operand, true));
                }
            } else if (condition.getOperator().equalsIgnoreCase(OR)) {
                flatConditions.add(condition);
            }
        }
        return flatConditions;
    }


}