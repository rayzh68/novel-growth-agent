# PROJECT RULES

## Rule 1：系统边界

增长系统只负责商业评估、增长策略、投放验证、反馈分析。

禁止包含生产工厂流程：
- Story Bible
- Rewrite
- Review
- Finalize
- 翻译
- 改编
- 全本生产

## Rule 2：核心目标

增长系统的目标不是生产小说，而是：

发现机会
验证机会
投入资源
放大收益
动态淘汰

## Rule 3：商业验证评分维度

商业验证阶段核心评估：
- Commercial Promise
- Creative Potential
- Binge Potential
- Test50 Value
- Investment Attractiveness

## Rule 4：参考指标边界

Western Fit 与 Translation Risk 只作为参考信息。

高迁移成本不等于低商业价值。

商业验证阶段优先判断故事骨架是否值得投资，而不是是否容易翻译。

## Rule 5：禁止硬编码题材

不得在 Python 代码中长期硬编码：
- 题材
- 榜单
- 分类
- 标签
- 单本小说特定词
- 人物名

分类、榜单、题材词统一通过：
config/market_taxonomy.json

或市场抓取结果引用。

## Rule 6：允许 V0.1 规则，但必须标记技术债

商业验证 V0.1 可以使用规则启发式方法。

但不得长期依赖具体题材关键词。

最终应升级为结构信号分析：
- 冲突密度
- 悬念密度
- 反转密度
- 目标驱动
- 情绪压力
- 剧情推进
- 广告角度可生成数量

## Rule 7：解释性优先

商业验证结果不能只有分数。

必须逐步增加：
- reasons
- risks
- evidence_samples
- suggested_next_action

## Rule 8：文件控制

独立模块可以新增文件。

但禁止为了小功能新增大量层级或启动文件。

新增前必须判断是否可放入现有模块。

## Rule 9：代码验证

所有代码修改完成后必须运行：

python -m py_compile

核心文件变更后必须检查：

git status
