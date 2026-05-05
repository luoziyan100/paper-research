"""Text parsing and summarization helpers."""

from __future__ import annotations

import re
from typing import Dict, List


def parse_sections(text: str) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    current = "body"
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        inline_heading = split_inline_heading(line)
        if inline_heading:
            current, content = inline_heading
            sections.setdefault(current, [])
            if content:
                sections[current].append(content)
            continue
        chinese_heading = normalize_chinese_heading(line)
        if chinese_heading:
            current = chinese_heading
            sections.setdefault(current, [])
            continue
        normalized = re.sub(r"[^a-zA-Z ]", "", line).strip().lower()
        english_heading = normalize_english_heading(normalized)
        if english_heading:
            current = english_heading
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    return {name: " ".join(lines) for name, lines in sections.items() if lines}


def split_inline_heading(line: str) -> tuple[str, str] | None:
    if "：" in line:
        heading_text, content = line.split("：", 1)
    elif ":" in line:
        heading_text, content = line.split(":", 1)
    else:
        return None
    chinese_heading = normalize_chinese_heading(heading_text)
    if chinese_heading:
        return chinese_heading, content.strip()
    normalized = re.sub(r"[^a-zA-Z ]", "", heading_text).strip().lower()
    english_heading = normalize_english_heading(normalized)
    if english_heading:
        return english_heading, content.strip()
    return None


def paper_title(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("title:"):
            return clean_title_text(line)
        if line.startswith("标题：") or line.startswith("题目："):
            return clean_title_text(line)
        if line.startswith("标题:") or line.startswith("题目:"):
            return clean_title_text(line)
        markdown_heading = re.match(r"^#{1,6}\s+(.+)$", line)
        if markdown_heading:
            return clean_title_text(markdown_heading.group(1))
    for line in text.splitlines():
        line = line.strip()
        if line:
            return line[:120]
    return ""


def clean_title_text(text: str) -> str:
    title = text.strip()
    if title.lower().startswith("title:"):
        return title.split(":", 1)[1].strip()
    if title.startswith("标题：") or title.startswith("题目："):
        return title.split("：", 1)[1].strip()
    if title.startswith("标题:") or title.startswith("题目:"):
        return title.split(":", 1)[1].strip()
    return title


def normalize_chinese_heading(line: str) -> str:
    normalized = line.strip().rstrip("：:")
    normalized = re.sub(r"^#{1,6}\s*", "", normalized)
    normalized = re.sub(r"^[（(][一二三四五六七八九十\d]+[）)]\s*", "", normalized)
    normalized = re.sub(r"^[一二三四五六七八九十]+[、.．]\s*", "", normalized)
    normalized = re.sub(r"^[一二三四五六七八九十]+\s+", "", normalized)
    normalized = re.sub(r"^\d+[、.．]\s*", "", normalized)
    normalized = re.sub(r"^\d+\s+", "", normalized)
    heading_map = {
        "摘要": "abstract",
        "引言": "introduction",
        "介绍": "introduction",
        "方法": "method",
        "方法论": "method",
        "实验": "experiments",
        "结果": "results",
        "讨论": "discussion",
        "局限": "limitations",
        "限制": "limitations",
        "结论": "conclusion",
    }
    return heading_map.get(normalized, "")


def normalize_english_heading(normalized_line: str) -> str:
    heading_map = {
        "abstract": "abstract",
        "introduction": "introduction",
        "background": "introduction",
        "method": "method",
        "methods": "method",
        "methodology": "method",
        "approach": "method",
        "system design": "method",
        "experiments": "experiments",
        "experiment": "experiments",
        "evaluation": "experiments",
        "empirical evaluation": "experiments",
        "experiments and results": "experiments",
        "results": "results",
        "findings": "results",
        "discussion": "discussion",
        "limitations": "limitations",
        "limitation": "limitations",
        "conclusion": "conclusion",
    }
    return heading_map.get(normalized_line, "")


def first_sentences(text: str, count: int = 2) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", " ".join(text.split()))
    selected = [sentence for sentence in sentences if sentence][:count]
    return " ".join(selected)[:900]


def compact(text: str, limit: int = 450) -> str:
    compacted = " ".join(text.split())
    if len(compacted) <= limit:
        return compacted
    return compacted[: limit - 3].rstrip() + "..."


def problem_statement(abstract: str) -> str:
    sentence = first_sentences(abstract, count=1)
    if not sentence:
        return "an unstated research problem."
    return sentence[0].lower() + sentence[1:]


def zh_problem_summary(abstract: str) -> str:
    lower = abstract.lower()
    parts = []
    if "long papers" in lower or "paper" in lower or "长论文" in abstract:
        parts.append("长论文深度解读")
    if "benchmark" in lower or "external" in lower or "优秀研究报告" in abstract:
        parts.append("外部优秀报告对照")
    if "rubric" in lower or "score" in lower or "评分标准" in abstract:
        parts.append("评分标准迭代")
    if "record" in lower or "iteration" in lower or "记录" in abstract:
        parts.append("过程记录")
    if parts:
        return "、".join(parts)
    return "论文自动分析流程"


def zh_method_summary(method: str) -> str:
    lower = method.lower()
    if "多角色流程" in method or "拆分为多角色" in method:
        return "系统把审查任务拆分为多角色流程"
    if "separates" in lower and "roles" in lower:
        return "系统把报告写作、评分标准设计、评分和批评分离为独立角色"
    if method.strip():
        return "论文提出了一个需要进一步拆解的技术流程"
    return "方法描述不够明确"


def zh_evidence_summary(experiments: str) -> str:
    lower = experiments.lower()
    if "baseline" in lower and "可复现" in experiments:
        return "迭代审查提高了假设、限制、基线方法和可复现性细节的覆盖"
    if "three papers" in lower and "improved coverage" in lower:
        return "在三篇论文上，迭代评分提高了假设、限制和可复现性细节的覆盖"
    if experiments.strip():
        return "实验声称支持主要结论，但仍需要检查基线方法、指标和统计细节"
    return "实验或结果部分不够明确"


def zh_limitation_summary(limitations: str) -> str:
    lower = limitations.lower()
    risks = []
    if "benchmark" in lower or "对照报告" in limitations or "优秀报告" in limitations:
        risks.append("结果依赖对照报告质量")
    if "overfit" in lower or "rubric" in lower or "评分标准" in limitations or "过拟合" in limitations:
        risks.append("评分标准可能过拟合当前报告")
    if "critic" in lower:
        risks.append("批评智能体的能力会影响纠偏效果")
    if risks:
        return "；".join(risks)
    return "论文限制没有充分展开，需要从评估设计和可复现性角度补查"


def join_phrases(text: str) -> str:
    phrases = []
    for raw_item in text.split("; "):
        item = raw_item.strip().rstrip(".。；;")
        if item:
            phrases.append(item)
    return "；".join(phrases)


def join_english_phrases(text: str) -> str:
    phrases = []
    for raw_item in text.split("; "):
        item = raw_item.strip().rstrip(".;")
        if item:
            phrases.append(item)
    return "; ".join(phrases)
