import request from './request';

interface ApiResponse<T> {
  code: number;
  data: T;
  message: string;
}

export const api = {
  get: <T>(url: string, params?: any) =>
    request.get<ApiResponse<T>, ApiResponse<T>>(url, { params }),

  post: <T>(url: string, data?: any) =>
    request.post<ApiResponse<T>, ApiResponse<T>>(url, data),

  put: <T>(url: string, data?: any) =>
    request.put<ApiResponse<T>, ApiResponse<T>>(url, data),

  delete: <T>(url: string, params?: any) =>
    request.delete<ApiResponse<T>, ApiResponse<T>>(url, { params }),
};

export default api;