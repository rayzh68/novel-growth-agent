# PROJECT_STATE

## Project
novel-growth-agent

## Current Stable Facts
- GitHub 已同步到新电脑。
- 新电脑依赖安装完成。
- 核心文件曾编译通过。
- research_pipeline.py 后续被多次补丁污染，需要回滚/整理。
- 当前 Growth System 依赖 Story Bible / Reader / Reviewer / Market Research。
- 当前发现 market_profile_builder.py 输出存在污染：
  - story_seeds 偏向人名/实体。
  - reader_signals 偏向读者情绪词。
  - research_queries 出现 happens next / chef kiss 等无效查询。
  - core_themes 为空。
  - market_drivers 数量过少。

## Key Decision
商业验证阶段必须与 Growth System 隔离。

原因：
- 商业验证面向“新书刚拿到、没有 Story Bible / Reader / Reviewer”的场景。
- Growth System 面向“已有生产工厂产物后的增长素材生成”。
- 两者输入不同，强行合并会污染 research_queries 和 market_profile。

## New Architecture Direction
全本原文
→ 切章 / 抽样
→ 商业验证模块
→ 判断是否值得翻译前50章验证
→ 值得才进入 Story Bible / Reader / Reviewer / Growth System

## Current Risk
不要继续把 --trial-chapters 塞进 research_pipeline.py。
不要继续在 market_profile_builder.py 里修补商业验证逻辑。
