"""参数校验：非法时区、日期、逆序时间范围。"""
from common import Checks, date_params, env, explain, get_stat


def main():
    key = env('DIFY_APP_A_KEY', required=True)
    baseline = date_params()
    cases = {
        '非法时区': {'timezone': 'Invalid/Timezone'},
        '非法开始日期': {'start': 'not-a-date'},
        '开始时间晚于结束时间': {'start': '2026-11-20 00:00', 'end': '2026-11-01 00:00'},
    }
    checks = Checks()
    for title, change in cases.items():
        r = get_stat('daily-messages', key, {**baseline, **change})
        checks.check(title, r.status == 400, explain(r))
    checks.summary()


if __name__ == '__main__':
    main()
