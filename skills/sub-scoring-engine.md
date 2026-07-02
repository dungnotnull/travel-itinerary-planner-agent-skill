---
name: sub-scoring-engine
description: Score a draft itinerary on feasibility, pacing, cost efficiency, and experience match with evidence.
---

## Purpose
Evaluate a draft itinerary using weighted scoring across four dimensions, providing quantitative and qualitative feedback with evidence-backed flags before final optimization.

## Inputs
- **Draft itinerary** from research phase: day-by-day activities with times, costs, locations
- **Trip profile** from `sub-profile-intake`: interests, constraints, pace preference
- **Framework selection** from `sub-framework-selector`: routing method, budget allocation, activity caps
- **Research data**: prices (dated), transit times, opening hours, seasonal conditions

## Process

### Dimension 1: Feasibility Scoring (30% weight)

**Sub-metrics:**
1. Transit time ratio (15%)
2. Opening hours alignment (10%)
3. Buffer adequacy (5%)

```python
def score_feasibility(itinerary: dict, framework: dict) -> dict:
    """Score itinerary feasibility with evidence."""

    scores = {}
    flags = []
    evidence = []

    # 1. Transit Time Ratio
    total_transit_time = 0
    total_active_time = 0

    for day in itinerary["days"]:
        for i, activity in enumerate(day["activities"]):
            if i > 0:
                prev = day["activities"][i-1]
                transit = get_transit_time(prev["location"], activity["location"])
                total_transit_time += transit
            total_active_time += activity["duration"]

    transit_ratio = total_transit_time / (total_transit_time + total_active_time)

    # Score: <20% = 100, 20-30% = 80, 30-40% = 50, >40% = 20
    if transit_ratio < 0.20:
        transit_score = 100
    elif transit_ratio < 0.30:
        transit_score = 80
    elif transit_ratio < 0.40:
        transit_score = 50
    else:
        transit_score = 20
        flags.append({
            "severity": "high",
            "type": "excessive_transit",
            "message": f"Transit time is {transit_ratio*100:.0f}% of total time (should be <30%)",
            "evidence": f"{total_transit_time/60:.0f}h transit vs {total_active_time/60:.0f}h activity"
        })

    scores["transit_ratio"] = {
        "score": transit_score,
        "weight": 0.15,
        "weighted_score": transit_score * 0.15,
        "value": transit_ratio,
        "evidence": f"{total_transit_time/60:.1f}h transit, {total_active_time/60:.1f}h activities"
    }

    # 2. Opening Hours Alignment
    misaligned_activities = 0
    total_activities = 0

    for day in itinerary["days"]:
        for activity in day["activities"]:
            total_activities += 1
            scheduled_time = activity["start_time"]
            if "opens" in activity and "closes" in activity:
                if scheduled_time < activity["opens"] or scheduled_time > activity["closes"]:
                    misaligned_activities += 1
                    flags.append({
                        "severity": "high",
                        "type": "hours_mismatch",
                        "message": f"{activity['name']} scheduled at {scheduled_time} but open {activity['opens']}-{activity['closes']}",
                        "evidence": f"Cannot visit when closed"
                    })

    alignment_rate = 1 - (misaligned_activities / total_activities)
    hours_score = alignment_rate * 100

    scores["hours_alignment"] = {
        "score": hours_score,
        "weight": 0.10,
        "weighted_score": hours_score * 0.10,
        "value": alignment_rate,
        "evidence": f"{total_activities - misaligned_activities}/{total_activities} activities aligned with hours"
    }

    # 3. Buffer Adequacy
    total_buffer_time = 0
    required_buffer = itinerary["days"][0]["date"].__class__.total_days * 60 * 8 * 0.15  # 15% of 8h

    for day in itinerary["days"]:
        for activity in day.get("buffers", []):
            total_buffer_time += activity["duration"]

    buffer_ratio = total_buffer_time / required_buffer if required_buffer > 0 else 0

    if buffer_ratio >= 1.0:
        buffer_score = 100
    elif buffer_ratio >= 0.8:
        buffer_score = 80
    elif buffer_ratio >= 0.5:
        buffer_score = 50
        flags.append({
            "severity": "medium",
            "type": "insufficient_buffer",
            "message": f"Only {buffer_ratio*100:.0f}% of recommended buffer time",
            "evidence": f"{total_buffer_time/60:.1f}h buffer vs {required_buffer/60:.1f}h required"
        })
    else:
        buffer_score = 30
        flags.append({
            "severity": "high",
            "type": "inadequate_buffer",
            "message": f"Severely inadequate buffer: {buffer_ratio*100:.0f}% of recommended",
            "evidence": f"{total_buffer_time/60:.1f}h buffer vs {required_buffer/60:.1f}h required"
        })

    scores["buffer_adequacy"] = {
        "score": buffer_score,
        "weight": 0.05,
        "weighted_score": buffer_score * 0.05,
        "value": buffer_ratio,
        "evidence": f"{total_buffer_time/60:.1f}h buffer ({buffer_ratio*100:.0f}% of required)"
    }

    # Calculate weighted total
    feasibility_score = sum(s["weighted_score"] for s in scores.values())

    return {
        "dimension": "Feasibility",
        "overall_score": feasibility_score,
        "max_score": 30,
        "sub_scores": scores,
        "flags": flags,
        "evidence_summary": f"{total_transit_time/60:.1f}h transit ({transit_ratio*100:.0f}%), {misaligned_activities} hour mismatches, {buffer_ratio*100:.0f}% buffer"
    }
```

