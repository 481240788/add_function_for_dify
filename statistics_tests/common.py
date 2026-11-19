"""Dify statistics API tests: standard library only."""
from __future__ import annotations
import json
import os
import sys
from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ENDPOINTS = [
    'daily-messages', 'daily-conversations', 'daily-end-users',
    'token-costs', 'average-session-interactions',
    'user-satisfaction-rate', 'average-response-time', 'tokens-per-second',
]

@dataclass
class Response:
    status: int
    body: object
    raw: str


def env(name: str, required: bool = False, default: str = '') -> str:
    value = os.environ.get(name, default).strip()
    if required and not value:
        raise RuntimeError(f'缺少环境变量 {name}（请先在终端 export）')
    return value


def base_url() -> str:
    return env('DIFY_BASE_URL', default='http://localhost').rstrip('/')


def date_params() -> dict[str, str]:
    return {
        'start': env('DIFY_START', default='2026-11-01 00:00'),
        'end': env('DIFY_END', default='2026-11-20 00:00'),
        'timezone': env('DIFY_TIMEZONE', default='Asia/Shanghai'),
    }


def request(method: str, path: str, key: str | None, params: dict | None = None, payload: dict | None = None) -> Response:
    url = base_url() + path
    if params:
        url += ('&' if '?' in url else '?') + urlencode(params)
    headers = {'Accept': 'application/json'}
    if key is not None:
        headers['Authorization'] = f'Bearer {key}'
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urlopen(req, timeout=30) as resp:
            status = resp.status
            raw = resp.read().decode('utf-8', errors='replace')
    except HTTPError as exc:
        status = exc.code
        raw = exc.read().decode('utf-8', errors='replace')
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f'无法访问 {url}: {exc}') from exc
    try:
        body = json.loads(raw)
    except json.JSONDecodeError:
        body = raw
    return Response(status, body, raw)


def get_stat(name: str, key: str | None, params: dict | None = None) -> Response:
    assert name in ENDPOINTS, name
    return request('GET', f'/v1/statistics/{name}', key, date_params() if params is None else params)


class Checks:
    def __init__(self):
        self.pass_count = 0
        self.fail_count = 0
        self.skip_count = 0

    def check(self, title: str, good: bool, detail: str = '') -> None:
        if good:
            self.pass_count += 1
            print(f'[PASS] {title}')
        else:
            self.fail_count += 1
            print(f'[FAIL] {title}: {detail}')

    def skip(self, title: str, reason: str) -> None:
        self.skip_count += 1
        print(f'[SKIP] {title}: {reason}')

    def summary(self) -> None:
        print(f'\n结果: PASS={self.pass_count}, FAIL={self.fail_count}, SKIP={self.skip_count}')
        sys.exit(1 if self.fail_count else 0)


def explain(r: Response) -> str:
    return f'HTTP {r.status}; body={str(r.body)[:300]}'
