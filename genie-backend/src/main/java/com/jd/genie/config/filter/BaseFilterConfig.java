package com.jd.genie.config.filter;

import jakarta.servlet.DispatcherType;
import jakarta.servlet.Filter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;
import org.springframework.web.filter.CorsFilter;


/**
 * @author bjwangjuntao
 */
@Configuration
public class BaseFilterConfig {
	public BaseFilterConfig() {
	}

	@Bean
	public FilterRegistrationBean<CorsFilter> corsFilter() {
		UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
		CorsConfiguration config = new CorsConfiguration();
		config.setAllowCredentials(true);
		config.addAllowedOriginPattern("*");
		config.addAllowedHeader("*");
		config.addAllowedMethod("*");
		source.registerCorsConfiguration("/**", config);
		CorsFilter corsFilter = new CorsFilter(source);
        return this.creatAllFilter(corsFilter, 1);
	}


	<T extends Filter> FilterRegistrationBean<T> creatAllFilter(T filter, int order) {
		return this.createFilter(filter, order, "/*");
	}

	<T extends Filter> FilterRegistrationBean<T> createFilter(T filter, int order, String... urlPatterns) {
		FilterRegistrationBean<T> bean = new FilterRegistrationBean<>();
		bean.setFilter(filter);
		bean.setOrder(order);
		bean.addUrlPatterns(urlPatterns);
		bean.setDispatcherTypes(DispatcherType.REQUEST, new DispatcherType[0]);
		return bean;
	}
}
