#!/usr/bin/env python3
"""
ACE 反思循环实现
Agent: Generator → Reflector → Curator
"""

import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Generator:
    """生成回答"""
    def generate(self, query: str, context: dict) -> dict:
        logger.info(f"Generator: generating answer for '{query}'")
        return {
            "content": f"基于 {context.get('sources', [])} 生成的回答",
            "sources": context.get("sources", []),
            "confidence": 0.85
        }

class Reflector:
    """审查回答"""
    def review(self, output: dict, evidence: list) -> dict:
        logger.info("Reflector: reviewing output")
        issues = []

        # 验证证据链
        for source in output.get("sources", []):
            if source not in evidence:
                issues.append({
                    "type": "citation",
                    "severity": "high",
                    "description": f"证据 {source} 未找到"
                })

        # 验证置信度
        if output.get("confidence", 0) < 0.7:
            issues.append({
                "type": "confidence",
                "severity": "medium",
                "description": "置信度低于阈值"
            })

        return {
            "status": "approved" if not issues else "needs_revision",
            "issues": issues,
            "confidence": output.get("confidence", 0)
        }

class Curator:
    """最终决策"""
    def decide(self, output: dict, review: dict) -> dict:
        logger.info("Curator: making final decision")

        if review["status"] == "approved":
            decision = "approve"
        elif review["status"] == "needs_revision" and review["confidence"] > 0.6:
            decision = "revise"
        else:
            decision = "reject"

        return {
            "decision": decision,
            "reason": review.get("issues", []),
            "timestamp": datetime.now().isoformat()
        }

class ACEReview:
    """ACE 反思循环主类"""
    def __init__(self):
        self.generator = Generator()
        self.reflector = Reflector()
        self.curator = Curator()

    def run(self, query: str, context: dict) -> dict:
        logger.info(f"ACE Review: processing '{query}'")

        # Stage 1: Generator
        output = self.generator.generate(query, context)

        # Stage 2: Reflector
        evidence = context.get("evidence", [])
        review = self.reflector.review(output, evidence)

        # Stage 3: Curator
        decision = self.curator.decide(output, review)

        # 记录 ACE 日志
        self._log_ace(query, output, review, decision)

        return {
            "output": output,
            "review": review,
            "decision": decision
        }

    def _log_ace(self, query: str, output: dict, review: dict, decision: dict):
        log_dir = Path(".memory/ace")
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{datetime.now().strftime('%Y%m%d')}-{hash(query) & 0xFFFFFFFF:08x}.md"

        content = f"""---
id: {hash(query) & 0xFFFFFFFF:08x}
date: {datetime.now().isoformat()}
stage: complete
status: {decision['decision']}
---

# ACE 反思记录

## 查询

{query}

## Generator 输出

```json
{json.dumps(output, ensure_ascii=False, indent=2)}
```

## Reflector 审查

```json
{json.dumps(review, ensure_ascii=False, indent=2)}
```

## Curator 决策

```json
{json.dumps(decision, ensure_ascii=False, indent=2)}
```
"""

        log_file.write_text(content, encoding="utf-8")
        logger.info(f"ACE log saved: {log_file}")

def main():
    ace = ACEReview()

    # 测试
    result = ace.run(
        "测试查询",
        {
            "sources": ["raw/test.md"],
            "evidence": ["raw/test.md"]
        }
    )

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()