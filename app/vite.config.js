import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit()],
  server: {
    proxy: {
      // Appels API redirigés vers le serveur local axum du PC caisse
      "/api": { target: "http://127.0.0.1:8080", changeOrigin: true }
    }
  }
});
