#!/usr/bin/env python3
"""Local Smart AI Failover Router (OpenAI-compatible)."""
import json
import os
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8787
FAIL_STATUSES = {401, 402, 403, 429, 500, 502, 503, 504}
COOLDOWN = 60

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    env = {}
    for base in (ROOT, os.getcwd()):
        path = os.path.join(base, ".ai-providers.env")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
            break
    return env


ENV = load_env()


def e(key, default=""):
    return ENV.get(key, os.environ.get(key, default))


def provider(name, env_key, base_url, model, roles=None, requires_key=True):
    bu_env = e(f"{name}_BASE_URL", "")
    bu = bu_env if bu_env else e(base_url, "")
    m_env = e(f"{name}_MODEL", "")
    m = m_env if m_env else e(model, "")
    key = e(env_key, "") if env_key else ""
    if requires_key and not key:
        return None

OPENROUTER_BASE = "https://openrouter.ai/api/v1"
VERCEL_BASE = "https://ai-gateway.vercel.sh/v1"
QWEN_BASE = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
HF_BASE = "https://router.huggingface.co/v1"
OPENWEBUI_BASE = e("OPENWEBUI_BASE_URL", "http://127.0.0.1:8080/v1")
OLLAMA_BASE = e("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")

PROVIDERS = []
for p in [
    provider("FREE_QWEN_KIMI", "FREE_QWEN_KIMI_API_KEY", "FREE_QWEN_KIMI_BASE_URL", "FREE_QWEN_KIMI_MODEL", roles={"fast-coder"}, requires_key=True),
    provider("OPENROUTER", "OPENROUTER_API_KEY", "OPENROUTER_BASE_URL", "OPENROUTER_MODEL", roles=None, requires_key=True),
    provider("VERCEL_AI_GATEWAY", "VERCEL_AI_GATEWAY_API_KEY", "VERCEL_AI_GATEWAY_BASE_URL", "VERCEL_AI_GATEWAY_MODEL", roles={"smart-planner"}, requires_key=True),
    provider("QWEN", "QWEN_API_KEY", "QWEN_BASE_URL", "QWEN_MODEL", roles=None, requires_key=True),
    provider("HUGGINGFACE", "HUGGINGFACE_API_KEY", "HUGGINGFACE_BASE_URL", "HUGGINGFACE_MODEL", roles=None, requires_key=True),
    provider("APINEX", "APINEX_API_KEY", "APINEX_BASE_URL", "APINEX_MODEL", roles=None, requires_key=True),
    provider("CLEANAPI", "CLEANAPI_API_KEY", "CLEANAPI_BASE_URL", "CLEANAPI_MODEL", roles=None, requires_key=True),
    provider("ORCAROUTER", "ORCAROUTER_API_KEY", "ORCAROUTER_BASE_URL", "ORCAROUTER_MODEL", roles=None, requires_key=True),
    provider("CODECRAFT", "CODECRAFT_API_KEY", "CODECRAFT_BASE_URL", "CODECRAFT_MODEL", roles=None, requires_key=True),
    provider("OPENWEBUI", "OPENWEBUI_API_KEY", "OPENWEBUI_BASE_URL", "OPENWEBUI_MODEL", roles=None, requires_key=False),
]:
    if p:
        PROVIDERS.append(p)

_defaults = {
    "OPENROUTER": (OPENROUTER_BASE, "openrouter/free"),
    "VERCEL_AI_GATEWAY": (VERCEL_BASE, "openai/gpt-4o-mini"),
    "QWEN": (QWEN_BASE, "qwen-plus"),
    "HUGGINGFACE": (HF_BASE, "Qwen/Qwen2.5-7B-Instruct"),
    "OPENWEBUI": (OPENWEBUI_BASE, e("OPENWEBUI_MODEL", "llama3.1")),
}
for p in PROVIDERS:
    if p["name"] in _defaults:
        bu, m = _defaults[p["name"]]
        if not p["base_url"]:
            p["base_url"] = bu
        if not p["model"]:
            p["model"] = m

ollama_model = e("OLLAMA_MODEL", "qwen2.5:3b")
if ollama_model:
    PROVIDERS.append({"name": "OLLAMA", "key": "", "base_url": OLLAMA_BASE, "model": ollama_model, "roles": None})

cooldowns = {}


def in_cooldown(name):
    return time.time() < cooldowns.get(name, 0)


def set_cooldown(name):
    cooldowns[name] = time.time() + COOLDOWN


def serves(p, model):
    if p["roles"] is None:
        return True
    return model in p["roles"]


def available(p):
    return bool(p["base_url"] and p["model"]) and not in_cooldown(p["name"])

    if not bu or not m:
        return None
    return {"name": name, "key": key, "base_url": bu, "model": m, "roles": roles}

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") == "/v1/models":
            data = {"object": "list", "data": [
                {"id": "smart-planner", "object": "model", "created": int(time.time()), "owned_by": "local-router"},
                {"id": "fast-coder", "object": "model", "created": int(time.time()), "owned_by": "local-router"},
            ]}
            body = json.dumps(data).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self._cors()
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self._cors()
            self.end_headers()

    def do_POST(self):
        if self.path.rstrip("/") != "/v1/chat/completions":
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {}
        stream = bool(payload.get("stream"))
        model = payload.get("model", "smart-planner")
        candidates = [p for p in PROVIDERS if serves(p, model) and available(p)]
        if not candidates:
            candidates = [p for p in PROVIDERS if available(p)]
        for p in candidates:
            try:
                url = p["base_url"].rstrip("/") + "/chat/completions"
                body = dict(payload)
                body["model"] = p["model"]
                body["stream"] = stream
                data = json.dumps(body).encode("utf-8")
                headers = {"Content-Type": "application/json"}
                if p["key"]:
                    headers["Authorization"] = "Bearer " + p["key"]
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                try:
                    resp = urllib.request.urlopen(req, timeout=120)
                except urllib.error.HTTPError as he:
                    err_body = he.read()
                    if he.code in FAIL_STATUSES:
                        set_cooldown(p["name"])
                        continue
                    self.send_response(he.code)
                    self.send_header("Content-Type", he.headers.get("Content-Type", "application/json"))
                    self._cors()
                    self.end_headers()
                    self.wfile.write(err_body)
                    return
                except Exception:
                    set_cooldown(p["name"])
                    continue
                ctype = resp.headers.get("Content-Type", "text/event-stream" if stream else "application/json")
                self.send_response(resp.status)
                self.send_header("Content-Type", ctype)
                self._cors()
                if not stream:
                    out = resp.read()
                    self.send_header("Content-Length", str(len(out)))
                    self.end_headers()
                    self.wfile.write(out)
                    return
                self.send_header("Transfer-Encoding", "chunked")
                self.end_headers()
                try:
                    while True:
                        chunk = resp.read(4096)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            except Exception:
                set_cooldown(p["name"])
                continue
        msg = {"error": {"message": "All providers failed or in cooldown", "type": "router_error"}}
        out = json.dumps(msg).encode()
        self.send_response(503)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self._cors()
        self.end_headers()
        self.wfile.write(out)

    def log_message(self, *args):
        return


if __name__ == "__main__":
    httpd = ThreadingHTTPServer((HOST, PORT), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()