### Dimension 2: Pacing & Fatigue Scoring (20% weight)

**Sub-metrics:**
1. Activity count adherence (10%)
2. Rest time adequacy (6%)
3. Jet-lag adjustment (4%)

```python
def score_pacing(itinerary: dict, profile: dict, framework: dict) -> dict:
    """Score pacing and fatigue management."""

    scores = {}
    flags = []
    activity_caps = framework["pacing"]["parameters"]["activity_caps"]

    # 1. Activity Count Adherence
    overpacked_days = 0
    total_days = len(itinerary["days"])

    for i, day in enumerate(itinerary["days"]):
        day_num = i + 1
        activities_count = len(day["activities"])

        # Get cap for this day (jet-lag adjusted)
        if day_num == 1:
            cap = activity_caps["jet_lag_schedule"]["day_1"]
        elif day_num == 2:
            cap = activity_caps["jet_lag_schedule"]["day_2"]
        else:
            cap = activity_caps["recommended_per_day"]

        if activities_count > cap:
            overpacked_days += 1
            flags.append({
                "severity": "medium" if activities_count <= cap * 1.2 else "high",
                "type": "overpacked_day",
                "message": f"Day {day_num}: {activities_count} activities exceeds cap of {cap:.1f}",
                "evidence": f"Reduces pace score, increases fatigue risk"
            })

    adherence_rate = 1 - (overpacked_days / total_days)
    adherence_score = adherence_rate * 100

    scores["activity_adherence"] = {
        "score": adherence_score,
        "weight": 0.10,
        "weighted_score": adherence_score * 0.10,
        "value": adherence_rate,
        "evidence": f"{total_days - overpacked_days}/{total_days} days within activity caps"
    }

    # 2. Rest Time Adequacy
    buffer_req = framework["pacing"]["parameters"]["buffer_requirements"]
    under_rested_days = 0

    for day in itinerary["days"]:
        actual_rest = sum(b.get("duration", 0) for b in day.get("buffers", []))
        min_rest = buffer_req["buffer_minutes_per_day"]

        if actual_rest < min_rest:
            under_rested_days += 1
            flags.append({
                "severity": "medium",
                "type": "insufficient_rest",
                "message": f"Day {day.get('day_number')}: Only {actual_rest}min rest vs {min_rest}min required",
                "evidence": f"Fatigue risk increases without adequate rest"
            })

    rest_adequacy = 1 - (under_rested_days / total_days)
    rest_score = rest_adequacy * 100

    scores["rest_adequacy"] = {
        "score": rest_score,
        "weight": 0.06,
        "weighted_score": rest_score * 0.06,
        "value": rest_adequacy,
        "evidence": f"{total_days - under_rested_days}/{total_days} days with adequate rest"
    }

    # 3. Jet-Lag Adjustment (if applicable)
    trip_has_jet_lag = requires_jet_lag_consideration(profile)
    jet_lag_score = 100

    if trip_has_jet_lag:
        day_1_light = len(itinerary["days"][0]["activities"]) <= activity_caps["jet_lag_schedule"]["day_1"] * 1.2
        day_2_light = len(itinerary["days"][1]["activities"]) <= activity_caps["jet_lag_schedule"]["day_2"] * 1.2

        if not day_1_light or not day_2_light:
            reduction = (0 if day_1_light else 50) + (0 if day_2_light else 50)
            jet_lag_score = 100 - reduction
            flags.append({
                "severity": "medium",
                "type": "no_jet_lag_adjustment",
                "message": f"Days 1-2 not adjusted for jet lag",
                "evidence": f"Fatigue risk higher without lighter first days"
            })

    scores["jet_lag_adjustment"] = {
        "score": jet_lag_score,
        "weight": 0.04,
        "weighted_score": jet_lag_score * 0.04,
        "value": 1.0 if jet_lag_score == 100 else 0.5,
        "evidence": f"Jet lag {'considered' if jet_lag_score == 100 else 'not considered'}"
    }

    pacing_score = sum(s["weighted_score"] for s in scores.values())

    return {
        "dimension": "Pacing & Fatigue",
        "overall_score": pacing_score,
        "max_score": 20,
        "sub_scores": scores,
        "flags": flags,
        "evidence_summary": f"{overpacked_days} overpacked days, {under_rested_days} under-rested"
    }
```

