# 三项目训练与评测入口就绪审计（2026-10-23 v2）

结论：**三个新版项目均尚不具备直接启动 A100 完整训练 smoke 的条件。** 已有 CPU 参考模块和旧版训练经验可以复用，但不是三个新版训练入口已实现的证据。本轮没有下载权重、安装依赖、运行训练或调用付费 API。

审计范围为仓库 `src/`、`scripts/`、`tests/`、`tiny_posttrain/` 和三项目蓝图；检查了工作区及其父目录适用的 `AGENTS.md`，未发现。机器可读结果与源码 SHA 见同目录 `training_readiness_20261023_v2.json`。数据导出与几何原标注关联由同轮独立工作推进，本报告不代替其验收。

## 1. 本轮实际执行的 CPU 检查

使用现成 `python`：Python 3.12.14、PyTorch 2.14.1+cpu、Transformers 4.57.6、TRL 1.16.0、PEFT 0.19.0、Datasets 4.7.0、Accelerate 1.10.1；`torch.cuda.is_available()=False`，CUDA runtime 为 null。

- 导入新版 losses、OPD 契约、数学验证、几何解析，以及旧版 training/evaluation：通过。
- `python -m tiny_posttrain.cli --help`：退出码 0，显示旧版 GSM8K CLI；仅支持 sft/grpo 阶段，没有新版 OPD/VL 入口。
- `python -m pytest tests/test_losses_and_masks.py tests/test_opd_contract.py tests/test_geometry_parser.py tests/test_math_verifier.py -q`：**72 passed in 6.99s**。
- `python -m pytest tiny_posttrain/tests/test_trainers.py::test_mask tiny_posttrain/tests/test_trainers.py::test_grpo_full_batch_contract tiny_posttrain/tests/test_sft_preflight.py -q`：**3 passed in 18.52s**。仅执行 mask、配置和 preflight 测试，没有调用 Trainer.train。

合计 75 个针对性 CPU 检查通过。它们验证公式/shift/mask、接口断言及旧版配置，不验证 7B/VL 实际加载、生成、反向或显存。

## 2. 项目一：7B 数学 SFT／GRPO／Dr.GRPO

状态：**正式入口缺失，暂不可直接上卡训练。**

存在：`src/losses/reference.py:10` 有 SFT shift 参考；`:17` 有 GRPO/Dr.GRPO 优势；`:29` 有 token policy loss。参考文件明确声明不是 GPU trainer。现有数据脚本与 token 审计不做模型更新。

缺失：清单建议的 `scripts/train_project1_sft.py`、`scripts/train_project1_rl.py`、`scripts/evaluate_math.py` 仍不存在。没有新版独立运行配置／Linux CUDA 锁文件／7B 数据适配入口。SFT 的 assistant-only labels、EOS、拒绝截断、数据 manifest 与参数恢复尚未通过新版入口接通验收；E0→直接 RL 与同一 SFT 起点→GRPO/Dr.GRPO 的固定 reference 还没有实际接线。

可复用但不可混算：`tiny_posttrain/src/tiny_posttrain/training.py:144` 有真实旧训练入口；`:117` 建立 TRL 配置，`:198` 恢复 checkpoint，`:234` 初始化 GRPO。`tiny_posttrain/configs/smoke.json` 仍是 1.5B GSM8K，SFT 长度 1024／RL 回答 512，并非新版 7B 的 1500～3000 token 数据协议。`resources.py:98` 固定读取旧 `data/gsm8k/splits.json`，不能仅换模型名就宣称已迁移。

正式 Math-Verify 0.9.0 已在 `scripts/math_verify_pilot_worker.py` 隔离接入 API pilot，但 `src/evaluation/math_verifier.py` 仍是受限表达式验证器，文件头明确不是完整 MATH verifier。尚无统一模型预测缓存→逐题恢复→正式判分→分组指标的新版评测入口。

最短待办：先实现数学评测与 SFT smoke 配置、接通封存数据/模板/版本；再实现 GRPO/Dr.GRPO 两配置与固定 reference；在 CPU 检查真实样本 labels/EOS/长度/异常策略，之后才租卡验证最长样本完整更新与恢复。

