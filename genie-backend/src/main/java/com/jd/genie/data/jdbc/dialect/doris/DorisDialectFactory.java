package com.jd.genie.data.jdbc.dialect.doris;

import com.google.auto.service.AutoService;
import com.jd.genie.data.jdbc.dialect.DialectEnum;
import com.jd.genie.data.jdbc.dialect.JdbcDialect;
import com.jd.genie.data.jdbc.dialect.JdbcDialectFactory;
import lombok.extern.slf4j.Slf4j;

@Slf4j
@AutoService(JdbcDialectFactory.class)
public class DorisDialectFactory implements JdbcDialectFactory {
    @Override
    public boolean acceptsURL(String url) {
        return url.startsWith(DialectEnum.DORIS.getUrlPrefix());
    }

    @Override
    public JdbcDialect create() {
        return new DorisDialect();
    }
    
}
