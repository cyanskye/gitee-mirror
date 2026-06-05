#!/usr/bin/env python3
"""镜像后处理：把 Gitee 各仓库 README 里指向作者自己 GitHub 仓库的地址改写为 Gitee 地址。

- 只改写 GITEE_USER 自己命名空间下的链接（clone / raw / 仓库链接），
  绝不改动指向第三方的 github.com 链接（否则在 Gitee 上会变成死链）。
- 通过 Gitee Contents API 直接在 Gitee 端提交，不碰 GitHub，也不走 git push
  （因此不会触发 Gitee 的「隐藏邮箱」推送钩子）。
- 需在每次镜像之后运行：mirror 的 force_update 会把 README 重置回 GitHub 版本，
  本步骤再把链接改回 Gitee，保证 Gitee 上看到的始终是国内地址。

环境变量：
  GITEE_USER   Gitee 用户名，默认 cyanskye
  GITEE_TOKEN  Gitee 私人令牌（必需）
  REPO_LIST    逗号/空格分隔的仓库名（由工作流传入动态名单）
"""
import os
import re
import json
import base64
import urllib.parse
import urllib.request
import urllib.error

USER = os.environ.get("GITEE_USER", "cyanskye")
TOKEN = os.environ["GITEE_TOKEN"]
REPOS = [r.strip() for r in os.environ.get("REPO_LIST", "").replace(",", " ").split() if r.strip()]
API = "https://gitee.com/api/v5"


def call(method, path, params):
    if method == "GET":
        req = urllib.request.Request(f"{API}{path}?" + urllib.parse.urlencode(params), method="GET")
    else:
        req = urllib.request.Request(f"{API}{path}", data=urllib.parse.urlencode(params).encode(), method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.load(e)
        except Exception:
            return e.code, {}


def rewrite(text):
    """只改写 USER 自己命名空间下的 github 地址，返回 (新文本, 是否有改动)。"""
    orig = text
    # raw.githubusercontent.com/USER/REPO/BRANCH/... -> gitee.com/USER/REPO/raw/BRANCH/...
    text = re.sub(rf"raw\.githubusercontent\.com/{re.escape(USER)}/([^/\s)]+)/",
                  rf"gitee.com/{USER}/\1/raw/", text)
    # SSH clone: git@github.com:USER/ -> git@gitee.com:USER/
    text = text.replace(f"git@github.com:{USER}/", f"git@gitee.com:{USER}/")
    # https 链接 / clone: github.com/USER/ -> gitee.com/USER/
    text = re.sub(rf"github\.com/{re.escape(USER)}/", f"gitee.com/{USER}/", text)
    return text, text != orig


def main():
    for repo in REPOS:
        code, meta = call("GET", f"/repos/{USER}/{repo}", {"access_token": TOKEN})
        if code != 200:
            print(f"{repo}: 跳过（取仓库信息 HTTP {code}）")
            continue
        branch = meta.get("default_branch") or "master"
        code, rd = call("GET", f"/repos/{USER}/{repo}/readme", {"access_token": TOKEN, "ref": branch})
        if code != 200 or "content" not in rd:
            print(f"{repo}: 无 README，跳过")
            continue
        text = base64.b64decode(rd["content"]).decode("utf-8", "ignore")
        new, changed = rewrite(text)
        if not changed:
            print(f"{repo}: README 无需改写")
            continue
        code, _ = call("PUT", f"/repos/{USER}/{repo}/contents/{rd['path']}", {
            "access_token": TOKEN,
            "content": base64.b64encode(new.encode()).decode(),
            "message": "docs: README 中的 GitHub 地址改写为 Gitee（镜像自动维护）",
            "sha": rd["sha"],
            "branch": branch,
        })
        print(f"{repo}: 改写 README -> HTTP {code}")


if __name__ == "__main__":
    main()
