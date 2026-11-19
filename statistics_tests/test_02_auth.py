"""鉴权：无 Key 与错误 Key 均应 401。"""
from common import Checks, explain, get_stat


def main():
    checks = Checks()
    for title, key in [('无 Authorization', None), ('无效 API Key', 'app-invalid-for-statistics-test')]:
        r = get_stat('daily-messages', key)
        checks.check(title, r.status == 401, explain(r))
    checks.summary()


if __name__ == '__main__':
    main()