### Dimension 3: Cost Efficiency Scoring (25% weight)

**Sub-metrics:**
1. Budget utilization (10%)
2. Per-day spending balance (10%)
3. Contingency reserve (5%)

```python
def score_cost_efficiency(itinerary: dict, framework: dict, profile: dict) -> dict:
    """Score cost efficiency and budget adherence."""

    scores = {}
    flags = []
    budget = profile["budget"]
    allocation = framework["budget"]["parameters"]["allocation"]

    # Calculate total estimated cost
    estimated_costs = {
        "transport": 0,
        "lodging": 0,
        "food": 0,
        "activities": 0
    }

    for day in itinerary["days"]:
        for activity in day["activities"]:
            cat = activity.get("category", "activities")
            if cat in estimated_costs:
                estimated_costs[cat] += activity.get("estimated_cost", 0)

    total_estimated = sum(estimated_costs.values())
    remaining_budget = budget["converted_to_dest"] - total_estimated

    # 1. Budget Utilization
    utilization_rate = total_estimated / budget["converted_to_dest"]

    if 0.85 <= utilization_rate <= 1.05:
        utilization_score = 100  # Sweet spot
    elif 0.70 <= utilization_rate < 0.85:
        utilization_score = 85  # Under-utilizing
        flags.append({
            "severity": "low",
            "type": "under_budget",
            "message": f"Budget under-utilized at {utilization_rate*100:.0f}%",
            "evidence": f"Could add more experiences within budget"
        })
    elif utilization_rate < 0.70:
        utilization_score = 60
        flags.append({
            "severity": "medium",
            "type": "severely_under_budget",
            "message": f"Only {utilization_rate*100:.0f}% of budget used",
            "evidence": f"Significant room for more activities"
        })
    elif utilization_rate > 1.20:
        utilization_score = 30
        flags.append({
            "severity": "high",
            "type": "budget_overrun",
            "message": f"Budget exceeded by {(utilization_rate-1)*100:.0f}%",
            "evidence": f"Total {total_estimated:.0f} vs budget {budget['converted_to_dest']:.0f}"
        })
    else:
        utilization_score = 100 - abs(1 - utilization_rate) * 100

    scores["budget_utilization"] = {
        "score": utilization_score,
        "weight": 0.10,
        "weighted_score": utilization_score * 0.10,
        "value": utilization_rate,
        "evidence": f"{total_estimated:.0f} / {budget['converted_to_dest']:.0f} ({utilization_rate*100:.0f}%)"
    }

    # 2. Per-Day Spending Balance
    daily_spending = []
    for day in itinerary["days"]:
        day_total = sum(a.get("estimated_cost", 0) for a in day["activities"])
        daily_spending.append(day_total)

    avg_daily = sum(daily_spending) / len(daily_spending)
    max_daily = max(daily_spending)

    spending_variance = max_daily / avg_daily if avg_daily > 0 else 1

    if spending_variance <= 1.3:
        balance_score = 100  # Well balanced
    elif spending_variance <= 1.6:
        balance_score = 80
    elif spending_variance <= 2.0:
        balance_score = 60
        flags.append({
            "severity": "medium",
            "type": "spiking_daily_spend",
            "message": f"Highest day {max_daily:.0f} is {spending_variance:.1f}x average",
            "evidence": f"Unbalanced spending may strain budget on certain days"
        })
    else:
        balance_score = 40
        flags.append({
            "severity": "high",
            "type": "extreme_spending_variance",
            "message": f"Extreme variance: {spending_variance:.1f}x between days",
            "evidence": f"Highest {max_daily:.0f} vs average {avg_daily:.0f}"
        })

    scores["spending_balance"] = {
        "score": balance_score,
        "weight": 0.10,
        "weighted_score": balance_score * 0.10,
        "value": spending_variance,
        "evidence": f"Variance {spending_variance:.2f}x (max {max_daily:.0f}, avg {avg_daily:.0f})"
    }

    # 3. Contingency Reserve
    contingency_reserve = allocation["contingency"]["amount"]
    contingency_used = total_estimated - (budget["converted_to_dest"] - contingency_reserve)
    contingency_remaining = contingency_reserve - contingency_used

    if contingency_remaining >= contingency_reserve * 0.8:
        reserve_score = 100
    elif contingency_remaining >= contingency_reserve * 0.5:
        reserve_score = 80
    elif contingency_remaining >= contingency_reserve * 0.2:
        reserve_score = 60
        flags.append({
            "severity": "medium",
            "type": "contingency_depleted",
            "message": f"Only {contingency_remaining:.0f} of {contingency_reserve:.0f} contingency remains",
            "evidence": f"Little buffer for unexpected costs"
        })
    else:
        reserve_score = 30
        flags.append({
            "severity": "high",
            "type": "no_contingency",
            "message": f"Contingency exhausted or negative",
            "evidence": f"{contingency_remaining:.0f} remaining of {contingency_reserve:.0f} target"
        })

    scores["contingency_reserve"] = {
        "score": reserve_score,
        "weight": 0.05,
        "weighted_score": reserve_score * 0.05,
        "value": contingency_remaining / contingency_reserve,
        "evidence": f"{contingency_remaining:.0f} / {contingency_reserve:.0f} reserve remaining"
    }

    cost_score = sum(s["weighted_score"] for s in scores.values())

    return {
        "dimension": "Cost Efficiency",
        "overall_score": cost_score,
        "max_score": 25,
        "sub_scores": scores,
        "flags": flags,
        "evidence_summary": f"{utilization_rate*100:.0f}% budget used, {spending_variance:.2f}x variance, {contingency_remaining:.0f} contingency"
    }
```

