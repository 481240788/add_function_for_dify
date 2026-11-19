"""撤销 Key：单独脚本，绝不自动删除 Key。仅使用已手动撤销的 Key。"""
from common import Checks, ENDPOINTS, env, explain, get_stat


def main():
    key = env('DIFY_REVOKED_KEY', required=True)
    checks = Checks()
    for name in ENDPOINTS:
        r = get_stat(name, key)
        checks.check(f'{name} 拒绝已撤销 Key', r.status == 401, explain(r))
    checks.summary()


if __name__ == '__main__':
    main()
