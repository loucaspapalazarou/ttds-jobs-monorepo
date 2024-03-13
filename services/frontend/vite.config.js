import {fileURLToPath, URL} from 'node:url'

import {defineConfig, loadEnv} from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default ({mode}) => {
    process.env = Object.assign(process.env, loadEnv(mode, process.cwd(), ''));
    return defineConfig({
        envDir: '.',
        plugins: [
            vue(),
        ],
        server: {
            host: true,
            port: 8000,
            proxy: {
                "/api": {
                    target: 'http://backend:5001',
                    changeOrigin: true,
                    secure: false,
                    rewrite: (path) => path.replace(/^\/api/, "")
                }
            },
        },
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url))
            }
        },
        preview: {
            port: 8080,
            proxy: {
                "/api": {
                    target: process.env.VITE_SEARCH_API_URL,
                    changeOrigin: true,
                    secure: false,
                    rewrite: (path) => path.replace(/^\/api/, "")
                }
            },
        }
    })
}
