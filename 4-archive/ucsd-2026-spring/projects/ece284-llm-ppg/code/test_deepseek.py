"""test_deepseek.py — DeepSeek API key + endpoint smoke test.

1. load_dotenv() 从 code/.env 读 DEEPSEEK_API_KEY
2. 校验 key 不是 "__USER_WILL_FILL_THIS__" 占位符 (否则提示用户先填 key)
3. 用 openai SDK 调 deepseek-v4-flash 问 "say hello"
4. 打印响应

Run:
    cd code/ && python test_deepseek.py
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PLACEHOLDER = "__USER_WILL_FILL_THIS__"
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-flash"


def main():
    # 1. Load .env (在脚本所在目录, 不依赖 cwd)
    env_path = Path(__file__).parent / ".env"
    load_dotenv(dotenv_path=env_path)

    # 2. 验证 key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print(f"[ERROR] DEEPSEEK_API_KEY 未在环境变量中找到")
        print(f"        请在 {env_path} 里填实际 key")
        sys.exit(1)

    if api_key == PLACEHOLDER:
        print(f"[ERROR] DEEPSEEK_API_KEY 还是占位符 {PLACEHOLDER!r}")
        print(f"        请编辑 {env_path}, 把右边换成真实 key 再跑")
        sys.exit(1)

    print(f"[OK] API key loaded (length={len(api_key)})")
    print(f"[OK] base_url = {DEEPSEEK_BASE_URL}")
    print(f"[OK] model    = {DEEPSEEK_MODEL}")
    print()

    # 3. 调一次 API
    client = OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)
    print("[call] requesting deepseek-v4-flash with 'say hello' ...")
    response = client.chat.completions.create(
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": "say hello"}],
    )

    # 4. 打印响应
    print()
    print("=" * 60)
    print("Response:")
    print("=" * 60)
    print(response.choices[0].message.content)
    print("=" * 60)
    print()
    print(f"[done] model={response.model}  "
          f"usage={response.usage}")


if __name__ == "__main__":
    main()
