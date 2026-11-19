"""功能测试：Advanced Chat/Chatflow 应用，7 个 200 + 响应时间预期 400。"""
from common import Checks, ENDPOINTS, env, explain, get_stat


def main():
    key = env('DIFY_APP_A_KEY', required=True)
    checks = Checks()
    for name in ENDPOINTS:
        r = get_stat(name, key)
        if name == 'average-response-time':
            ok = r.status == 400 and isinstance(r.body, dict) and r.body.get('code') == 'invalid_param'
            checks.check(f'{name}（Advanced Chat 模式限制）', ok, explain(r))
        else:
            ok = r.status == 200 and isinstance(r.body, dict) and isinstance(r.body.get('data'), list)
            checks.check(f'{name}（200 + data 数组）', ok, explain(r))
    checks.summary()


if __name__ == '__main__':
    main()
