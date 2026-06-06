# PROJECT STATE

更新时间：2026-06-06

## 项目定位

novel-growth-agent 是增长系统。

核心目标：
用最小成本发现值得投入的小说项目，并负责后续增长策略。

增长系统不是生产工厂，不负责改编、重写、翻译、Story Bible、Review、Finalize。

## 增长系统职责

1. 中文原始小说商业价值评估

用于判断一本刚拿到的中文原创网文是否值得投入。

核心输出：
- Commercial Promise
- Creative Potential
- Binge Potential
- Test50 Value
- Investment Attractiveness
- Recommendation

2. 多书排序与项目优先级

用于在多本候选小说中排序，决定先验证哪本、暂停哪本、放弃哪本。

3. 50章验证增长

读取生产工厂产出的前50章英文内容，生成：
- 广告素材方向
- SEO策略
- Landing Page策略
- 投放计划
- 验证指标

4. 全本增长

当英文全本完成后，增长系统负责：
- 全本推广策略
- SEO矩阵
- 内容矩阵
- 广告矩阵
- 持续放量策略

5. 市场反馈分析

根据投放和站点数据判断：
- 继续投入
- 降低优先级
- 暂停
- 放弃

## 已完成

- GitHub 同步。
- 新电脑环境完成。
- .agent 项目文档建立。
- config/market_taxonomy.json 占位词库建立。
- 删除旧审计 zip。
- 删除 run_analysis 旧备份文件。
- 新增 core/commercial_validation.py。

## 当前商业验证模块状态

文件：
core/commercial_validation.py

状态：
Rule-based V0.1

定位：
- 只做商业验证计算。
- 不读写文件。
- 不跑 pipeline。
- 不调用 Research。
- 不调用生产工厂。

当前技术债：
- 仍包含少量中文触发词。
- 当前结果偏分数化，解释性不足。
- 后续需要从关键词规则升级为结构信号规则。

后续方向：
- 增加 reasons。
- 增加 risks。
- 增加 evidence_samples。
- 增加 suggested_next_action。
- 增加章节抽样：前段 + 中段 + 结尾。
