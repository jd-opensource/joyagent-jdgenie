import api from './index';

export const agentApi = {
  loginIn: () =>
    api.get(`/web/api/login`),
  getWhiteList: () => api.get(`/web/api/getWhiteList`),
  apply: (email: string) => api.get(`/web/api/genie/apply`, { email }),
};