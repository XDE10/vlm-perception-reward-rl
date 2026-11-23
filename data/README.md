# 批准数据包

协议 v3 的 609 条训练行和 82 条验证行随经过批准的数据包提供。通过仓库维护者取得数据包，将包内 `data/` 内容解到仓库 `data/` 下。保留包内相对路径，包括 `portable_release/`、行里引用的图像路径及 `project3_audit/intergps_annotations.jsonl`。路径和 SHA256 用于验证数据身份。Git 检出提供代码、查验清单和小型测试夹具。

```bash
python tools/verify_migration.py --full --data-root data
python -m scripts.training.register_runs --check
```

也可在 Colab 启动器中用 `P3_DATA_ROOT=/path/to/data` 指定独立的数据目录。打包只读取经证据清单绑定的运行数据。公开评测的数据源与版本由代码按清单下载并校验。详细入口见 [协议 v3](../docs/training.md)。

Shuffle-R1 使用独立的 27,436 条训练数据和 256 条内部 dev，接入方式见 [Shuffle-R1 指南](../shuffle_r1/README.md)。
