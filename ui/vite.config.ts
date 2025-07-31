import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import tailwindcss from '@tailwindcss/vite';

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
    host: '0.0.0.0',
    port: 3000,
    proxy: {
      '/web': {
        target: process.env.VITE_SERVER_BASE_URL || 'http://127.0.0.1:8080',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'terser' as const,
    rollupOptions: {output: {inlineDynamicImports: true},},
    cssCodeSplit: false,
  },
}));
