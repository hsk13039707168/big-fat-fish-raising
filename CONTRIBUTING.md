# 贡献指南

感谢你愿意为《大肥鱼养成计划》出一份力！这是一个纯前端小游戏，改动门槛很低 —— 会改 HTML / CSS / JS 就能上手。

## 一、开始之前

- 提交 Issue 前先搜一下 [已有 Issue](../../issues)，避免重复。
- 涉及**新玩法、大改数值、UI 重构**的改动，建议先开一个 Issue 讨论，避免做完被打回。
- 修 Bug、改文案、补文档这类小改动可以直接开 PR。

## 二、本地开发

```bash
git clone https://github.com/hsk13039707168/big-fat-fish-raising.git
cd big-fat-fish-raising
python -m http.server 8123      # 或 npx serve .
# 浏览器打开 http://127.0.0.1:8123/大肥鱼养成计划.html
```

**强烈建议用本地服务器而不是双击打开**：`file://` 下 Canvas 会被浏览器污染，白底去底会静默降级，你会误以为抠图功能坏了。

改动完成后，请确认单文件版仍然能正常构建：

```bash
python tools/bundle.py
node --check tools/.bundle_check.js    # 校验注入的内嵌脚本语法
```

## 三、代码规范

本项目**没有构建工具、没有 linter**，靠约定保持一致：

| 项目 | 约定 |
| --- | --- |
| 缩进 | 2 个空格 |
| 引号 | JS 统一单引号，HTML 属性双引号 |
| 分号 | 保留 |
| 命名 | 系统级对象用大驼峰（`DragSystem` / `ComputeSystem`），函数与变量小驼峰 |
| 注释 | 修改处请写 `// BUG FIX #N：现象 → 根因 → 修复`，便于回溯 |
| 配置 | 数值、素材路径、台词一律放**配置区**（`ASSETS` / `STAGES_M1` / `STAGES_M2` / `ChipMap` / `ITEMS` / `TUNE`），不要在逻辑里硬编码 |
| 兼容性 | 只用浏览器原生 API，不引第三方库；DOM 操作前判空 |

### 提交信息（Conventional Commits）

```
feat:     新增功能        feat(mode1): 新增第六阶段进化
fix:      修复缺陷        fix(drag): 快甩时命中判定失效
docs:     文档            docs: 补充素材替换说明
refactor: 重构            refactor: 拆分 DialogSystem
perf:     性能            perf: 粒子上限动态化
test:     测试            test: 补充进化流程用例
chore:    杂项            chore: 更新 .gitignore
```

## 四、Pull Request 流程

1. `git checkout -b feat/简短描述`（或 `fix/` `docs/`）
2. 写代码 + 本地验证（桌面 + 手机窄屏各看一眼）
3. 提交：`git commit -m "feat: 简要描述改动"`
4. 推送：`git push origin 你的分支名`
5. 开 PR，按 [PR 模板](.github/PULL_REQUEST_TEMPLATE.md) 填写，**附上改动前后的截图**（视觉改动必须）

PR 会被检查的点：

- [ ] 桌面（1280px）与手机（390px）下都不破版
- [ ] 控制台无报错
- [ ] 涉及素材改动时，`python tools/bundle.py` 仍能构建成功
- [ ] 数值改动写在配置区，并有注释说明意图
- [ ] `CHANGELOG.md` 的 `Unreleased` 段已补充条目

## 五、素材贡献

- 立绘建议 768×1024 或 1024×1024，主体居中、头部留白；道具建议 256×256 透明底 PNG。
- 放到 `assets/`（ASCII 文件名），中文原图放 `素材包/` 并在 `ALT_NAMES` 里补映射。
- ⚠️ **请确保你拥有所提交素材的合法授权**。涉及第三方商标、真人肖像的素材请勿提交。

## 六、发布流程（维护者）

1. 更新 `CHANGELOG.md`：把 `Unreleased` 转入新版本号并写日期
2. `python tools/bundle.py -o dist/大肥鱼养成计划_X.Y.Z.html`
3. 提交并打标签：`git tag -a vX.Y.Z -m "vX.Y.Z"`
4. 推送：`git push origin main --tags`
5. 创建 Release 并**上传 `dist/` 里的单文件版**作为附件

## 七、行为准则

参与本项目即表示你同意遵守 [行为准则](./CODE_OF_CONDUCT.md)。

有问题随时开 Issue 讨论 —— 欢迎各种形式的贡献：代码、素材、文档、错别字，甚至只是一个好玩的点子。
