"""
Assignment 2 evaluator for the Travel Planner Agent.

Usage:
1. Run your agent for the 10 prompts in eval_dataset.json.
2. Create actual_responses.json with this shape:
   {
     "TC01": {"response": "...", "tools_used": ["recommend_places", "estimate_budget"]},
     ...
   }
3. Run:
      python evaluator.py
   This creates evaluation_results.json.

Bonus:
   Set GEMINI_API_KEY in .env and run:
      python evaluator.py --llm-judge
   The Gemini judge scores correctness, relevance, completeness and tool usage
   on a 0-1 scale and gives a reason.
"""

import argparse
import json
import os
from pathlib import Path

DATASET = Path(__file__).with_name("eval_dataset.json")
RESPONSES = Path(__file__).with_name("actual_responses.json")
RESULTS = Path(__file__).with_name("evaluation_results.json")

BLOCKED_MESSAGE = "Sorry, I can only help with travel planning."

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def contains_any(text, words):
    t = text.lower()
    return any(w.lower() in t for w in words)

def heuristic_score(case, response, tools):
    """Conservative deterministic scoring when LLM-as-a-Judge is not used."""
    cid = case["id"]
    text = response.strip()
    lower = text.lower()
    scores = {"correctness": 0.0, "relevance": 0.0,
              "completeness": 0.0, "tool_usage": 0.0}
    reasons = []

    if not text:
        return scores, "No actual response was supplied."

    # Out-of-scope request: should be blocked locally.
    if cid == "TC10":
        blocked = "only help with travel" in lower or "travel planning" in lower
        scores["correctness"] = 1.0 if blocked else 0.0
        scores["relevance"] = 1.0 if blocked else 0.0
        scores["completeness"] = 1.0 if blocked else 0.0
        scores["tool_usage"] = 1.0 if not tools else 0.0
        reasons.append("Out-of-scope request should be rejected locally.")
        return scores, " ".join(reasons)

    # Missing destination/budget and invalid values.
    if cid == "TC04":
        asks_destination = contains_any(lower, ["destination", "where", "which city", "which place"])
        scores["correctness"] = 1.0 if asks_destination else 0.0
        scores["relevance"] = 1.0 if asks_destination else 0.5
        scores["completeness"] = 1.0 if asks_destination else 0.0
        scores["tool_usage"] = 1.0 if not tools else 0.0
        return scores, "Destination is missing and should be requested."

    if cid == "TC05":
        asks_budget = "budget" in lower and contains_any(lower, ["provide", "tell", "need", "without", "missing", "how much"])
        scores["correctness"] = 1.0 if asks_budget else 0.5
        scores["relevance"] = 1.0 if "jaipur" in lower else 0.5
        scores["completeness"] = 1.0 if asks_budget else 0.5
        scores["tool_usage"] = 1.0 if "estimate_budget" not in tools else 0.5
        return scores, "Budget is missing; the agent should request it or clearly qualify an approximate estimate."

    if cid == "TC06":
        invalid = contains_any(lower, ["0 day", "invalid", "positive number", "at least 1", "cannot"])
        scores["correctness"] = 1.0 if invalid else 0.0
        scores["relevance"] = 1.0 if invalid else 0.5
        scores["completeness"] = 1.0 if invalid else 0.0
        scores["tool_usage"] = 1.0 if not tools else 0.0
        return scores, "Zero-day duration should be rejected or clarified."

    if cid == "TC07":
        invalid = contains_any(lower, ["negative", "invalid", "positive", "cannot", "greater than"])
        scores["correctness"] = 1.0 if invalid else 0.0
        scores["relevance"] = 1.0 if invalid else 0.5
        scores["completeness"] = 1.0 if invalid else 0.0
        scores["tool_usage"] = 1.0 if not tools else 0.0
        return scores, "Negative budget should be rejected or clarified."

    # Normal travel cases.
    destination = {
        "TC01": "jaipur", "TC02": "delhi", "TC03": "jaipur",
        "TC08": "jaipur", "TC09": "jaipur"
    }.get(cid)
    if destination:
        scores["correctness"] = 1.0 if destination in lower else 0.0
        scores["relevance"] = 1.0 if destination in lower else 0.5

    if cid in {"TC01", "TC02", "TC03"}:
        duration = {"TC01": "3", "TC02": "5", "TC03": "3"}[cid]
        scores["correctness"] = min(scores["correctness"], 1.0 if duration in lower else 0.5)
        budget_present = "₹" in text or "rs" in lower or "inr" in lower
        scores["completeness"] = 1.0 if budget_present else 0.5
        scores["tool_usage"] = 1.0 if "estimate_budget" in tools else 0.0
        if cid == "TC01":
            history = contains_any(lower, ["amer fort", "city palace", "jantar mantar", "hawa mahal"])
            food = contains_any(lower, ["johari bazaar", "mi road", "masala chowk", "food"])
            scores["completeness"] = (scores["completeness"] + float(history) + float(food)) / 3
        else:
            scores["completeness"] = min(scores["completeness"], 1.0 if "day" in lower else 0.5)

    elif cid == "TC08":
        history = contains_any(lower, ["amer fort", "city palace", "jantar mantar", "hawa mahal", "jaigarh", "nahargarh"])
        scores["completeness"] = 1.0 if history else 0.0
        scores["tool_usage"] = 1.0 if "recommend_places" in tools else 0.0

    elif cid == "TC09":
        food = contains_any(lower, ["johari bazaar", "mi road", "masala chowk", "local food"])
        scores["completeness"] = 1.0 if food else 0.0
        scores["tool_usage"] = 1.0 if "recommend_places" in tools else 0.0

    if cid in {"TC01", "TC02", "TC03"} and "recommend_places" in tools:
        scores["tool_usage"] = 1.0
    elif cid in {"TC01", "TC02", "TC03"}:
        scores["tool_usage"] = max(scores["tool_usage"], 0.0)

    return scores, "Deterministic rubric score. Use --llm-judge for semantic evaluation."

