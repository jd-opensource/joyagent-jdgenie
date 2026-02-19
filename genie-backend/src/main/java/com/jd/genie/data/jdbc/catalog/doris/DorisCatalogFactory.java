package com.jd.genie.data.jdbc.catalog.doris;

import com.google.auto.service.AutoService;
import com.jd.genie.data.jdbc.catalog.JdbcCatalog;
import com.jd.genie.data.jdbc.catalog.JdbcCatalogFactory;
import com.jd.genie.data.jdbc.dialect.DialectEnum;


@AutoService(JdbcCatalogFactory.class)
public class DorisCatalogFactory implements JdbcCatalogFactory {
    @Override
    public DialectEnum jdbcDialect() {
        return DialectEnum.DORIS;
    }

    @Override
    public JdbcCatalog createCatalog() {
        return new DorisCatalog();
    }
}
