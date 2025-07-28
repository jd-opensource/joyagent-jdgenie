import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import tailwindcss from '@tailwindcss/vite';

const serverBaseUrl = '10.246.7.123:8080';

export default defineConfig((mode) => ({
  plugins: [
    react(),
    tailwindcss()
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
      crypto: 'crypto-browserify',
    },
  },
  css: {preprocessorOptions: {less: {javascriptEnabled: true},},},
  server: {
    // 修改为监听所有接口，而不是特定主机名
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/web': {
        target: serverBaseUrl,
        changeOrigin: true,
      },
    },
  },
  define: {
    // 一定要序列化，否则打包时会报错
    SERVICE_BASE_URL: JSON.stringify(mode.mode === 'development' ? '' : serverBaseUrl),
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser' as const,
    rollupOptions: {output: {inlineDynamicImports: true},},
    cssCodeSplit: false,
  },
}));
