HCL Internship Assignment

## How to Run

### Step 1: Install the Required Dependencies

Install Google ADK:

```bash
pip install google-adk
```

### Step 2: Run the Agent

Run the following command:

```bash
adk web
```

Open the ADK Web UI and select the Travel Planner Agent.

---

# Activities

## Day 1 — Create a Travel Planner Agent

- Created a Personal Travel Planner Agent using Google ADK.
- Implemented basic travel planning functionality.
- The agent can understand:
  - Destination
  - Number of days
  - Travel budget
  - User interests
- Added tools for:
  - Recommending places
  - Estimating travel budget
- Generates customized day-wise travel itineraries.

---

## Day 2 — Restrict the Agent to Travel Queries

Added restrictions so that the agent only responds to travel-related queries.

The agent can handle requests related to:

- Travel planning
- Destinations
- Itineraries
- Travel budgets
- Places to visit
- Hotels and accommodation
- Transportation
- Restaurants and food
- Travel activities

Non-travel questions are rejected appropriately.

### Example

```text
User: What is Python?

Agent:
Sorry, I can only help with travel planning. Please ask me something related to planning a trip, destinations, itineraries, travel budgets, places to visit, accommodation, transportation, or travel activities.
```

The travel-domain restriction is implemented before the model is called, allowing unrelated queries to be blocked locally.

---

# Day 3 — Assignment 2: Evaluation

The Travel Planner Agent was evaluated using **10 test cases** covering valid requests, invalid inputs, missing information, budgets, durations, user preferences, and non-travel queries.

## Test Cases

| Test Case | Description |
|---|---|
| TC01 | Valid 3-day Jaipur trip |
| TC02 | Valid 5-day Delhi trip |
| TC03 | Low-budget trip |
| TC04 | Missing destination |
| TC05 | Missing budget |
| TC06 | Invalid number of days |
| TC07 | Negative budget |
| TC08 | Historical-place preference |
| TC09 | Food preference |
| TC10 | Non-travel question |

---

## Evaluation Metrics

Each test case was evaluated using four metrics:

1. **Correctness**
2. **Relevance**
3. **Completeness**
4. **Tool Usage**

Each metric is scored between **0 and 1**.

The overall score is calculated from the average of the evaluation metrics across all test cases.

---

# Evaluation Results

| Metric | Average Score |
|---|---:|
| Correctness | 0.85 |
| Relevance | 0.95 |
| Completeness | 0.85 |
| Tool Usage | 0.70 |
| **Overall Score** | **83.75%** |

### Overall Evaluation Score

**83.75%**

---

# Test Case Results

| Test Case | Score | Result |
|---|---:|---|
| TC01 | 100% | Valid Jaipur trip successfully planned |
| TC02 | 100% | Valid Delhi trip successfully planned |
| TC03 | 100% | Low-budget trip successfully handled |
| TC04 | 100% | Missing destination correctly identified |
| TC05 | 75% | Missing budget should be requested |
| TC06 | 12.5% | 0-day duration should be rejected |
| TC07 | 75% | Negative budget should be rejected |
| TC08 | 100% | Historical preference successfully handled |
| TC09 | 75% | Food preference handled; tool usage needs improvement |
| TC10 | 100% | Non-travel question correctly rejected |

---

# Evaluation Files

```text
Travel_Agent/
│
├── agent.py
├── tools.py
├── eval_dataset.json
├── actual_responses.json
├── evaluator.py
├── evaluation_results.json
├── README.md
└── requirements.txt
```

---

# Evaluation Process

1. Created an evaluation dataset containing 10 test cases.
2. Started the Travel Planner Agent using Google ADK.
3. Tested each test case using the ADK Web UI.
4. Recorded the actual responses from the agent.
5. Recorded the tools used by the agent.
6. Stored the actual results in `actual_responses.json`.
7. Evaluated the responses using four metrics.
8. Calculated individual test-case scores.
9. Calculated the overall evaluation score.
10. Stored the final results in `evaluation_results.json`.

---

# Running the Evaluator

After creating `actual_responses.json`, run:

```bash
python evaluator.py
```

The evaluator generates:

```text
evaluation_results.json
```

The file contains individual test-case scores, metric scores, the overall score, and reasons for the scores.

---

# LLM-as-a-Judge

An optional **LLM-as-a-Judge** evaluation using Gemini is implemented in `evaluator.py`.

Run:

```bash
python evaluator.py --llm-judge
```

The LLM judge evaluates:

- Correctness
- Relevance
- Completeness
- Tool Usage
- Reason for the score

---

# Failed Cases and Observations

### 1. Missing Budget

When the user does not provide a budget, the agent should ask for the budget instead of assuming one.

### 2. Invalid Duration

A duration of `0` days should be rejected. The agent should request a valid positive number of days.

### 3. Negative Budget

A negative budget should be rejected instead of being converted into an alternative budget plan.

### 4. Tool Usage

Tool usage should be consistent with the user's request. The appropriate recommendation and budget tools should be used whenever applicable.

---

# Planned Improvements

Future improvements include:

- Add strict input validation.
- Validate the number of travel days.
- Reject zero or negative durations.
- Reject negative budgets.
- Ask for missing destination information.
- Ask for missing budget information.
- Improve itinerary generation.
- Expand destination-specific recommendations.
- Add more destinations.
- Add accommodation recommendations.
- Add transportation recommendations.
- Improve personalization based on user preferences.
- Improve consistency in tool usage.
- Add more evaluation test cases.

---

# Project Objective

The objective of this project is to build a **Personal Travel Planner Agent using Google ADK** that can:

- Understand travel-related requests.
- Identify the destination.
- Understand trip duration.
- Consider the user's budget.
- Understand user interests.
- Recommend suitable places.
- Estimate travel expenses.
- Generate personalized itineraries.
- Restrict unrelated questions.
- Evaluate its performance using predefined test cases.

---

# Conclusion

The Travel Planner Agent successfully handles most valid travel-planning requests and correctly rejects non-travel queries.

The agent achieved an overall evaluation score of:

## **83.75%**

The evaluation identified areas for improvement, particularly:

- Input validation
- Missing-budget handling
- Invalid-duration handling
- Negative-budget handling
- Consistent tool usage
- Expanded travel recommendations

The project demonstrates the development, restriction, and evaluation of a travel-focused AI agent using **Google ADK**.
