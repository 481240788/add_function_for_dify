"""跨应用隔离：全 8 个接口逐一检查 A/B Key，A 带 B app_id 不得返回 B 的结果。"""
from common import Checks, ENDPOINTS, env, explain, get_stat, date_params


def main():
    a = env('DIFY_APP_A_KEY', required=True)
    b = env('DIFY_APP_B_KEY', required=True)
    b_id = env('DIFY_APP_B_ID', required=True)
    checks = Checks()
    print('说明：本测试对所有接口执行 A/B 基线和 app_id 注入；同值结果无法证明隔离。')
    for name in ENDPOINTS:
        ra = get_stat(name, a)
        rb = get_stat(name, b)
        # 不同应用模式可能导致 400；只有同一接口两边皆 200 才做结果归属比较
        if ra.status != 200 or rb.status != 200:
            checks.skip(name, f'基线非双 200 (A={ra.status}, B={rb.status})；建议使用同类型两应用测试')
            continue
        injected = get_stat(name, a, {**date_params(), 'app_id': b_id})
        if injected.status == 400:
            checks.check(name, True)  # 显式拒绝未知/越权参数也安全
        else:
            checks.check(name, injected.status == 200 and injected.body == ra.body,
                         f'注入后响应偏离 A 基线: {explain(injected)}')
        if ra.body == rb.body:
            checks.skip(f'{name} 数据区分度', 'A/B 数据相同，无法独立证明来自不同应用；请给 B 产生不同数据后重测')
        else:
            checks.check(f'{name} A/B 基线不同', True)
    checks.summary()


if __name__ == '__main__':
    main()
