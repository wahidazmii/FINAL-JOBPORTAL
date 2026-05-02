import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: process.env.VITE_BACKEND_URL || "http://localhost:8001",
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: "build",
    sourcemap: false,
  },
  define: {
    // allow process.env shim for any legacy references
  },
});
