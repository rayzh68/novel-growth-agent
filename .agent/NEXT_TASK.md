# NEXT_TASK

## Immediate Task
先停止继续修 research_pipeline.py 的 trial-chapters 补丁。

## Step 1
检查当前 Git 状态：

git status

## Step 2
如果 research_pipeline.py 被污染，先恢复：

git restore research_pipeline.py

## Step 3
重新编译核心文件：

python -m py_compile `
market_profile_builder.py `
research_pipeline.py `
research\runner.py `
research\batch_runner.py `
research\cleaner.py `
research\analyzer.py

## Step 4
设计商业验证模块，但不要先写代码。

需要确认：
- 全本原文输入位置。
- 当前是否已有切章代码。
- 如果没有，商业验证模块内置最小切章逻辑。
- 输出路径：
  output/commercial_validation/book_001_validation.json

## Step 5
商业验证模块应作为 main.py 的子命令，而不是单独启动文件：

python main.py validate --book book_001

## Current Design Target
商业验证输入：
- 全本 TXT。
- 自动切章。
- 抽取前10~20章。
- 中间抽几章。
- 结尾抽几章。

商业验证输出：
- hook_strength
- genre_fit
- binge_potential
- adaptation_difficulty
- monetization_potential
- overall_score
- recommendation:
  - SKIP
  - TEST_10_CHAPTERS
  - TEST_50_CHAPTERS
  - FULL_PIPELINE
