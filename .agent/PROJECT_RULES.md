# PROJECT RULES

## Rule 1
增长系统只负责商业评估与增长策略，禁止包含生产工厂流程。

## Rule 2
核心目标：
发现值得投入的项目，不生产小说。

## Rule 3
商业验证阶段只评估：
- Commercial Promise
- Creative Potential
- Binge Potential
- Test50 Value
- Investment Attractiveness

## Rule 4
Western Fit 与 Translation Risk 仅参考，不作为淘汰条件。

## Rule 5
不得在代码中硬编码：
- 题材
- 榜单
- 分类
- 标签
统一通过 config/market_taxonomy.json 加载。

## Rule 6
新增功能优先合并现有模块，禁止一个功能新增一个启动文件。

## Rule 7
代码修改完成后必须：
python -m py_compile
验证。
