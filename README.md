# gitee-mirror

把 GitHub 账号 cyanskye 下的所有 public 仓库自动镜像到 Gitee 账号 cyanskye。

- 方向：GitHub（主）→ Gitee（镜像，只读）
- 频率：每 6 小时定时 + 随时手动触发（Actions → Run workflow）
- 认证：推送走 SSH 私钥（GITEE_PRIVATE_KEY）；Gitee 令牌（GITEE_TOKEN）仅用于自动建仓
- 私有仓库不同步；force_update=true，请勿直接在 Gitee 改代码（会被覆盖）

手动触发：gh workflow run mirror.yml --repo cyanskye/gitee-mirror
改频率：编辑 .github/workflows/mirror.yml 里的 cron
