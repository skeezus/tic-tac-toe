import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [
    react(),
    {
      name: "config-js",
      configureServer(server) {
        server.middlewares.use("/config.js", (_req, res) => {
          res.setHeader("Content-Type", "application/javascript");
          res.end("// dev: same origin");
        });
      },
    },
  ],
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/ws": {
        target: backendUrl.replace(/^http/, "ws"),
        ws: true,
      },
      "/api": {
        target: backendUrl,
        changeOrigin: true,
      },
      "/health": {
        target: backendUrl,
        changeOrigin: true,
      },
    },
  },
});
