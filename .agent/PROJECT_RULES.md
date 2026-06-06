# PROJECT_RULES

## Non-negotiable Rules
1. 不随便新增启动文件。
2. 不把小功能拆成一堆零散脚本。
3. 不把商业验证逻辑混进 Growth Profile。
4. 不在 Python 代码里硬编码具体题材词、分类词、人物词。
5. 分类词可以使用，但必须来自可调用词库或市场抓取结果。
6. taxonomy / ranking terms 可以放在 config 或 data 中，代码只加载使用。
7. input / output / .venv / project_audit / archive 不作为硬编码扫描对象。
8. 修改前先查现有代码位置，不猜。
9. 代码修改必须给完整 PowerShell 命令，不要给零碎片段。
10. 每次改完必须 py_compile 验证。

## Current Core Files
- market_profile_builder.py
- research_pipeline.py
- research/runner.py
- research/batch_runner.py
- research/cleaner.py
- research/analyzer.py

## Important Boundary
Growth System:
- 使用 Story Bible / Reader / Reviewer / Market Research。
- 输出 market_profile / market_drivers / research_queries。

Commercial Validation:
- 使用全本原文切章抽样。
- 没有 Story Bible / Reader / Reviewer。
- 输出是否值得翻译、是否值得先做50章验证。
- 必须单独输出到 output/commercial_validation/。