### Dimension 4: Experience Match Scoring (25% weight)

**Sub-metrics:**
1. Interest alignment (12%)
2. Attraction quality rating (8%)
3. Uniqueness/exclusivity (5%)

```python
def score_experience_match(itinerary: dict, profile: dict) -> dict:
    """Score how well itinerary matches user interests."""

    scores = {}
    flags = []
    interests = profile["interests"]["mapped_categories"]
    primary_interest = profile["interests"]["primary_interest"]

    # 1. Interest Alignment
    interest_matched_activities = 0
    interest_scores = []

    for day in itinerary["days"]:
        for activity in day["activities"]:
            activity_categories = activity.get("categories", [])
            match_score = 0

            for cat in activity_categories:
                if cat in interests:
                    match_score += interests[cat]

            interest_scores.append(match_score)
            if match_score > 0.3:  # 30%+ match threshold
                interest_matched_activities += 1

    total_activities = sum(len(d["activities"]) for d in itinerary["days"])
    match_rate = interest_matched_activities / total_activities if total_activities > 0 else 0
    avg_interest_score = sum(interest_scores) / len(interest_scores) if interest_scores else 0

    # Score based on match rate and average score
    alignment_score = (match_rate * 0.6 + avg_interest_score * 0.4) * 100

    if alignment_score < 50:
        flags.append({
            "severity": "medium",
            "type": "poor_interest_match",
            "message": f"Only {match_rate*100:.0f}% of activities match stated interests",
            "evidence": f"Primary interest '{primary_interest}' underrepresented"
        })

    scores["interest_alignment"] = {
        "score": alignment_score,
        "weight": 0.12,
        "weighted_score": alignment_score * 0.12,
        "value": match_rate,
        "evidence": f"{interest_matched_activities}/{total_activities} activities match interests (avg score: {avg_interest_score:.2f})"
    }

    # 2. Attraction Quality Rating
    activity_ratings = []
    for day in itinerary["days"]:
        for activity in day["activities"]:
            rating = activity.get("rating", 3.5)  # Default mid-range
            activity_ratings.append(rating)

    avg_rating = sum(activity_ratings) / len(activity_ratings) if activity_ratings else 3.5

    # Score: 4.5+ = 100, 4.0-4.5 = 85, 3.5-4.0 = 70, <3.5 = 50
    if avg_rating >= 4.5:
        rating_score = 100
    elif avg_rating >= 4.0:
        rating_score = 85
    elif avg_rating >= 3.5:
        rating_score = 70
    else:
        rating_score = 50
        flags.append({
            "severity": "medium",
            "type": "low_quality_activities",
            "message": f"Average attraction rating {avg_rating:.1f}/5.0 is below recommended 3.5",
            "evidence": f"Consider higher-rated alternatives"
        })

    scores["attraction_quality"] = {
        "score": rating_score,
        "weight": 0.08,
        "weighted_score": rating_score * 0.08,
        "value": avg_rating,
        "evidence": f"Average rating {avg_rating:.2f}/5.0 across {len(activity_ratings)} activities"
    }

    # 3. Uniqueness/Exclusivity
    unique_activities = 0
    for day in itinerary["days"]:
        for activity in day["activities"]:
            if activity.get("unique_to_destination", False):
                unique_activities += 1
            elif activity.get("cannot_do_at_home", False):
                unique_activities += 1

    unique_rate = unique_activities / total_activities if total_activities > 0 else 0
    uniqueness_score = unique_rate * 100

    if unique_rate < 0.3:
        flags.append({
            "severity": "low",
            "type": "generic_activities",
            "message": f"Only {unique_rate*100:.0f}% of activities are unique to destination",
            "evidence": f"Consider more destination-specific experiences"
        })

    scores["uniqueness"] = {
        "score": uniqueness_score,
        "weight": 0.05,
        "weighted_score": uniqueness_score * 0.05,
        "value": unique_rate,
        "evidence": f"{unique_activities}/{total_activities} activities are destination-unique"
    }

    experience_score = sum(s["weighted_score"] for s in scores.values())

    return {
        "dimension": "Experience Match",
        "overall_score": experience_score,
        "max_score": 25,
        "sub_scores": scores,
        "flags": flags,
        "evidence_summary": f"{match_rate*100:.0f}% interest match, {avg_rating:.1f} avg rating, {unique_rate*100:.0f}% unique"
    }
```

