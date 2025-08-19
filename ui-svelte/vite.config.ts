import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig, loadEnv } from 'vite';
import path from 'path';

export default defineConfig(({ command, mode }) => {
	const env = loadEnv(mode, process.cwd(), '');
	return {
		plugins: [sveltekit()],
		resolve: {
			alias: {
				'@': path.resolve('./src'),
				'$lib': path.resolve('./src/lib'),
			}
		},
		server: {
			host: '0.0.0.0',
			port: 3000,
			proxy: {
				'/web': {
					target: env.SERVICE_BASE_URL || 'http://localhost:8080',
					changeOrigin: true,
				}
			}
		},
		define: {
			SERVICE_BASE_URL: JSON.stringify(env.SERVICE_BASE_URL || 'http://localhost:8080'),
		},
		build: {
			outDir: 'build',
			sourcemap: false,
			minify: 'terser' as const,
			rollupOptions: {
				output: {
					inlineDynamicImports: true
				}
			},
			cssCodeSplit: false
		}
	};
});