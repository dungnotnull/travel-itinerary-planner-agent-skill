# PROJECT-detail.md — Personalized Travel Itinerary Planner (Idea 66)

## Executive Summary
A harness that builds a route-optimized, budget-fit travel itinerary from a traveler's preferences and constraints, scores it on feasibility, pacing, cost efficiency, and experience match, and emits an improved day-by-day plan.

## Problem Statement
DIY itineraries waste time backtracking, overschedule, and exceed budgets. This skill applies routing and budgeting logic for realistic, high-value plans.

## Target Users & Use Cases
- **Solo traveler:** "5 days in Kyoto on $1,000" → optimized day plan.
- **Family:** "Kid-friendly Rome, 4 days" → paced, low-fatigue route.
- **Foodie:** "Bangkok food trip" → interest-weighted itinerary.

## Harness Architecture
```
/travel-itinerary-planner
  → sub-profile-intake      (destination, budget, interests)  [gate: dates + budget set]
  → sub-framework-selector  (routing + budgeting)             [gate: ≥1 named method]
  → [main] research         (prices/hours/conditions)         [gate: facts dated]
  → sub-scoring-engine      (feasibility/pacing/cost/exp)     [gate: each dim evidence]
  → sub-improvement-roadmap (day-by-day + alternatives)       [gate: route-optimized + budget-fit]
  → [main] synthesize
```

## Full Sub-Skill Catalog
| Sub-skill | Purpose | Inputs | Outputs | Tools | Gate |
|-----------|---------|--------|---------|-------|------|
| sub-profile-intake | Context | destination, budget, interests | profile | Read | Dates + budget set |
| sub-framework-selector | Pick method | trip type | method set | Read, WebSearch | ≥1 named method |
| sub-scoring-engine | Score itinerary | draft plan | dim scores | Read | Each dim evidence |
| sub-improvement-roadmap | Build plan | scores | day-by-day plan | Write | Route-optimized + budget-fit |

## Skill File Format Specification
Per Claude skill standard; see skills/main.md.

## E2E Execution Flow
1. Intake: destination, dates, budget, party composition, interests, mobility/dietary constraints, pace preference. 2. Selector picks routing (geographic clustering to minimize backtracking) + budget allocation. 3. Research current prices, opening hours, seasonal/weather, closures. 4. Score: feasibility (time/transit realism), pacing (fatigue/buffer), cost efficiency (vs budget), experience match (interest weighting). 5. Roadmap: day-by-day plan clustered by area, with budget breakdown, rain-day alternatives, and booking notes. 6. Render.
Error handling: budget infeasible for destination/dates → flag + rescope; offline → use brain + flag (prices may be stale).

## SECOND-KNOWLEDGE-BRAIN Integration
Sources: tourism boards, transit data, traveler-behavior research, seasonal data. Weekly append.

## Supporting Tools Spec
`knowledge_updater.py`: queries on destination/travel trends & advisories; weekly cron; dedupe by hash.

## Quality Gates
- Itinerary geographically clustered (minimal backtracking) and within budget.
- Each dimension cites evidence (transit time, price, hours).
- Buffer/rest time included; price facts dated; offline flagged.

## Test Scenarios (summary)
1. Budget city trip. 2. Family low-fatigue pace. 3. Interest-weighted (food). 4. Infeasible budget (rescope). 5. Rainy-day alternatives. (Full set in tests/.)

## Key Design Decisions
1. Geographic clustering to cut backtracking. 2. Budget allocation explicit. 3. Buffer time mandatory. 4. Prices dated + flagged volatile. 5. Interest-weighted experience scoring.
