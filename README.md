# novel-growth-agent

网文市场推广增长 Agent 系统 V1 MVP。

## 核心原则

本项目采用统一控制入口：

```powershell
python main.py <command>
```

`agents\`、`core\`、`scripts\` 都是内部实现文件。日常使用不要直接运行多个 `.py` 文件，只使用 `main.py`。

## 目标

不是单纯生成广告素材，而是在尽量短的时间内找到可放量的正 ROI 组合。

第一阶段主渠道：

- 首选：Facebook / Instagram
- 第二：TikTok

## 系统边界

本系统负责：

- 市场定位
- 读者画像
- 卖点提炼
- Hook 生成
- Facebook / Instagram 广告文案
- TikTok 短视频脚本
- 落地页方案配置
- UTM 链接
- 投放计划
- CSV 数据分析
- 下一轮素材迭代
- growth_feedback.json

本系统不负责：

- 不改正文
- 不建站
- 不部署页面
- 不接广告 API
- 不自动花钱

## Windows 快速开始

在 PowerShell 中执行：

```powershell
cd D:\novel-growth-agent

py -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Copy-Item .env.example .env -Force

python main.py all --book book_001 --round round_001
```

或者直接运行：

```powershell
.\setup_windows.ps1
```

## 如果 PowerShell 不允许激活虚拟环境

执行一次：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

然后重新运行：

```powershell
.\.venv\Scripts\Activate.ps1
```

## 统一命令

### 1. 一键生成推广资产 + 运行数据分析

```powershell
python main.py all --book book_001 --round round_001
```

### 2. 只生成推广资产

```powershell
python main.py generate --book book_001
```

生成内容包括：市场定位、读者画像、卖点、Hook、Facebook广告、TikTok脚本、落地页方案、UTM链接、投放计划。

### 3. 只运行数据分析

```powershell
python main.py analyze --book book_001 --round round_001
```

生成内容包括：增长报告、下一轮计划、growth_feedback.json。

### 4. 从 novel-mvp 导入内容资产包

```powershell
python main.py import-book --source D:\novel-mvp\output\marketing_package\book_001 --book book_001
```

### 5. 导入广告数据 CSV

```powershell
python main.py import-report --source D:\somewhere\facebook_round_001.csv --type ad
python main.py import-report --source D:\somewhere\site_events_round_001.csv --type site
```

### 6. 导出反馈给 novel-mvp

```powershell
python main.py export-feedback --book book_001 --target D:\novel-mvp\input\growth_feedback
```

### 7. 查看当前输出状态

```powershell
python main.py status --book book_001
```

### 8. 清空 output 重新跑

```powershell
python main.py clean --yes
python main.py all --book book_001 --round round_001
```

## 使用 OpenRouter

编辑 `.env`：

```env
OPENROUTER_API_KEY=你的key
MOCK_LLM=0
MODEL_DEFAULT=openai/gpt-4o-mini
```

如果不配置 API key，系统仍可使用本地 fallback 跑通流程。

## 输出给建站系统的文件

```text
output\landing_briefs\book_001_landing_page_spec.json
output\landing_briefs\book_001_landing_page_copy.md
output\utm_links\book_001_utm_links.csv
```

## 输出给网文开发系统的反馈

```text
output\feedback\book_001_growth_feedback.json
```

## 主要输出位置

```text
output\marketing_profiles\
output\personas\
output\selling_points\
output\hooks\
output\creatives\
output\landing_briefs\
output\utm_links\
output\campaign_plans\
output\reports\
output\next_rounds\
output\feedback\
```
