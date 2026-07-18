#!/usr/bin/env python3
"""
FlowWiki 多语言目录映射模块。

约定：
- 仓库中实际目录始终是英文名（raw/ wiki/ 00_首页/ ...），Agent 直接使用
- 人类通过本地化目录入口访问（如 原始资料/ → 指向 raw/）
- 每个本地化目录包含一个 README.md 说明实际路径

映射表:
    raw/          ↔  原始资料/
    wiki/         ↔  知识库/
    00_首页/      ↔  首页/
    .memory/     ↔  .记忆/
    storage/      ↔  存储/
    _scripts/     ↔  脚本/
    _templates/   ↔  模板/
    ops/          ↔  运维/
"""

from pathlib import Path
from typing import Optional

# ── 目录映射表 ──
LOCALE_MAP = {
    "zh": {
        "raw/": "原始资料/",
        "wiki/": "知识库/",
        "00_首页/": "首页/",
        ".memory/": ".记忆/",
        "storage/": "存储/",
        "_scripts/": "脚本/",
        "_templates/": "模板/",
        "ops/": "运维/",
        "docs/": "文档/",
        "spec/": "规格/",
        "openspec/": "变更记录/",
    },
    "en": {
        # English uses the default names (identity mapping)
    },
}

# ── 反向映射（方便查询） ──
def _reverse_map(lang: str) -> dict[str, str]:
    """Build reverse map: language-specific name → canonical English name."""
    rev: dict[str, str] = {}
    for en, local in LOCALE_MAP.get(lang, {}).items():
        rev[local] = en
    return rev


def detect_locale() -> str:
    """
    检测用户地区，返回推荐语言代码。
    优先级：config.toml > 环境变量 > IP 检测 > 默认 'en'
    """
    import os

    # 1) 环境变量
    env_lang = os.environ.get("FLOWWIKI_LANG") or os.environ.get("LANG", "")
    if env_lang.lower().startswith("zh"):
        return "zh"

    # 2) 尝试从 config.toml 读取
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ImportError:
            tomllib = None  # type: ignore[assignment]

    if tomllib:
        for candidate in [Path("config.toml"), Path(".llm-wiki/config.toml")]:
            if candidate.exists():
                try:
                    data = tomllib.loads(candidate.read_text(encoding="utf-8"))
                    lang = data.get("locale", {}).get("lang", "")
                    if lang:
                        return lang
                except Exception:
                    pass

    # 3) IP 归属地检测（外部 API）
    try:
        import urllib.request, json
        req = urllib.request.Request(
            "https://ipapi.co/json/", headers={"User-Agent": "FlowWiki-setup/1.0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
            country = data.get("country_code", "").upper()
            if country == "CN":
                return "zh"
    except Exception:
        pass

    return "en"


def locale_name(english_path: str, lang: str) -> str:
    """将英文路径转为本地化显示名。"""
    mapping = LOCALE_MAP.get(lang, {})
    # 去掉尾部斜杠做匹配
    key = english_path.rstrip("/") + "/"
    return mapping.get(key, english_path)


def english_name(local_path: str, lang: str) -> str:
    """将本地化路径转回英文路径。"""
    rev = _reverse_map(lang)
    key = local_path.rstrip("/") + "/"
    return rev.get(key, local_path)


def generate_locale_dirs(root: Path, lang: str) -> list[str]:
    """
    在项目根目录生成本地化目录入口（只创建 README.md，不创建实际目录结构）。
    返回创建的文件列表。
    """
    if lang == "en":
        return []  # English is the default, nothing to generate

    mapping = LOCALE_MAP.get(lang, {})
    created: list[str] = []

    for en_dir, local_dir in mapping.items():
        local_path = root / local_dir.rstrip("/")
        en_path = root / en_dir.rstrip("/")

        if not en_path.exists():
            continue  # 跳过不存在的英文目录

        local_path.mkdir(parents=True, exist_ok=True)

        readme = local_path / "README.md"
        readme.write_text(
            f"# {local_dir.rstrip('/')}\n\n"
            f"> 此目录为人类阅读入口，实际内容位于 `{en_dir}`。\n"
            f"> AI Agent 直接使用 `{en_dir}` 路径。\n\n"
            f"- 英文路径: [{en_dir}](../{en_dir})\n"
            f"- 如需浏览内容，请打开 `{en_dir}` 目录。\n",
            encoding="utf-8",
        )
        created.append(str(local_path))

    return created


def resolve_path(user_path: str, lang: str, root: Optional[Path] = None) -> Path:
    """
    将用户输入路径（可能是本地化名称）解析为实际文件系统路径。
    例如 resolve_path("原始资料/laws/", "zh") → Path("raw/laws/")
    """
    if root is None:
        root = Path.cwd()  # type: ignore[assignment]
    # 尝试匹配本地化前缀
    rev = _reverse_map(lang)
    for local_prefix, en_prefix in rev.items():
        local_p = local_prefix.rstrip("/") + "/"
        if user_path.startswith(local_p):
            return root / en_prefix.rstrip("/") / user_path[len(local_p):]
    return root / user_path
