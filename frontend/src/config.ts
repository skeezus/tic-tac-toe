/**
 * Backend base URL for API/WebSocket. In production, set by /config.js (injected by server).
 * When unset (e.g. dev with same-origin proxy), we use the current origin.
 */
declare global {
  interface Window {
    __BACKEND_URL__?: string;
  }
}

export function getBackendBase(): string {
  const url = window.__BACKEND_URL__?.trim();
  if (url) return url.replace(/\/$/, "");
  return window.location.origin;
}

export function getWebSocketUrl(): string {
  const base = getBackendBase();
  const protocol = base.startsWith("https") ? "wss:" : "ws:";
  const host = base.replace(/^https?:\/\//, "");
  return `${protocol}//${host}/ws`;
}
