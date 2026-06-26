# gitee-mirror

自动将 GitHub 仓库镜像到 Gitee —— **零手动维护同步名单**，动态抓取你名下所有非 fork 的公开仓库，每 6 小时自动同步一次。

## 为什么需要这个

国内访问 GitHub 不稳定，很多开发者在 Gitee 上维护一份镜像方便国内用户 clone/浏览。但手动维护同步名单很烦——新建一个仓库就要去 workflow 里加一行，忘了就漏掉。

这个项目**不需要维护名单**。每次运行自动从 GitHub API 抓取你名下的仓库列表，过滤掉 fork 和私有仓库，新仓库自动纳入同步范围。

## 工作流程

```
┌─────────────────────────────────────────────────────┐
│  每 6 小时 / 手动触发                                  │
├─────────────────────────────────────────────────────┤
│  1. 动态生成名单                                       │
│     GitHub API → 抓取名下非 fork 公开仓库 → 去重排序       │
├─────────────────────────────────────────────────────┤
│  2. 镜像到 Gitee                                      │
│     git clone + Gitee API 建仓 + git push --mirror     │
├─────────────────────────────────────────────────────┤
│  3. 同步公开/私有状态                                   │
│     查 GitHub 仓库可见性 → PATCH Gitee 仓库设置          │
├─────────────────────────────────────────────────────┤
│  4. 改写 README 链接                                   │
│     GitHub 地址 → Gitee 地址（仅改写自己命名空间下的链接）  │
└─────────────────────────────────────────────────────┘
```

## 快速上手

### 1. Fork 本项目

Fork 到你自己账号下，然后把 workflow 和脚本里的 `cyanskye` 替换为你的 GitHub/Gitee 用户名。

### 2. 配置 Secrets

在仓库 Settings → Secrets and variables → Actions 中添加三个 secret：

| Secret | 说明 |
|--------|------|
| `GITEE_PRIVATE_KEY` | SSH 私钥（用于 git push 到 Gitee） |
| `GITEE_TOKEN` | Gitee 私人令牌（用于创建仓库和 API 调用） |
| `GITHUB_TOKEN` | GitHub 自动提供，无需手动配置 |

**获取 Gitee Token**：https://gitee.com/profile/personal_access_tokens ，勾选 `projects` 权限。

**配置 SSH 公钥**：在 Gitee SSH 公钥设置中添加对应 `GITEE_PRIVATE_KEY` 的公钥。

### 3. 设置排除名单（可选）

在 `.github/workflows/mirror.yml` 顶部修改 `EXCLUDE` 变量：

```yaml
env:
  EXCLUDE: "不想同步的仓库1, 仓库2"
```

留空则同步所有非 fork 公开仓库。

### 4. 触发同步

- **自动**：每 6 小时运行一次
- **手动**：Actions 页面 → Mirror GitHub to Gitee → Run workflow

或者用 CLI：

```bash
gh workflow run mirror.yml --repo <你的用户名>/gitee-mirror
```

## 目录结构

```
.
├── .github/workflows/mirror.yml   # GitHub Actions 工作流
├── scripts/
│   ├── build_list.py              # 动态生成同步名单
│   └── rewrite_readme.py          # 改写 README 中的链接
└── README.md
```

## 注意事项

- 使用 `git push --mirror --force`，**请勿在 Gitee 端直接改代码**（会被覆盖）
- **零外部 Action 依赖**，镜像逻辑完全自控，不会因第三方 Action 更新而挂掉
- 只同步你自己创建的公开仓库，fork 和私有仓库自动跳过
- README 改写只处理你自己命名空间下的链接，不会误改指向第三方的 GitHub 地址

## License

MIT
