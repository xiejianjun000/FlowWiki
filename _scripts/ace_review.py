#!/usr/bin/env python3
"""
ACE 反思循环 + 知识缺口学习
Generator → Reflector → Curator
    ↓           ↓           ↓
  生成回答   检测缺口/幻觉   决策：存/学/拒

新增: 知识缺口自动补全 — 当 KB 无法回答时，搜索外部源并生成学习卡片
"""
import json, logging, os, re, urllib.request
import os, sys
from datetime import datetime
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
from _scripts.ops_log import ops_log

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MEMORY_DIR = PROJECT_ROOT / ".memory" / "ace"
GAP_DIR = PROJECT_ROOT / ".memory" / "gaps"

# ── Knowledge Gap Detection ──
GAP_SIGNALS = [
    "知识库未覆盖", "暂无相关", "无法确定", "需要补充", "未收录",
    "not found in knowledge base", "insufficient information", "cannot determine",
    "缺乏", "无相关资料", "超出范围", "unknowledgeable",
]

def detect_gaps(content: str, sources: list) -> list[dict]:
    """检测知识库回答中的缺口信号"""
    gaps = []
    content_lower = content.lower()

    # Signal detection
    for signal in GAP_SIGNALS:
        if signal.lower() in content_lower:
            gaps.append({
                "type": "knowledge_gap",
                "signal": signal,
                "severity": "medium"
            })

    # Source deficiency
    if not sources or len(sources) < 2:
        gaps.append({
            "type": "source_deficiency",
            "detail": f"仅 {len(sources)} 个源可用",
            "severity": "high" if not sources else "medium"
        })

    # External reference without KB support
    external_pattern = re.compile(r'《([^》]+)》|"([^"]+)"')
    for m in external_pattern.finditer(content):
        ref = m.group(1) or m.group(2)
        if len(ref) > 4 and ref not in str(sources):
            gaps.append({
                "type": "external_reference",
                "reference": ref,
                "severity": "low"
            })

    return gaps

# ── ACE Agents ──

class Generator:
    """生成回答 — 基于 knowledge base 或标记缺口"""

    def generate(self, query: str, kb_pages: dict, use_llm: bool = True) -> dict:
        logger.info(f"Generator: processing '{query[:50]}...'")

        if not kb_pages and use_llm:
            # KB has nothing — mark as gap immediately
            return {
                "content": f"知识库当前未覆盖此问题。建议补充相关原始资料。\n\n"
                          f"问题: {query}\n\n缺失领域: 待分析",
                "sources": [],
                "confidence": 0.1,
                "knowledge_gaps": [{
                    "query": query,
                    "missing_domain": "未识别",
                    "suggested_sources": []
                }]
            }

        if not use_llm:
            return {
                "content": f"基于 {list(kb_pages.keys())[:5]} 生成回答",
                "sources": list(kb_pages.keys())[:5],
                "confidence": 0.6
            }

        # LLM-powered generation
        api_key = os.environ.get("DEEPSEEK_API_KEY", "")
        if not api_key:
            return {"content": "LLM 不可用", "sources": [], "confidence": 0}

        pages_text = "\n".join(f"--- {k} ---\n{v[:800]}" for k, v in list(kb_pages.items())[:15])

        prompt = f"""你是 FlowWiki Generator。基于知识库内容回答问题。

## 知识库内容（执法督察评查领域）
{pages_text or '(知识库为空)'}

## 用户问题
{query}

## 输出 JSON
{{
  "content": "基于知识库的回答（如果知识库完全无法覆盖才标记'知识库未覆盖'）",
  "sources": ["引用的知识库页面名称"],
  "confidence": 0.0-1.0,
  "knowledge_gaps": []
}}

注意:
- 优先用知识库内容回答问题，即使不是直达答案，也要综合推理
- confidence 评估你回答的可信度：>0.7=知识库充分覆盖, 0.4-0.7=能部分回答, <0.3=完全无法回答
- 只有完全超出执法评查领域的问题才标记 knowledge_gaps
- 不要对知识库已有内容的问题标记为缺口"""

        try:
            payload = json.dumps({
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是 FlowWiki Generator。输出纯 JSON。"},
                    {"role": "user", "content": prompt},
                ],
                "temperature": 0.3, "max_tokens": 1500,
            }).encode()

            req = urllib.request.Request("https://api.deepseek.com/v1/chat/completions",
                data=payload,
                headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"})

            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read())
                content = result["choices"][0]["message"]["content"].strip()
                if content.startswith("```"):
                    content = "\n".join(content.split("\n")[1:])
                    if content.rstrip().endswith("```"):
                        content = content[:content.rfind("```")].strip()
                js = content.find("{")
                je = content.rfind("}") + 1
                return json.loads(content[js:je]) if js >= 0 else {"content": content, "sources": [], "confidence": 0.5}
        except Exception as e:
            return {"content": f"生成失败: {e}", "sources": [], "confidence": 0}


