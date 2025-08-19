import { writable, derived, get } from 'svelte/store';
import '$lib/types/chat';
import '$lib/types/message';

// Main chat state
export const chatList = writable<CHAT.ChatItem[]>([]);
export const chatTitle = writable<string>('');
export const activeTask = writable<CHAT.Task | undefined>();
export const plan = writable<CHAT.Plan | undefined>();
export const taskList = writable<MESSAGE.Task[]>([]);
export const showAction = writable<boolean>(false);
export const loading = writable<boolean>(false);
export const sessionId = writable<string>('');

// Input state
export const inputInfo = writable<CHAT.TInputInfo>({
  message: '',
  deepThink: false,
  files: []
});

// Product selection state
export const selectedProduct = writable<CHAT.Product | undefined>();

// Derived stores
export const hasActiveChat = derived(
  chatList,
  $chatList => $chatList.length > 0
);

export const currentChat = derived(
  chatList,
  $chatList => $chatList[$chatList.length - 1]
);

// Helper functions
export function addChat(chat: CHAT.ChatItem) {
  chatList.update(chats => [...chats, chat]);
}

export function updateCurrentChat(updates: Partial<CHAT.ChatItem>) {
  chatList.update(chats => {
    if (chats.length === 0) return chats;
    const newChats = [...chats];
    newChats[newChats.length - 1] = {
      ...newChats[newChats.length - 1],
      ...updates
    };
    return newChats;
  });
}

export function clearChat() {
  chatList.set([]);
  chatTitle.set('');
  activeTask.set(undefined);
  plan.set(undefined);
  taskList.set([]);
  showAction.set(false);
  loading.set(false);
}

export function resetInputInfo() {
  inputInfo.set({
    message: '',
    deepThink: false,
    files: []
  });
}