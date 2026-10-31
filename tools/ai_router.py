#!/usr/bin/env python3
"""Local Smart AI Failover Router (OpenAI-compatible)."""
import json
import os
import subprocess
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENV_FILE = ROOT / ".ai-providers.env"

def load_env():
    if ENV_FILE.exists():
        for raw in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value

load_env()

def env(name, default=""):
    return os.environ.get(name, default).strip()

FAILOVER_STATUSES = {401, 402, 403, 429, 500, 502, 503, 504}
COOLDOWN_SECONDS = 60
_cooldowns = {}
_cooldown_lock = threading.Lock()


def set_cooldown(name):
    with _cooldown_lock:
        _cooldowns[name] = time.time() + COOLDOWN_SECONDS


def in_cooldown(name):
    with _cooldown_lock:
        until = _cooldowns.get(name, 0)
        if time.time() < until:
            return True
        _cooldowns.pop(name, None)
        return False


def first_ollama_model():
    configured = env("OLLAMA_MODEL")
    if configured:
        return configured
    try:
        result = subprocess.run(
            ["ollama", "list"], capture_output=True, text=True, timeout=5
        )
        lines = [line for line in result.stdout.splitlines() if line.strip()]
        if len(lines) > 1:
            return lines[1].split()[0]
    except Exception:
        pass
    return "llama3.2"


def make_provider(name, key_env, base_env, model_env, base_default, model_default,
                  preferred=None, requires_key=True):
    key = env(key_env) if key_env else ""
    base = env(base_env, base_default)
    model = env(model_env, model_default)
    if requires_key and not key:
        return None
    if not base:
        return None
    if not model:
        if name == "OLLAMA":
            model = first_ollama_model()
        else:
            model = "gpt-4o-mini"
    if not model:
        return None
    return {
        "name": name,
        "key": key,
        "base": base.rstrip("/"),
        "model": model,
        "preferred": set(preferred or ()),
    }


def build_providers():
    providers = []
    items = [
        ("FREE_QWEN_KIMI", "FREE_QWEN_KIMI_API_KEY", "FREE_QWEN_KIMI_BASE_URL",
         "FREE_QWEN_KIMI_MODEL", "", "", {"fast-coder"}, True),
        ("OPENROUTER", "OPENROUTER_API_KEY", "OPENROUTER_BASE_URL",
         "OPENROUTER_MODEL", "https://openrouter.ai/api/v1", "openrouter/free", None, True),
        ("VERCEL_AI_GATEWAY", "VERCEL_AI_GATEWAY_API_KEY", "VERCEL_AI_GATEWAY_BASE_URL",
         "VERCEL_AI_GATEWAY_MODEL", "https://ai-gateway.vercel.sh/v1", "openai/gpt-4o-mini",
         None, True),
        ("QWEN", "QWEN_API_KEY", "QWEN_BASE_URL", "QWEN_MODEL",
         "https://dashscope-intl.aliyuncs.com/compatible-mode/v1", "qwen-plus", None, True),
        ("HUGGINGFACE", "HUGGINGFACE_API_KEY", "HUGGINGFACE_BASE_URL", "HUGGINGFACE_MODEL",
         "https://router.huggingface.co/v1", "Qwen/Qwen2.5-7B-Instruct", None, True),
    ]
    for spec in items:
        provider = make_provider(*spec)
        if provider:
            providers.append(provider)

    for name in ("APINEX", "CLEANAPI", "ORCAROUTER", "CODECRAFT"):
        provider = make_provider(
            name,
            f"{name}_API_KEY",
            f"{name}_BASE_URL",
            f"{name}_MODEL",
            "",
            "gpt-4o-mini",
            None,
            True,
        )
        if provider:
            providers.append(provider)

    openwebui = make_provider(
        "OPENWEBUI",
        "OPENWEBUI_API_KEY",
        "OPENWEBUI_BASE_URL",
        "OPENWEBUI_MODEL",
        "",
        "gpt-4o-mini",
        None,
        False,
    )
    if openwebui and openwebui["base"]:
        providers.append(openwebui)

    ollama = make_provider(
        "OLLAMA",
        "",
        "OLLAMA_BASE_URL",
        "OLLAMA_MODEL",
        "http://127.0.0.1:11434/v1",
        first_ollama_model(),
        None,
        False,
    )
    if ollama:
        providers.append(ollama)

    return providers


ALL_PROVIDERS = build_providers()


