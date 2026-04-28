"""
Eval runner — calls Claude with tool use for each golden set question,
collects answers, scores them, and prints a report.

Uses prompt caching on the system prompt (stable across all questions).
Runs sequentially to avoid rate limits.

Usage:
    python -m eval.runner
    python -m eval.runner --ids ANS-01 DEF-02 REF-01
    python -m eval.runner --type refusal
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import argparse
import json
import time
from datetime import datetime

import anthropic

from eval.golden_set import GOLDEN_SET, QUESTION_TYPE_COUNTS
from eval.tools import TOOL_SCHEMAS, dispatch
from eval.judge import score_question, aggregate, EvalReport, QuestionResult

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are the churn rate assistant for a SaaS company.
You have access to the company's semantic layer through four tools:
- get_metric: calculate churn rate for a given period, window, and segment
- compare_periods: compare churn rate between two periods
- list_definitions: list available metric definition versions
- explain_calculation: explain how the churn rate is calculated including all rules and thresholds

CRITICAL RULES:
1. Always use a tool to retrieve data before answering quantitative questions.
2. Always mention the definition version (currently 1.0) in your answer.
3. If the data cannot honestly answer the question (forecast, prediction, data outside the available range 2021-2026, PII/personal data requests, subjective quality judgements without benchmarks), you MUST refuse clearly and explain why.
4. Never invent numbers. Never extrapolate. If you are uncertain, say so.
5. When you refuse, be specific about WHY the data cannot answer the question.
6. False confidence — giving a confident wrong answer — is the worst possible outcome.

The canonical churn date is contract_end_date. The primary unit is nMRR (normalized MRR, annual contracts divided by 12). The current definition version is 1.0, approved 2026-04-28."""


def run_question(client: anthropic.Anthropic, question: dict) -> tuple[str, list[str]]:
    """
    Run a single question through Claude with tool use.
    Returns (model_answer, tool_calls_made).
    """
    messages = [{"role": "user", "content": question["question"]}]
    tool_calls_made = []

    # Agentic loop — continue until model stops calling tools
    for _ in range(5):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=TOOL_SCHEMAS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text = " ".join(
                block.text for block in response.content if hasattr(block, "text")
            )
            return text, tool_calls_made

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    tool_calls_made.append(block.name)
                    result_text = dispatch(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                    })
            messages.append({"role": "user", "content": tool_results})
            continue

        # Unexpected stop reason
        break

    return "[eval error: no final text response]", tool_calls_made


