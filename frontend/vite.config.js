import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

// In development Django runs on :8000 and Vite proxies to it, so the SPA and API share an
// origin and Django's session + CSRF cookies work without CORS.
const backend = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      "/api": backend,
      "/media": backend,
      "/admin": backend,
      "/static": backend,
    },
  },
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test-setup.js"],
  },
});
