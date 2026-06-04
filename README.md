# gitee-mirror

把 GitHub 账号 cyanskye 下**我自己创建的仓库**镜像到 Gitee 账号 cyanskye（不含任何 fork）。

- 方向：GitHub（主）→ Gitee（镜像，只读）
- 范围：白名单 static_list（见 .github/workflows/mirror.yml），只同步列出的仓库，所有 fork 自动排除
- 频率：每 6 小时定时 + 随时手动触发
- 认证：推送走 SSH 私钥（GITEE_PRIVATE_KEY）；Gitee 令牌（GITEE_TOKEN）仅用于自动建仓
- force_update=true，请勿在 Gitee 直接改代码（会被覆盖）

## 新增一个要同步的仓库
编辑 mirror.yml 里的 static_list，逗号后加上仓库名即可。

手动触发：gh workflow run mirror.yml --repo cyanskye/gitee-mirror