class Reflector:
    """审查回答 — 检测缺口、幻觉、证据链断裂"""

    def review(self, output: dict, kb_sources: list) -> dict:
        logger.info("Reflector: reviewing output")

        issues = []
        content = output.get("content", "")
        sources = output.get("sources", [])
        confidence = output.get("confidence", 0.5)

        # 1. Check explicit knowledge gaps from Generator
        gaps = output.get("knowledge_gaps", [])

        # 2. Auto-detect gap signals
        auto_gaps = detect_gaps(content, sources)
        gaps.extend(auto_gaps)

        # 3. Validate sources
        for src in sources:
            if src not in kb_sources:
                issues.append({
                    "type": "citation",
                    "severity": "high",
                    "description": f"引用的源 '{src}' 不在知识库中"
                })

        # 4. Low confidence check
        if confidence < 0.3:
            issues.append({
                "type": "low_confidence",
                "severity": "high" if not gaps else "medium",
                "description": f"置信度 {confidence} 低于阈值 0.3"
            })

        # 5. Determine status
        if gaps and confidence < 0.3:
            status = "knowledge_gap"
        elif issues:
            status = "needs_revision"
        else:
            status = "approved"

        return {
            "status": status,
            "issues": issues,
            "knowledge_gaps": gaps,
            "confidence": confidence,
            "kb_source_count": len(kb_sources),
        }


class Curator:
    """决策：存/wiki / 标缺口 / 拒绝"""

    def decide(self, output: dict, review: dict) -> dict:
        logger.info("Curator: making decision")

        status = review["status"]
        gaps = review.get("knowledge_gaps", [])

        if status == "knowledge_gap":
            decision = "learn"
            reason = f"检测到 {len(gaps)} 个知识缺口，需要外部学习"
        elif status == "needs_revision":
            decision = "revise"
            reason = str(review.get("issues", []))[:200]
        elif status == "approved":
            decision = "store"
            reason = "审查通过，可存入 wiki"
        else:
            decision = "reject"
            reason = "未通过审查"

        return {
            "decision": decision,
            "reason": reason,
            "knowledge_gaps": gaps,
            "timestamp": datetime.now().isoformat(),
        }


class GapLearner:
    """知识缺口学习器 — 搜索外部源，生成学习卡片"""

    def learn(self, gaps: list[dict], query: str) -> list[dict]:
        """For each gap, attempt to find relevant external knowledge."""
        cards = []
        GAP_DIR.mkdir(parents=True, exist_ok=True)

        for gap in gaps[:3]:
            if isinstance(gap, str):
                gap = {"missing_domain": gap, "suggested_sources": []}
            domain = gap.get("missing_domain", gap.get("signal", "未识别领域"))
            suggested = gap.get("suggested_sources", [])

            card = {
                "id": f"gap-{datetime.now().strftime('%Y%m%d-%H%M%S')}-{hash(str(gap)) & 0xFFF:03x}",
                "timestamp": datetime.now().isoformat(),
                "status": "open",
                "query": query,
                "missing_domain": domain,
                "suggested_sources": suggested,
                "action": "human_review" if not suggested else "auto_ingest_candidate",
                "notes": f"知识库缺失: {domain}。建议补充 {', '.join(suggested[:3])} 到 raw/。"
            }

            # Save gap card
            card_path = GAP_DIR / f"{card['id']}.json"
            json.dump(card, open(card_path, "w"), ensure_ascii=False, indent=2)
            cards.append(card)
            logger.info(f"Gap card created: {card_path}")

        return cards


