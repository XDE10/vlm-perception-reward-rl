# Top-up v6：批准范围、事实修剪与训练入口

本版本基于用户明确的累计 API 总硬上限 **$8**，继承原账本与未知费用预留。结果以 `data/topup_v6_20261024/release/manifest.json` 为准；候选池、未通过审核行及 surplus 不随之获得训练批准。dev 使用 `evaluation_approved=true`、`training_approved=false`。

## 准入没有放宽

项目一保持原 `150~1500 Qwen tokens`、完整输出结构、无循环推导、保守 Math-Verify、两条完整轨迹的 AI 过程审核。不能把短于150 tokens一概称为数学错误或简单题。新源题以最短完整正确原轨迹1200~3200 tokens筛选，竞赛来源/源采样非全对仅作优先级；这不构成官方难度标签。

1495题主批次和5题代数补充批次分开保存。全部同标准补齐1500新源题后，六类分布为530/300/300/225/95/50；没有把95道不等式伪称为100道。原生池是候选，只有通过双轨审核的同题交集可训练。

代码 dev 先封存候选，再在无网络、只读、非root、限CPU/内存/进程/时间的 Docker 中运行全部源测试与常量mutant检查，然后送AI。多解构造题不进入此版固定输出dev。失败dev及历史dev不转作训练；新增train从另一份未分配来源抽取。测试通过和AST复杂度都不等于完备正确性或官方难度。

## 项目三：逐条保留，题答冲突仍阻断整题

每条事实都有原图审核证据、可见标签与源索引。文字已给出/可直接推出、无可见点名、内部圆变量、无法区分圆身份、无法解析、无法确认的事实单独mask；只要题答无方向/条件冲突且保留至少一条认证图像独占事实，就可以成为部分感知监督样本。ID742仍隔离。AI认证是工程证据，不是100%真值证明。

原始响应不改写。对严格等于 `type=json_object` 的冗余响应格式字段，仅在有记录的缓存侧车重解析中剥离；仍要求实际stop结束、完整且不重复的事实索引、逐条证据、题答检查与本地标签/圆身份约束。其他字段不作盲目容错。独立抽查发现的题干蕴含遗漏（如ID265的对角线交点、ID1053的弧端点）由确定性文字守卫对所有缓存进一步剔除，其他合格事实保留。

## V4有限范围 Precision / Recall

令 $G^+$ 为认证正确的图像独占事实，$G^-$ 为可由认证常量属性位证明错误的命题，$P$ 为模型 `<perception>` 中经安全解析、语义规范化和去重后的事实集合。例如认证 `Length(A,B)=3` 时，同一属性位预测4可证为FP；预测别的未知线段则mask。仅凭AI说“图上没有某标记”不构成否定事实，缺乏认证反证的负例也会mask。

$$
TP=|P\cap G^+|,\quad FP=|P\cap G^-|,\quad R=TP/|G^+|,\quad P_{\rm scoped}=TP/(TP+FP).
$$

分母为零时该项记0；F1取二者调和平均。$P\setminus(G^+\cup G^-)$ 是未认证范围，mask而不误判为FP。题干已给事实也不计图像独占TP。不同的符号表达式未必在未知变量取值下不等，因此不能当作已证伪常量冲突；相互矛盾的认证属性位双边mask。有限Precision只覆盖认证属性位，不能解释成全图幻觉率。重复事实不重复加分，角顶点/多边形边界角色不乱序，弧长与角度单位不混淆。格式错误或超过128条事实得0，日志记录有限Precision/Recall/F1和被mask预测数量。

GRPO默认为答案奖励权重1、感知F1权重0.2。认证列表/标准答案是私有奖励元数据；模型输入只有题面和图片。不能把部分标注当作完整类别mask、完整图像金标或完整reasoning监督。

## 运行入口

工作目录为 `D:/Users/Mr.Z/Desktop/modern_genai`。迁移至A100/Colab时将配置中绝对路径统一改为实际路径，保持数据与图片SHA一致。GPU环境使用CUDA版torch并核对TRL/transformers/PEFT版本；本地开发的CPU wheel不能用于GPU训练。

```powershell
python -m scripts.train_project1_sft --config data/topup_v6_20261024/training_configs/project1_compact_sft_smoke.json
python -m scripts.train_project2_opd --config data/topup_v6_20261024/training_configs/project2_opd_smoke.json
python -m scripts.train_project3 --config data/topup_v6_20261024/training_configs/project3_fact_sft_smoke.json
python -m scripts.train_project3 --config data/topup_v6_20261024/training_configs/project3_sparse_v4_grpo_smoke.json
```

配置默认仅2步工程smoke。SFT先导出合并权重与文件清单，RL从合并后的SFT基座新增LoRA，以便禁用新RL adapter时得到正确的固定SFT reference；禁止直接禁用已训练SFT adapter退回初始基座。checkpoint保留优化器/调度器/RNG与run identity。OPD两个教师按域分时驻留，接收相同学生token前缀，KL仅在已审计共同词表上重归一化。

本轮完成CPU规则、损失、优化/断点、输入白名单与实际tokenizer检查；未下载或加载GPU模型权重、未运行A100或真实VL processor smoke。上卡还需检查最长样本显存、视觉token对齐、rollout组奖励、教师梯度、保存恢复和固定预算评测，不能据此写入准确率、速度提升或完整视觉金标结论。
