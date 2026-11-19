"""运行各独立测试脚本。撤销测试仅在提供 DIFY_REVOKED_KEY 时运行。"""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TESTS = [
    'test_01_functional.py', 'test_02_auth.py', 'test_03_params.py',
    'test_04_isolation.py', 'test_05_revoked.py', 'test_06_completion.py',
]
NEEDS = {
    'test_01_functional.py': ['DIFY_APP_A_KEY'],
    'test_03_params.py': ['DIFY_APP_A_KEY'],
    'test_04_isolation.py': ['DIFY_APP_A_KEY', 'DIFY_APP_B_KEY', 'DIFY_APP_B_ID'],
    'test_05_revoked.py': ['DIFY_REVOKED_KEY'],
    'test_06_completion.py': ['DIFY_COMPLETION_KEY'],
}


def main():
    success = 0
    failed = 0
    skipped = 0
    for script in TESTS:
        missing = [k for k in NEEDS.get(script, []) if not os.getenv(k)]
        if missing:
            print(f'\n[SKIP] {script}: 缺少 {", ".join(missing)}', flush=True)
            skipped += 1
            continue
        print(f'\n===== {script} =====', flush=True)
        proc = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=False)
        if proc.returncode:
            failed += 1
        else:
            success += 1
    print(f'\n脚本汇总: 成功={success}, 失败={failed}, 跳过={skipped}')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
