"""Completion 专项：查询平均响应时间，要求 200 且 data 中 latency 为数值。"""
from common import Checks, env, explain, get_stat


def main():
    key = env('DIFY_COMPLETION_KEY', required=True)
    r = get_stat('average-response-time', key)
    checks = Checks()
    checks.check('Completion 请求返回 200', r.status == 200, explain(r))
    data = r.body.get('data') if isinstance(r.body, dict) else None
    checks.check('响应 data 为数组', isinstance(data, list), explain(r))
    if isinstance(data, list) and data:
        values = [row.get('latency') for row in data if isinstance(row, dict)]
        checks.check('存在数值 latency（毫秒）', any(isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0 for v in values), str(values))
        print(f'实际统计: {data}')
    else:
        checks.skip('latency 数值检查', '该时间段没有统计数据；先在 Completion 应用产生至少一条记录')
    checks.summary()


if __name__ == '__main__':
    main()
