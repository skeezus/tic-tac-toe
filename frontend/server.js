/**
 * Minimal production server: serves static build and injects BACKEND_URL via /config.js.
 * Used by the production Docker image for Cloud Run.
 */
import express from "express";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const dist = path.join(__dirname, "dist");
const port = process.env.PORT || 5173;
const backendUrl = process.env.BACKEND_URL || "";

app.get("/config.js", (_req, res) => {
  res.type("application/javascript");
  res.send(`window.__BACKEND_URL__ = ${JSON.stringify(backendUrl)};\n`);
});

app.use(express.static(dist));

app.get("*", (req, res) => {
  res.sendFile(path.join(dist, "index.html"));
});

app.listen(port, "0.0.0.0", () => {
  console.log(`Serving on port ${port}`);
});