def llm_judge(case, response, tools):
    try:
        from google import genai
    except ImportError:
        raise SystemExit("google-genai is not installed. Install/use your existing google-adk environment.")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise SystemExit("GEMINI_API_KEY is not set. Keep it in .env; do not commit .env.")

    client = genai.Client(api_key=api_key)
    prompt = f"""
You are an evaluator for a Travel Planner Agent.

Test case: {case['id']}
User input: {case['input']}
Expected behavior:
{json.dumps(case['expected_behavior'], indent=2, ensure_ascii=False)}

Actual agent response:
{response}

Tools reported as used:
{json.dumps(tools)}

Score each metric from 0 to 1:
- correctness
- relevance
- completeness
- tool_usage

For out-of-scope or invalid cases, correct behavior may be a refusal/clarification and no tool call.
For tool_usage, give 1 only if the reported tools match what the request requires.
Return ONLY valid JSON:
{{
  "correctness": 0.0,
  "relevance": 0.0,
  "completeness": 0.0,
  "tool_usage": 0.0,
  "reason": "brief explanation"
}}
"""
    result = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )
    raw = result.text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(raw)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--llm-judge", action="store_true")
    args = parser.parse_args()

    dataset = load_json(DATASET)
    if not RESPONSES.exists():
        print("actual_responses.json is missing.")
        print("Create it using the format described at the top of evaluator.py.")
        return

    responses = load_json(RESPONSES)
    results = []
    totals = {"correctness": 0.0, "relevance": 0.0,
              "completeness": 0.0, "tool_usage": 0.0}

    for case in dataset["eval_cases"]:
        item = responses.get(case["id"], {})
        response = item.get("response", "")
        tools = item.get("tools_used", [])

        if args.llm_judge:
            scores = llm_judge(case, response, tools)
            reason = scores.pop("reason", "")
        else:
            scores, reason = heuristic_score(case, response, tools)

        overall = sum(scores.values()) / 4
        for key in totals:
            totals[key] += scores[key]

        results.append({
            "test_case": case["id"],
            "input": case["input"],
            "actual_response": response,
            "tools_used": tools,
            **scores,
            "overall_score": round(overall, 4),
            "overall_percentage": round(overall * 100, 2),
            "reason": reason
        })

    n = len(results)
    averages = {k: round(v / n, 4) for k, v in totals.items()}
    overall = sum(averages.values()) / 4

    output = {
        "summary": {
            "test_cases": n,
            "average_correctness": averages["correctness"],
            "average_relevance": averages["relevance"],
            "average_completeness": averages["completeness"],
            "average_tool_usage": averages["tool_usage"],
            "overall_score": round(overall, 4),
            "overall_percentage": round(overall * 100, 2)
        },
        "results": results
    }

    with open(RESULTS, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(json.dumps(output["summary"], indent=2))
    print(f"\nSaved: {RESULTS}")

if __name__ == "__main__":
    main()
