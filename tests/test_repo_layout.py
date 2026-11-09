"""结构回归测试：固定 2026-11-08 整理后的仓库布局。

这些断言不测试数据或模型行为，只防止目录/入口在后续改动中悄悄退回平铺状态。
数据完整性仍由 ``tools/verify_migration.py`` 负责。
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
GROUPS = ["common", "data", "training", "reporting", "migration", "colab"]


def test_scripts_has_no_flat_modules():
    flat = sorted(
        path.name
        for path in SCRIPTS.glob("*.py")
        if path.name != "__init__.py"
    )
    assert flat == [], f"scripts/ 下出现平铺脚本: {flat}"
    assert (SCRIPTS / "README.md").is_file()


def test_each_script_group_is_a_package():
    for group in GROUPS:
        directory = SCRIPTS / group
        assert directory.is_dir(), f"缺少 scripts/{group}/"
        assert (directory / "__init__.py").is_file(), f"scripts/{group}/ 缺少 __init__.py"
        assert list(directory.glob("*.py")), f"scripts/{group}/ 没有脚本"


def test_scripts_readme_lists_every_script():
    catalog = (SCRIPTS / "README.md").read_text(encoding="utf-8")
    missing = [
        str(path.relative_to(ROOT))
        for group in GROUPS
        for path in sorted((SCRIPTS / group).glob("*.py"))
        if path.name != "__init__.py" and path.name not in catalog
    ]
    assert missing == [], f"scripts/README.md 未列出: {missing}"


def test_current_docs_and_root_files_exist():
    for relative in [
        "README.md",
        "AGENTS.md",
        "CHANGELOG.md",
        "pyproject.toml",
        ".editorconfig",
        "docs/README.md",
        "docs/repo_layout.md",
        "docs/architecture.md",
        "docs/data.md",
        "docs/training.md",
        "docs/verification.md",
        "configs/README.md",
        "data/README.md",
        "reports/README.md",
        "requirements/README.md",
    ]:
        assert (ROOT / relative).is_file(), f"缺少当前入口/说明文件: {relative}"


def test_pytest_configuration_points_at_tests():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert "[tool.pytest.ini_options]" in pyproject
    assert 'testpaths = ["tests"]' in pyproject
    assert "--strict-markers" in pyproject


def test_configs_use_relative_paths_and_pinned_revision():
    for config_path in sorted((ROOT / "configs").glob("*.json")):
        config = json.loads(config_path.read_text(encoding="utf-8"))
        manifest = ROOT / config["data_manifest"]
        assert not Path(config["data_manifest"]).is_absolute(), config_path
        assert manifest.is_file(), config_path
        assert (manifest.parent / config["data_file"]).is_file(), config_path
        assert not Path(config["tokenizer_path"]).is_absolute(), config_path
        assert (ROOT / config["tokenizer_path"]).is_dir(), config_path
        assert not Path(config["output_dir"]).is_absolute(), config_path
        assert not str(config["output_dir"]).startswith(("/", "\\")), config_path
        assert config.get("model_revision") not in (None, "", "main"), config_path
        # SFT 配置钉 40 位 HF revision；RL 从本地合并权重起跑，用显式身份串。
        if config["model_revision"] != "local-merged-with-weight-manifest":
            assert re.fullmatch(r"[0-9a-f]{40}", config["model_revision"]), config_path
        # model 是 HF id 或相对 runs/ 目录，二者都不能是绝对路径/盘符路径。
        assert not re.match(r"^[A-Za-z]:", str(config["model"])), config_path
