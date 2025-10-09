import { defineConfig } from 'vite'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'
import tailwindcss from '@tailwindcss/vite'

const config = defineConfig({
  plugins: [
    // this is the plugin that enables path aliases
    viteTsConfigPaths({
      projects: ['./tsconfig.json'],
    }),
    tailwindcss(),
    viteReact(),
  ],
  // Ensure environment variables are properly replaced at build time
  envPrefix: 'VITE_',
  build: {
    // SPA configuration
    rollupOptions: {
      input: {
        main: './index.html',
      },
    },
  },
})

export default config;