### Overall Scoring and Verdict

```python
def calculate_overall_score(dimension_scores: list[dict]) -> dict:
    """Calculate weighted total and generate verdict."""

    total_score = sum(d["overall_score"] for d in dimension_scores)
    max_score = sum(d["max_score"] for d in dimension_scores)
    percentage = (total_score / max_score) * 100

    # Collect all flags
    all_flags = []
    for dimension in dimension_scores:
        all_flags.extend(dimension.get("flags", []))

    # Generate verdict
    if percentage >= 85:
        verdict = "EXCELLENT"
        verdict_color = "green"
        recommendation = "Itinerary is well-optimized. Proceed to final roadmap."
    elif percentage >= 70:
        verdict = "GOOD"
        verdict_color = "yellow"
        recommendation = "Itinerary is solid with minor issues. Address high-severity flags."
    elif percentage >= 50:
        verdict = "FAIR"
        verdict_color = "orange"
        recommendation = "Itinerary needs improvement. Address medium+ severity flags."
    else:
        verdict = "POOR"
        verdict_color = "red"
        recommendation = "Itinerary requires significant revision. Rebuild addressing all flags."

    # Group flags by severity
    critical_flags = [f for f in all_flags if f["severity"] == "high"]
    medium_flags = [f for f in all_flags if f["severity"] == "medium"]

    return {
        "total_score": total_score,
        "max_score": max_score,
        "percentage": percentage,
        "verdict": verdict,
        "verdict_color": verdict_color,
        "recommendation": recommendation,
        "dimension_breakdown": {d["dimension"]: d for d in dimension_scores},
        "flags": {
            "critical": critical_flags,
            "medium": medium_flags,
            "all": all_flags
        },
        "flag_summary": f"{len(critical_flags)} critical, {len(medium_flags)} medium, {len(all_flags)} total"
    }
```

