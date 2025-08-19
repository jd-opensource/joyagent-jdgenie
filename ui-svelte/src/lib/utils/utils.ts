import { throttle } from "lodash";

/**
 * 检查字符串是否为有效的 JSON
 */
export const isValidJSON = (str?: string): boolean => {
  if (!str) return false;
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
};

/**
 * 检查文本是否包含 HTML 元素
 */
export const isHTML = (text: string): boolean => {
  try {
    const parser = new DOMParser();
    const doc = parser.parseFromString(text, "text/html");
    return Array.from(doc.body.childNodes).some(
      (node) => node.nodeType === Node.ELEMENT_NODE
    );
  } catch {
    return false;
  }
};

/**
 * 生成唯一 ID
 */
export const getUniqId = (): string => {
  return `${Date.now()}-${Math.floor(Math.random() * 10000)}`;
};

/**
 * 在新窗口打开 URL
 */
export const jumpUrl = (url?: string): void => {
  if (!url) return;
  window.open(url);
};

const ONE_DAY_MS = 24 * 60 * 60 * 1000;
const TEN_DAYS_MS = 10 * ONE_DAY_MS;

/**
 * 格式化时间戳
 */
export const formatTimestamp = (timestamp: number | string): string => {
  const now = Date.now();
  const inputDate = new Date(Number(timestamp));
  const diffTime = now - inputDate.getTime();

  if (diffTime <= ONE_DAY_MS) {
    return inputDate.toLocaleString();
  } else if (diffTime < TEN_DAYS_MS) {
    return `${Math.ceil(diffTime / ONE_DAY_MS)}天前`;
  }
  return "10天前";
};
/**
 * 从 URL 中获取查询参数
 */
export const getQuery = (targetUrl: string, key: string): string | null => {
  const url = new URL(targetUrl);
  const searchParams = new URLSearchParams(url.search);
  return searchParams.get(key);
};

export const scrollToTop = (dom: Element) => {
  setTimeout(()=>{
    dom.scrollTop = dom.scrollHeight;
  }, 100);
};

export const copyText = throttle((text?: string | number) => {
  if (navigator.clipboard) {
    navigator.clipboard.writeText((text || "") + "");
  } else {
    const input = document.createElement("textarea");
    input.value = text + "";
    document.body.appendChild(input);
    input.focus();
    input.select();
    document.execCommand("copy");
    document.body.removeChild(input);
  }
}, 1000);

/**
 * 阻止冒泡函数
 * @param e 事件对象
 */
export const preventDefault = <
  T extends {
    preventDefault?: () => void;
    stopPropagation?: () => void;
  },
>(
    e: T
  ) => {
  e.stopPropagation?.();
  e.preventDefault?.();
};

/**
 * 文件下载
 */
export const downloadFile = (url?: string, name?: string) => {
  if (!url) return;
  const link = document.createElement("a");
  link.href = url;
  link.style.display = "none";
  link.target = "_blank";
  if (name) {
    link.download = name;
  }
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

/**
 * 将秒数转换为分钟:秒数格式
 * @param seconds 总秒数
 * @returns 格式化的时间字符串，如 "2:35"
 */
export function formatSecondsToMinutes(seconds: number): string {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
}

export const getSessionId = () => {
  return `session-${getUniqId()}`;
};

/**
 * 设置全局消息实例，以便在应用中统一管理消息提示
 */
export type MessageApi = {
  info: (msg: string) => void;
  success: (msg: string) => void;
  error: (msg: string) => void;
  warning: (msg: string) => void;
};

let message: MessageApi | null = null;

/**
 * 设置全局的静态消息实例
 * @param messageCnf 消息实例
 */
export const setMessage = (messageCnf: typeof message) => {
  message = messageCnf;
};

export const showMessage = () => {
  return message;
};

export const getOS = () => {
  const userAgent = navigator.userAgent.toLowerCase();
  if (userAgent.includes('windows')) {
    return 'Windows';
  } else if (userAgent.includes('macintosh') || userAgent.includes('mac os x')) {
    return 'Mac';
  } else {
    return 'Unknown';
  }
};

/**
 * 解析CSV数据
 * @param str csv字符串
 * @returns
 */
export const parseCSVData = (str: string) =>  {
  const result = [];
  const jsonObj = str.split('\n');
  let arrHeader: string[] = [];

  for (const i in jsonObj) {
    if (typeof jsonObj[i] === 'string' && jsonObj[i].length > 0) {
      const row = `${jsonObj[i]}`;
      if (row.trim().length > 0) {
        const kv = jsonObj[i].split(',');
        if (Number(i) === 0) {
          // 获取column表头
          arrHeader = kv;
        } else {
          const obj: Record<string, string> = {};

          for (let index = 0; index < arrHeader.length; index++) {
            // 组装表格数据
            const name = String(arrHeader[index]);

            if (!arrHeader[index]) continue;
            if (!obj[name]) {
              try {
                if (kv[index]) {
                  obj[name] = String(kv[index]);
                } else {
                  obj[name] = '';
                }
              } catch (err: any) {
                // throw new Error(err);
                console.error(err);
                obj[name] = '';
              }
            }
          }
          result.push(obj);
        }
      }
    }
  }
  return result;
};