## 3. 项目二：双教师在线蒸馏

状态：**张量契约和 KL 单元检查通过，真实 OPD 训练及评测入口缺失。**

存在：`src/teachers/opd_contract.py:26` 验证学生 ID、attention mask、prefix，返回目标位置 response mask；`src/losses/reference.py:45` 实现共同词表重归一化和因果 shift，`:63` 实现 reverse KL 并 detach 教师。`tests/test_opd_contract.py` 验证左右 padding、同一张量与 prefix 错误；本轮全部通过。

缺失：`scripts/train_project2_opd.py`；学生真实生成→完整 prefix 转交教师→teacher.eval/no_grad→KL→学生更新→日志/保存/恢复的主循环；实际生成前共同支持外 token mask；共同词表外概率质量监测；域切换/卸载与恢复后的 domain/data position；真实数学/代码统一评测入口。`project_blueprints/sources/` 是上游来源快照，不是已安装/可调用的本地训练器。

代码数据有测试并不代表存在模型评测入口。`scripts/audit_official_code_benchmarks.py` 用于基准源审计，不能替代模型生成、代码提取、Linux 沙箱、HumanEval+/MBPP+ 判分与逐题恢复。dev 规格审核及目标 Linux 的隔离/超时/清理仍须完成。

最短待办：实现单教师、单域最小闭环；复用已审计 tokenizer 与契约，首先检查相同 prefix/position IDs/shift、教师无梯度而学生有梯度，冻结 checkpoint 身份和数据顺序；再加入双域路由。不要一开始同时驻留全部教师。

## 4. 项目三：多模态几何推理

状态：**几何 AST/评分模块通过；VL 训练、诊断生成和正式评测入口缺失。**

存在：`src/evaluation/geometry_perception_parser.py:45` 解析事实，`:108` 规范化，`:113` 解析响应，`:123` 计算已覆盖关系的 perception F1。CPU 测试不证明原图上的标注正确。

缺失：固定 revision 的 Qwen2.5-VL-3B processor/模型下载与图像 token 预算配置；EasyR1 commit/依赖锁与本地调用入口；Normal/No-image/Black-image/区域遮挡的真实生成驱动；视觉冻结/语言 LoRA 参数核查；感知标签有效 mask 与完整更新/恢复。原标注关联与 MathVista 重叠脚本即使本轮完成，也不等价于视觉独占金标验收完成。

最短待办：先用已关联真实图文构造两例 processor 输入检查，完成视觉独占训练标注审核并冻结 dev 诊断协议，再编写 VL 训练入口。该项目不阻塞项目一、二的工程 smoke。

## 5. 依赖锁与恢复边界

`tiny_posttrain/requirements.lock.txt:1` 明示是 Python 3.12 CPU 环境，torch/CUDA 单独验收；项目 metadata 的 dependencies 为空，不能仅 `pip install -e tiny_posttrain` 推断 GPU 依赖齐全。当前环境版本是实测值，不是推荐的 Linux GPU 组合，本轮没有验证其在 CUDA 上兼容。

旧 `tiny_posttrain/src/tiny_posttrain/storage.py:89` 要求 optimizer、scheduler、trainer_state、rng_state、resume、adapter 配置；`:94` 拒绝身份变化恢复。旧测试文件包含中断/跨进程恢复和 reference 核验，但本轮没有运行这些训练测试。新版三项目尚无相应 checkpoint 主链路，不能把旧版测试记录转移为新版验收。

上 A100 前最小交付：锁定一种 80GB 起始配置的 Python/PyTorch/CUDA/Transformers/TRL/PEFT 组合及模型 revision，写出真实可执行 smoke 命令；提供新入口的 CLI/参数冲突检查与数据/模板 SHA；明确保存 optimizer/scheduler/RNG/step/adapter/data position。40GB、QLoRA、vLLM、融合优化另开配置验收。

上卡后才可判定：加载→最长样本 forward/backward/optimizer step→中断恢复→RL rollout+完整更新→OPD 单教师真实更新；记录峰值 allocated/reserved、设备总显存、速度、有效梯度和异常。加载成功或 CPU 75 passed 均不代替这些门槛。