## Outputs

### Scoring Report
```python
scoring_report = {
    "overall": {
        "total_score": float,
        "max_score": float,
        "percentage": float,
        "verdict": str,  # "EXCELLENT", "GOOD", "FAIR", "POOR"
        "recommendation": str
    },
    "dimensions": {
        "feasibility": {
            "score": float,
            "max_score": 30,
            "sub_scores": dict,
            "evidence": str
        },
        "pacing": {
            "score": float,
            "max_score": 20,
            "sub_scores": dict,
            "evidence": str
        },
        "cost_efficiency": {
            "score": float,
            "max_score": 25,
            "sub_scores": dict,
            "evidence": str
        },
        "experience_match": {
            "score": float,
            "max_score": 25,
            "sub_scores": dict,
            "evidence": str
        }
    },
    "flags": {
        "critical": list[dict],
        "medium": list[dict],
        "low": list[dict]
    },
    "evidence_summary": str,
    "scored_at": datetime
}
```

## Quality Gates

### Required (Must Have)
- [ ] All 4 dimensions scored with evidence
- [ ] At least one sub-metric per dimension
- [ ] Flags generated for scores < 70
- [ ] Verdict determined (EXCELLENT/GOOD/FAIR/POOR)

### Recommended (Should Have)
- [ ] Evidence citations for each score
- [ ] Specific, actionable flag messages
- [ ] Cost total compared to budget
- [ ] Interest alignment calculation shown

### Validated (Best Practice)
- [ ] Score > 50% before proceeding
- [ ] No critical flags unaddressed
- [ ] At least one dimension ≥ 80%
- [ ] Flags prioritized by severity

## Error Handling

**Missing Data for Scoring:**
```
ERROR: Cannot score feasibility — transit times missing.
  Required: transit time between all activity pairs
  Action: Re-run research with transit API calls
```

**Zero Activities:**
```
ERROR: No activities to score.
  Draft itinerary is empty.
  Action: Complete research phase before scoring.
```

**Incomparable Interests:**
```
WARNING: User interests don't match any activity categories.
  Interests: [X, Y, Z]
  Activity categories: [A, B, C]
  Experience match score will be low.
```

## Integration Notes

### Calls Before This Step
- `sub-profile-intake` (provides interests, constraints)
- `sub-framework-selector` (provides activity caps, budget allocation)
- Research phase (provides draft itinerary with times/costs)

### Calls After This Step
- `sub-improvement-roadmap` (uses flags to guide optimization)

### Data Passed Forward
- `flags.critical` → Improvement roadmap (must-address items)
- `flags.medium` → Improvement roadmap (should-address items)
- `dimensions.feasibility.evidence` → Final itinerary (justification)
- `overall.verdict` → Go/no-go decision for roadmap
