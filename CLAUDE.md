# CLAUDE.md — Personalized Travel Itinerary Planner Skill (Idea 66)

**Skill name:** `travel-itinerary-planner`
**Tagline:** Budget/preference-optimized itineraries scored for feasibility and experience value.
**Current phase:** Scaffold complete (Phases 0–5).
**Source idea:** 66 — *Build & evaluate personalized travel itineraries by budget, preferences and time, optimizing route and cost, grounded in world-renowned planning/evaluation methods, with improvement recommendations; continuously crawl papers/docs to stay current.*
**Cluster:** `lifestyle-personal`

## Problem This Skill Solves
Travelers over-pack schedules, backtrack geographically, and blow budgets. This skill profiles preferences/constraints, builds a route-optimized, budget-fit itinerary, scores it (feasibility, pacing, cost efficiency, experience match), and emits improvements.

## Harness Flow Summary
1. **Intake** (`sub-profile-intake`) — destination, dates, budget, party, interests, constraints.
2. **Framework selection** (`sub-framework-selector`) — routing & budgeting methods.
3. **Research** (main) — verify current prices/hours/conditions vs SECOND-KNOWLEDGE-BRAIN.md.
4. **Scoring** (`sub-scoring-engine`) — itinerary feasibility/pacing/cost/experience.
5. **Roadmap** (`sub-improvement-roadmap`) — optimized day-by-day plan + alternatives.

## Sub-skills
- `sub-profile-intake.md` · `sub-framework-selector.md` · `sub-scoring-engine.md` · `sub-improvement-roadmap.md`

## Tools Required
WebSearch, WebFetch, Read, Write, Bash.

## Knowledge Sources
Official tourism boards, transit/route data, traveler-behavior research, seasonal/weather data, reputable travel guides.

## Supporting Python Tools
`tools/knowledge_updater.py` — crawl → SECOND-KNOWLEDGE-BRAIN.md.

## Active Development Tasks
- [x] Scaffold deliverables.
- [ ] Add transit-API integrations.

## Reference Docs
PROJECT-detail.md · PROJECT-DEVELOPMENT-PHASE-TRACKING.md · SECOND-KNOWLEDGE-BRAIN.md
