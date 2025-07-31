import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { showMessage } from './utils';

// 创建axios实例
const request: AxiosInstance = axios.create({
  baseURL: SERVICE_BASE_URL,
  timeout: 10000,
  headers: {'Content-Type': 'application/json',},
});

// 请求拦截器
request.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

const noAuth = (url?: string) => {
  showMessage()?.error('未登录');
  if (url) {
    location.href = url;
  }
};

// 响应拦截器
request.interceptors.response.use(
  (response: AxiosResponse) => {

    const { data, status } = response;

    if (status === 200) {
      // 根据后端约定的数据结构处理
      if (data.code === 200) {
        return data.data;
      } else if (data.code === 401) {
        noAuth(data.redirectUrl);
      } else {
        showMessage()?.error(data.msg || '请求失败');
        return Promise.reject(new Error(data.msg || '请求失败'));
      }
    }

    return response;
  },
  (error) => {
    console.error('响应错误:', error);

    const message = showMessage();
    if (error.response) {
      const { status, data: resData } = error.response;

      switch (status) {
        case 401:
          // 未授权，清除token并跳转登录
          noAuth(resData.redirectUrl);
          break;
        case 403:
          message?.error(error.message || '没有权限访问');
          break;
        case 404:
          message?.error(error.message || '请求的资源不存在');
          break;
        case 500:
          message?.error(error.message || '服务器内部错误');
          break;
        default:
          message?.error(error.message || `请求失败，状态码: ${status}`);
      }
    } else if (error.request) {
      message?.error(error.message || '网络错误，请检查网络连接');
    } else {
      message?.error('请求配置错误');
    }

    return Promise.reject(error);
  }
);

export default request;