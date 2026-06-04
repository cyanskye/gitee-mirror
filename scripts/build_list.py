#!/usr/bin/env python3
"""动态生成需要镜像到 Gitee 的仓库名单。

规则：
  - 抓取 GitHub 用户「自己创建（非 fork）的公开仓库」，自动包含未来新建的；
  - 自动排除 fork 和私有仓库；
  - 再去掉 EXCLUDE 环境变量里点名的仓库。

输出：逗号分隔的仓库名（喂给 hub-mirror-action 的 static_list）。

环境变量：
  GITHUB_USER  GitHub 用户名，默认 cyanskye
  GH_TOKEN     GitHub token（提高速率上限，可选）
  EXCLUDE      不想同步的仓库，逗号/空格分隔，可留空
"""
import os
import json
import urllib.request

USER = os.environ.get("GITHUB_USER", "cyanskye")
TOKEN = os.environ.get("GH_TOKEN", "")
EXCLUDE = {x.strip() for x in os.environ.get("EXCLUDE", "").replace(",", " ").split() if x.strip()}


def fetch_repo_names():
    names, page = [], 1
    while True:
        headers = {"Accept": "application/vnd.github+json"}
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
        req = urllib.request.Request(
            f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}",
            headers=headers,
        )
        data = json.load(urllib.request.urlopen(req))
        if not data:
            break
        for r in data:
            if r["fork"] or r["private"] or r["name"] in EXCLUDE:
                continue
            names.append(r["name"])
        page += 1
    return sorted(set(names))


if __name__ == "__main__":
    print(",".join(fetch_repo_names()))
