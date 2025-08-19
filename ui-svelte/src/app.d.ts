/// <reference types="@sveltejs/kit" />

declare global {
  namespace App {
    // interface Error {}
    // interface Locals {}
    // interface PageData {}
    // interface Platform {}
  }
  
  const SERVICE_BASE_URL: string;
  
  namespace CHAT {
    // Re-export types from lib/types/chat.ts
    export * from '$lib/types/chat';
  }
  
  namespace MESSAGE {
    // Re-export types from lib/types/message.ts
    export * from '$lib/types/message';
  }
}

export {};