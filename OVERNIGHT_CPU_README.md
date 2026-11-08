# 三项目 CPU 基础设施

本目录新增 `src/`、`tests/`、`data/`、`reports/`、`scripts/`；旧 `tiny_posttrain/` 的模型、训练代码和历史结果不改动。
这是 CPU 数值参考、元数据审计和离线数据工程，不是三个项目已完成训练。

## 运行

在仓库根目录执行（本机已经验证的 Python）：

```powershell
$env:CUDA_VISIBLE_DEVICES = ''
$env:HF_HUB_DISABLE_PROGRESS_BARS = '1'
python -m src.teachers.tokenizer_audit
python -m src.data.prepare_math_data
python -m scripts.run_cpu_demo
python -m pytest tests -v
```

前两个命令只读取公开模型元数据/tokenizer、下载公开数据集，没有模型权重。
后两个命令离线执行；真实产物集成测试要求前两个命令已成功生成报告和 JSONL。
新环境请按 `reports/cpu_environment.json` 安装相应 CPU 依赖，不要直接安装 CUDA 版 torch。
可替换为其他环境的 `python`，代码没有写死本机绝对路径。

## 模块

- `src/losses/reference.py`：SFT、GRPO/Dr.GRPO、对齐 FKL/RKL、固定权重 FKL 融合。
- `src/teachers/tokenizer_audit.py`：明确文件白名单、真实 revision、逐 token 比对和 64 条编码测试。
- `src/data/prepare_math_data.py`：原文/规范化哈希、三元组 Jaccard、256 题 dev、隔离证据及 manifest。
- `src/evaluation/math_verifier.py`：受限 AST 表达式，不调用 eval；最终标记提取、冲突/截断拒绝。
- `src/synthesis/async_client.py`：SQLite＋JSONL 恢复、预留预算账本、有限传输重试、最多三次内容重采样、限速。
- `src/evaluation/geometry_perception_parser.py`：有限 schema、确定性序列化、覆盖感知的去重 F1。

## 关键边界

1. 四个 tokenizer 的原始 token 映射一致，但 Math 教师的 chat template 不同。复用学生的相同 token 前缀，不独立套各模型模板。
2. 切片边界来源于真实报告，不是 `min(vocab_size)`。无效行在生成前屏蔽，概率在共同支持上重新归一化。真实尾部质量需日后加载权重测量。
3. SFT 忽略目标对应的 logits 槽位梯度为零，不表示共享模型参数或 prompt token embedding 无梯度。
4. 去重为词法启发式，阈值 0.85 在合成用例上验证，不证明无语义重复/预训练污染。MATH 源 test 包含 MATH-500，不用于调参。
5. 数学判分器是有意受限的参考实现，不支持所有数学对象、单位换算或官方复杂答案协议；不把拒绝解析当作推理错误的证明。
6. 几何关系仅支持注册的有限 schema；Tangent(AB,O) 中 O 是圆心的 schema 约定。单位不自动换算。覆盖不完整的类别不因缺标签而惩罚；无可信标签感知奖励为 0、mask=False。
7. 合成客户端默认 dry-run；唯一可执行 transport 是本地 MockTransport，没有 URL、密钥读取或付费适配器。预算单位为测试用模拟整数，不是现实费用。
8. BlindRequest 拒绝 reference/answer/solution 等非白名单字段，但不能靠字符串算法证明任意 problem/conditions 没有人工塞入答案。初始条件仍需来源审计；正常题目数值不会被删掉。
9. 缓存同时记录成功/拒绝/传输失败；验证失败中断可重用已保存输出。外部服务返回到本地落盘之间的崩溃窗口无法提供端到端 exactly-once，若将来接真实服务必须增加请求幂等/未知状态核查；当前无此网络服务。
10. 单客户端限速；SQLite 预算账本跨同数据库客户端有效。JSONL 是原子镜像，可在 SQLite 丢失时恢复；不要并发用不同数据库写同一镜像路径。失败请求保守保留预算，不自动退款。

## 产物入口

- `reports/overnight_execution_summary.md`：分阶段进度、完整文件路径、实际统计、最终完整 pytest 日志。
- `reports/tokenizer_alignment_report.json`：机器可读真实词表审计。
- `reports/tokenizer_alignment_summary.md`：可读审计结论。
- `data/math_manifest.json`：数据来源 revision、划分、文件行数和 SHA256。
- `reports/cpu_demo.json`：仅本地 Mock 的端到端示例，不是真实合成数据。

普通文本生成 API 不能直接替代任意学生前缀上的完整词表 OPD。白天接 API 前应单独完成接口、费用与请求来源审核。
