# Shuffle-R1 单卡 CPU 复验与数据封板

## CPU 复验

代码冻结于独立 worktree `g4-logical-batch-prep-20261115` 的 `aa88b60`，基线为作者 `b863694f25d38d0e118761363dc5897bb9625e82`。已验证提交 diff 与 [归档补丁](shuffle-r1-source.patch) 一致。提交仅保存在本地。

环境为 Python 3.12.3、PyTorch 2.13.0+cpu、Ray 2.48.0、torchdata 0.11.0。按带 SHA256 的[依赖锁](requirements-cpu.lock.txt)冷装 83 个包。独立环境首次收集测试时发现 `mathruler` 导入的 `pylatexenc` 未作为依赖声明，已加入锁文件。定向五模块和仓库根目录发现的测试均为 37 通过、0 跳过，Git diff 检查通过。该作者基线没有跟踪的 pytest 测试文件。[安装日志](install.txt) · [五模块日志](cpu-five-modules.txt) · [全仓日志](cpu-full-repo.txt)

- 真实入口 `shuffle_r1.main` 使用 `shuffle_r1.fsdp.FSDPWorker`。CPU 测试处理完整逻辑批次、最后短块、选样和张量顺序。复审修补了 vLLM 返回新 `DataProto` 时策略版本元数据丢失的问题。在临时源码副本撤销修补后，两个对应测试都复现失败。[复现日志](policy-version-before-fix.txt)
- 固定轨迹测试验证了实际 actor loss、8 路参考微批权重、old log-prob、4 次优化器更新与异常梯度停止。CPU checkpoint 测试覆盖优化器、调度器、下一批次、ABS 索引、RNG、损坏拒绝及提交中断恢复。
- 从真实作者 Geometry3K 训练分片取 16 题，用固定 revision 的 Qwen2.5-VL tokenizer 与 fast processor 走实际 CPU collate，核验图像张量、图格和三轴位置编码。[真实数据日志](real-data-collate.txt)

## MMRL30k 原始数据封板

固定 revision `b362381652529d67ebc26f5e140bd0a54ba4647d`。7 个原始 Parquet 分片的大小和 SHA256 都与发布方一致。五个 split 共 34,711 行，逐行检查了 `problem`、`answer`、`source` 和内嵌图片。全部图片可解码，所有图片均以 bytes 提供，path 为空。官方 `train` 含 29,101 行，其中 Geometry3K 2,101 行、MM-EUREKA 27,000 行，规范化后的题干、图片与答案合计有 74 行重复。原始数据和逐行清单位于 `/home/xde10/.local/state/vlm-perception-reward-rl/mmrl30k-b362381`。[发布方固定版本](https://huggingface.co/datasets/XenoZLH/MMRL30k/tree/b362381652529d67ebc26f5e140bd0a54ba4647d) · [审计 JSON](mmrl30k-audit.json) · [逐行审计日志](mmrl30k-audit.txt)

| 官方 `train` 对照测试 split | 测试行数 | 图像 RGB 像素一致 | 规范化题干、图像与答案都一致 |
| --- | ---: | ---: | ---: |
| `geo3k_test` | 601 | 300 | 1 |
| `k12_test` | 808 | 275 | 0 |

表内计数是测试侧命中的行数。按解码后的图像尺寸和 RGB 像素做精确匹配，没有做近似图匹配。发布版也单列 `geo3k_train` 与 `k12_train`，两组的交叉结果见审计 JSON。原样发布的 `train` 未通过按图隔离这一条件，未从原始数据删除任何行，也未启动 G4 探针。作者启动脚本的 `@test` 是占位写法，这份发布快照需要显式选择 `geo3k_test` 或 `k12_test`。

## S5 恢复点

已核对 12 个正式 S4 完成标记。正式 S5 有 13 个模型，每个模型 9 个条件，共 117 个条件。Drive 的 67 个完成标记与暂停清单相同，逐一核对了条件、项目提交、模型 revision、GPU、依赖版本和条数。还剩 50 个条件。暂停点 `final-eval-20261115T023255Z-dc08` 保存的 `rl_ans/seed2/test_blind` 有完整 601 条预测，Drive 文件 SHA256 与暂停记录相同。[核对记录](s5-resume-verification.json)

本轮完成了 S5 只读核对，未分配 GPU。恢复时原运行器按结果身份复用 Drive 已验证条件。

依赖锁、源码补丁、日志和审计结果的文件摘要见 [SHA256SUMS](SHA256SUMS)。真实 CUDA/vLLM/FSDP 更新和 GPU checkpoint 尚待验证。
