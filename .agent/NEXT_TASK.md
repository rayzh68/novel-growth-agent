# NEXT TASK

## 当前目标

继续完善增长系统商业验证模块 Commercial Validation。

## 当前已完成

已新增：

core/commercial_validation.py

该文件是商业验证核心计算模块。

## 下一步 P1

不要继续改 research_pipeline.py。

下一步只做两件事之一：

1. 给 commercial_validation.py 增加解释性输出：
   - reasons
   - risks
   - evidence_samples
   - suggested_next_action

或：

2. 设计调用入口：
   - 不新增独立启动文件
   - 优先考虑 main.py 子命令
   - 输出到 output/commercial_validation/

## 暂不做

- 不接入 Story Bible
- 不接入 Reader
- 不接入 Reviewer
- 不接入生产工厂
- 不做全本生产
- 不继续修 research_pipeline.py

## 近期开发顺序

P1：增强 commercial_validation.py 解释性  
P2：增加章节抽样策略  
P3：增加 main.py validate 子命令  
P4：输出 commercial_validation JSON  
P5：建立 project database  