def print_report(report: EvalReport, elapsed: float) -> None:
    sep = "=" * 70
    print(f"\n{sep}")
    print("CHURN RATE NL EVAL REPORT")
    print(f"Model: {MODEL} | Definition: v1.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(sep)

    print(f"\n{'METRIC':<35} {'VALUE':>10}  {'TARGET':>10}")
    print("-" * 58)
    print(f"{'Accuracy (answerable questions)':<35} {report.accuracy:>9.1%}  {'> 80%':>10}")
    print(f"{'Refusal accuracy':<35} {report.refusal_accuracy:>9.1%}  {'> 90%':>10}")
    print(f"{'False-confidence rate':<35} {report.false_confidence_rate:>9.1%}  {'< 5%':>10}")
    print(f"{'Overall pass rate':<35} {report.pass_rate:>9.1%}  {'> 80%':>10}")
    print(f"{'Questions evaluated':<35} {report.total:>10}")
    print(f"{'Elapsed':<35} {elapsed:>9.1f}s")

    # Per-type breakdown
    print(f"\n{'BY TYPE':<20} {'PASS':>6} {'FAIL':>6} {'TOTAL':>6}")
    print("-" * 40)
    by_type: dict[str, dict] = {}
    for r in report.results:
        bt = by_type.setdefault(r.question_type, {"pass": 0, "fail": 0})
        if r.verdict == "PASS":
            bt["pass"] += 1
        elif r.verdict == "FAIL":
            bt["fail"] += 1
    for qtype, counts in sorted(by_type.items()):
        total = counts["pass"] + counts["fail"]
        print(f"  {qtype:<18} {counts['pass']:>6} {counts['fail']:>6} {total:>6}")

    # Individual results
    print(f"\n{'ID':<10} {'TYPE':<12} {'VERDICT':<8} {'FC':>4}  QUESTION")
    print("-" * 70)
    for r in report.results:
        fc = "YES" if r.false_confidence_score > 0 else ""
        q_short = r.question[:45] + "..." if len(r.question) > 45 else r.question
        print(f"  {r.question_id:<8} {r.question_type:<12} {r.verdict:<8} {fc:>4}  {q_short}")
        if r.notes:
            print(f"{'':>46} !! {r.notes}")

    # Failures detail
    failures = [r for r in report.results if r.verdict == "FAIL"]
    if failures:
        print(f"\nFAILURES")
        print("-" * 70)
        for r in failures:
            q_safe = r.question.encode("ascii", "replace").decode()
            a_safe = r.model_answer[:300].encode("ascii", "replace").decode()
            print(f"\n[{r.question_id}] {q_safe}")
            print(f"  Answer: {a_safe}...")
            if r.notes:
                print(f"  Notes:  {r.notes}")

    print(f"\n{sep}\n")

    # CI exit code hint
    ok = (
        report.accuracy >= 0.80
        and report.refusal_accuracy >= 0.90
        and report.false_confidence_rate <= 0.05
    )
    status = "PASS" if ok else "FAIL"
    print(f"CI STATUS: {status}")
    return ok


def main():
    parser = argparse.ArgumentParser(description="Run churn rate NL eval harness")
    parser.add_argument("--ids", nargs="*", help="Run only specific question IDs")
    parser.add_argument("--type", help="Run only a specific question type")
    parser.add_argument("--dry-run", action="store_true", help="Print questions without calling API")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        # SDK may auto-detect from other sources (Claude Code, ~/.anthropic)
        try:
            import anthropic as _a
            _a.Anthropic()
        except Exception:
            print("ERROR: ANTHROPIC_API_KEY not set. Export it or use --dry-run.")
            sys.exit(1)

    questions = GOLDEN_SET
    if args.ids:
        questions = [q for q in questions if q["id"] in args.ids]
    if args.type:
        questions = [q for q in questions if q["question_type"] == args.type]

    print(f"Eval harness — {len(questions)} questions")
    print(f"Stratification: {QUESTION_TYPE_COUNTS}")

    if args.dry_run:
        for q in questions:
            print(f"  [{q['id']}] ({q['question_type']}) {q['question']}")
        return

    client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
    results: list[QuestionResult] = []
    start = time.time()

    for i, question in enumerate(questions, 1):
        print(f"[{i}/{len(questions)}] {question['id']} — {question['question'][:60]}...")
        try:
            answer, tool_calls = run_question(client, question)
            result = score_question(question, answer, tool_calls)
            results.append(result)
            verdict_icon = "+" if result.verdict == "PASS" else "x"
            fc_icon = " !! FALSE CONFIDENCE" if result.false_confidence_score > 0 else ""
            print(f"  {verdict_icon} {result.verdict}{fc_icon}")
            # Small delay to respect rate limits
            time.sleep(0.5)
        except Exception as e:
            print(f"  ERROR: {e}")
            results.append(QuestionResult(
                question_id=question["id"],
                question=question["question"],
                question_type=question["question_type"],
                should_refuse=question["should_refuse"],
                model_answer=f"[error: {e}]",
                tool_calls_made=[],
                accuracy_score=0.0,
                refusal_score=0.0 if question["should_refuse"] else None,
                false_confidence_score=0.0,
                verdict="FAIL",
                notes=f"Runner error: {e}",
            ))

    elapsed = time.time() - start
    report = aggregate(results)
    ok = print_report(report, elapsed)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
