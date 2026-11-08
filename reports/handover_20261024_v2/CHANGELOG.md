# CHANGELOG — handover_20261024_v2

## 新增

- 隔离的v2训练入口、统一prompt、V0起点V3/V4配置及lambda0.1/0.2/0.4扫描草稿。配对配置只有感知权重不同；输出目录由运行时权重派生。
- 独立答案/格式/感知回调与不依赖TRL metric转发的逐条JSONL日志、分层监控。保留冻结v4事实分，strict-v5并行输出。
- V1答案目标和V2感知加答案目标视图；无伪造reasoning，原JSONL不改。文本代理token统计和真实VL processor计数入口。
- 严格几何schema v5、691条新旧标签比较、显式空G mask。新schema允许源版本已有的反角；未将格式差异升级为标签错误。
- 语言LoRA模块全名筛选、视觉encoder/merger冻结断言、全部requires_grad参数清单及身份指纹探针。
- 1472题去同图剩余池的只读状态分层；不扩批准范围。
- 固定随机75题盲审包、私有key/manifest、实际缓存提示词与模型/像素证据、采样前后SHA、身份泄漏与数字巧合记录。
- Linux/CUDA候选依赖、Drive/bootstrap Notebook与shell、显存估算、运行前图片SHA检查说明。
- 新视觉诊断：开始即写identity、adapter逐文件SHA、失败/中断状态、token/预算记录；使用新共享输出协议。
- 新增单元/结构测试和真实TRL奖励派发测试；后者不执行train/generate/backward。原README测试保持不变。

## 保留与未验证

- 原训练器、原诊断器、原v4评分、原发布/manifest/SHA/批准/图片/划分均未改；所有新增代码/配置/产物写在本目录。
- 旧感知SFT→稀疏RL以独立工程路径命名，不冒充正式V3/V4；新配置仍只有2步草稿，不是完整正式实验。
- genai-test安装前两次Windows文件锁失败日志保留，后续最终安装/import/pip check与CPU测试留档；未改其他环境。
- 新测试初次收集因缺包初始化文件失败，已补__init__.py；未修改既有测试去凑通过数。盲审构建遇一个非dict缓存成员，增加类型检查后仍按原种子原样重建，不换样。
- 真实VL processor监督token、真实模块映射/前后向/rollout、恢复、CUDA/Colab安装与显存、盲审填写和误杀/误放率全部 **未验证**。