def chain_for(model):
    selected = []
    for provider in ALL_PROVIDERS:
        if provider["preferred"] and model not in provider["preferred"]:
            continue
        selected.append(provider)
    if model == "smart-planner":
        vercel = [p for p in selected if p["name"] == "VERCEL_AI_GATEWAY"]
        others = [p for p in selected if p["name"] != "VERCEL_AI_GATEWAY"]
        selected = vercel + others
    return selected


def build_headers(provider):
    headers = {"Content-Type": "application/json"}
    if provider["key"]:
        headers["Authorization"] = "Bearer " + provider["key"]
    if provider["name"] == "OPENROUTER":
        headers["HTTP-Referer"] = "http://localhost"
        headers["X-Title"] = "Rihal AI Router"
    if provider["name"] == "HUGGINGFACE":
        headers["X-Wait-For-Model"] = "true"
    return headers


class RouterHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        return

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ("/v1/models", "/models"):
            now = int(time.time())
            data = [
                {"id": "smart-planner", "object": "model", "created": now,
                 "owned_by": "rihal-router"},
                {"id": "fast-coder", "object": "model", "created": now,
                 "owned_by": "rihal-router"},
            ]
            self._send_json(200, {"object": "list", "data": data})
            return
        self._send_json(404, {"error": {"message": "not found", "type": "not_found"}})

    def do_POST(self):
        path = self.path.split("?")[0]
        if path not in ("/v1/chat/completions", "/chat/completions"):
            self._send_json(404, {"error": {"message": "not found", "type": "not_found"}})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            self._send_json(400, {"error": {"message": "invalid json", "type": "invalid_request"}})
            return

        model = body.get("model") or "smart-planner"
        stream = bool(body.get("stream"))
        chain = chain_for(model)
        if stream:
            self._handle_stream(body, model, chain)
        else:
            self._handle_non_stream(body, model, chain)

    def _send_json(self, status, payload):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self._cors()
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _handle_non_stream(self, body, model, chain):
        for provider in chain:
            if in_cooldown(provider["name"]):
                continue
            url = provider["base"] + "/chat/completions"
            payload = dict(body)
            payload["model"] = provider["model"]
            payload["stream"] = False
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=build_headers(provider),
                                       method="POST")
            try:
                with urllib.request.urlopen(req, timeout=180) as resp:
                    response_body = resp.read()
            except urllib.error.HTTPError as exc:
                error_body = exc.read()
                if exc.code in FAILOVER_STATUSES:
                    set_cooldown(provider["name"])
                    continue
                try:
                    parsed = json.loads(error_body.decode("utf-8", "replace"))
                except Exception:
                    parsed = {"error": {"message": error_body.decode("utf-8", "replace"),
                                        "type": "upstream_error"}}
                self._send_json(exc.code, parsed)
                return
            except Exception:
                set_cooldown(provider["name"])
                continue

            try:
                parsed = json.loads(response_body.decode("utf-8"))
                parsed["model"] = model
            except Exception:
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response_body)))
                self._cors()
                self.end_headers()
                try:
                    self.wfile.write(response_body)
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            self._send_json(200, parsed)
            return

        self._send_json(503, {"error": {"message": "all providers failed or in cooldown",
                                         "type": "router_error"}})

    def _handle_stream(self, body, model, chain):
        for provider in chain:
            if in_cooldown(provider["name"]):
                continue
            url = provider["base"] + "/chat/completions"
            payload = dict(body)
            payload["model"] = provider["model"]
            payload["stream"] = True
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers=build_headers(provider),
                                       method="POST")
            try:
                resp = urllib.request.urlopen(req, timeout=300)
            except urllib.error.HTTPError as exc:
                error_body = exc.read()
                if exc.code in FAILOVER_STATUSES:
                    set_cooldown(provider["name"])
                    continue
                try:
                    parsed = json.loads(error_body.decode("utf-8", "replace"))
                except Exception:
                    parsed = {"error": {"message": error_body.decode("utf-8", "replace"),
                                        "type": "upstream_error"}}
                self._send_json(exc.code, parsed)
                return
            except Exception:
                set_cooldown(provider["name"])
                continue

            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "close")
            self._cors()
            self.end_headers()
            try:
                for chunk in resp:
                    self.wfile.write(chunk)
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                resp.close()
            return

        self._send_json(503, {"error": {"message": "all providers failed or in cooldown",
                                         "type": "router_error"}})


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8787), RouterHandler)
    server.allow_reuse_address = True
    server.serve_forever()


if __name__ == "__main__":
    main()
