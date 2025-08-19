import { writable, get } from 'svelte/store';
import type { MessageApi } from '$lib/utils/utils';

export type ToastMessage = {
  id: string;
  type: 'info' | 'success' | 'error' | 'warning';
  message: string;
  duration?: number;
};

// Toast messages store
export const toastMessages = writable<ToastMessage[]>([]);

// Add a toast message
function addToast(type: ToastMessage['type'], message: string, duration = 3000) {
  const id = `toast-${Date.now()}-${Math.random()}`;
  const toast: ToastMessage = { id, type, message, duration };
  
  toastMessages.update(messages => [...messages, toast]);
  
  // Auto remove after duration
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id);
    }, duration);
  }
  
  return id;
}

// Remove a toast message
function removeToast(id: string) {
  toastMessages.update(messages => messages.filter(m => m.id !== id));
}

// Message API implementation for compatibility with utils
export const messageApi: MessageApi = {
  info: (msg: string) => addToast('info', msg),
  success: (msg: string) => addToast('success', msg),
  error: (msg: string) => addToast('error', msg),
  warning: (msg: string) => addToast('warning', msg),
};

// Export functions
export const message = {
  info: messageApi.info,
  success: messageApi.success,
  error: messageApi.error,
  warning: messageApi.warning,
  remove: removeToast
};