# ── ACE 主循环 ──

class ACEReview:
    """ACE 反思循环 — 增强版，含知识缺口学习"""

    def __init__(self):
        self.generator = Generator()
        self.reflector = Reflector()
        self.curator = Curator()
        self.learner = GapLearner()

    def run(self, query: str, kb_pages: dict, kb_source_list: list = None) -> dict:
        logger.info(f"ACE: processing '{query[:60]}...'")
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)

        # Stage 1: Generate
        output = self.generator.generate(query, kb_pages)

        # Stage 2: Reflect
        review = self.reflector.review(output, kb_source_list or list(kb_pages.keys()))

        # Stage 3: Curate
        decision = self.curator.decide(output, review)

        # Stage 4: Learn (if gaps detected)
        learning_cards = []
        if decision["decision"] == "learn":
            learning_cards = self.learner.learn(
                decision.get("knowledge_gaps", []), query
            )

        # Stage 5: Log
        self._log_ace(query, output, review, decision, learning_cards)

        # Stage 6: Ops log
        ops_log(
            "query" if decision["decision"] == "store" else decision["decision"],
            f"ACE {query[:60]}",
            {"confidence": review["confidence"], "gaps": len(decision.get("knowledge_gaps", []))},
            status="ok" if decision["decision"] in ("store", "revise") else "warn"
        )

        return {
            "output": output,
            "review": review,
            "decision": decision,
            "learning_cards": learning_cards,
        }

    def _log_ace(self, query, output, review, decision, cards):
        log_id = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        log_file = MEMORY_DIR / f"{log_id}.md"

        cards_text = "- 无"
        if cards:
            lines = []
            for c in cards:
                lines.append(f"- {c['id']}: {c['missing_domain']} -> {c['action']}")
            cards_text = "\n".join(lines)

        content = f"""---
id: {log_id}
date: {datetime.now().isoformat()}
decision: {decision['decision']}
gaps: {len(decision.get('knowledge_gaps', []))}
---

# ACE 反思记录

## 查询
{query}

## Generator 输出
```
{output.get('content', '')[:500]}
```

## Reflector 审查
- 状态: {review['status']}
- 置信度: {review['confidence']}
- 问题数: {len(review.get('issues', []))}
- 知识缺口: {len(review.get('knowledge_gaps', []))}

## Curator 决策
- 决策: {decision['decision']}
- 理由: {decision['reason']}

## 学习卡片
{cards_text}
"""
        log_file.write_text(content, encoding="utf-8")
        logger.info(f"ACE log: {log_file}")


# ── 测试 ──

def main():
    ace = ACEReview()

    # Test 1: Normal query (should pass)
    print("=" * 60)
    print("Test 1: 知识库能回答的问题")
    kb = {
        "排污许可": "企业应按排污许可证要求排放污染物，超标排放违反《排污许可管理条例》。",
        "证据链闭环": "证据链闭环要求所有违法事实有相互印证的证据支撑。",
    }
    result = ace.run("企业超标排放PM2.5该如何处罚？", kb, list(kb.keys()))
    print(f"  决策: {result['decision']['decision']}")
    print(f"  审查: {result['review']['status']}")

    # Test 2: Knowledge gap query
    print("\n" + "=" * 60)
    print("Test 2: 知识库无法回答的问题")
    result2 = ace.run(
        "核电站放射性废物处理标准是什么？",
        kb,  # Same KB, no nuclear content
        list(kb.keys())
    )
    print(f"  决策: {result2['decision']['decision']}")
    print(f"  审查: {result2['review']['status']}")
    print(f"  缺口数: {len(result2['decision'].get('knowledge_gaps', []))}")
    print(f"  学习卡片: {len(result2.get('learning_cards', []))}")
    if result2.get("learning_cards"):
        for c in result2["learning_cards"]:
            print(f"    - {c['id']}: {c['action']} ({c['missing_domain']})")


if __name__ == "__main__":
    main()
