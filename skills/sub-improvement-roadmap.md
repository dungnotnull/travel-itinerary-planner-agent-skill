---
name: sub-improvement-roadmap
description: Produce the optimized day-by-day itinerary with budget breakdown, alternatives, and contingencies.
---

## Purpose
Transform a scored draft into the final, improved itinerary by addressing scoring flags, optimizing routing, adding buffers, and providing comprehensive alternatives and contingencies.

## Inputs
- **Scored draft** from `sub-scoring-engine`: dimension scores, flags, evidence
- **Trip profile** from `sub-profile-intake`: constraints, interests, pace
- **Framework selection** from `sub-framework-selector`: routing method, budget caps
- **Research data**: activities with metadata, prices (dated), transit times

## Process

### Step 1: Address Critical and High-Severity Flags

**Priority 1: Infeasibility Flags**

```python
def address_infeasibility_flags(draft: dict, flags: list[dict]) -> dict:
    """Fix infeasible schedule elements."""

    improved = draft.copy()
    changes = []

    # Fix hours mismatches
    hours_flags = [f for f in flags if f["type"] == "hours_mismatch"]
    for flag in hours_flags:
        # Find the affected activity and reschedule
        activity = find_activity(improved, flag["message"])
        if activity:
            new_time = find_valid_time_slot(improved, activity)
            if new_time:
                activity["start_time"] = new_time
                changes.append(f"Rescheduled {activity['name']} to {new_time}")

    # Fix excessive transit
    transit_flags = [f for f in flags if f["type"] == "excessive_transit"]
    for flag in transit_flags:
        # Re-cluster the problematic day
        day_num = extract_day_number(flag["message"])
        improved["days"][day_num - 1] = recluster_day(
            improved["days"][day_num - 1],
            method="nearest_neighbor"
        )
        changes.append(f"Re-clustered day {day_num} to minimize backtracking")

    # Fix buffer inadequacy
    buffer_flags = [f for f in flags if f["type"] in ["insufficient_buffer", "inadequate_buffer"]]
    for flag in buffer_flags:
        day_num = extract_day_number(flag["message"])
        improved = add_buffers_to_day(improved, day_num)
        changes.append(f"Added buffers to day {day_num}")

    return improved, changes
```

**Priority 2: Budget Flags**

```python
def address_budget_flags(draft: dict, flags: list[dict], framework: dict) -> dict:
    """Fix budget-related issues."""

    improved = draft.copy()
    changes = []

    # Fix budget overrun
    overrun_flags = [f for f in flags if f["type"] == "budget_overrun"]
    if overrun_flags:
        # Strategy 1: Remove lowest-interest activities
        improved = remove_low_interest_activities(improved, threshold=0.3)
        changes.append("Removed activities with <30% interest match")

        # Strategy 2: Downgrade expensive activities
        improved = find_alternatives_for_expensive(improved, max_cost_ratio=0.7)
        changes.append("Found cheaper alternatives for high-cost activities")

    # Fix spending variance
    variance_flags = [f for f in flags if f["type"] == "spiking_daily_spend"]
    for flag in variance_flags:
        high_cost_day = identify_high_cost_day(improved)
        low_cost_day = identify_low_cost_day(improved)

        # Move one activity from high to low cost day
        if high_cost_day and low_cost_day:
            movable = find_most_moveable_activity(high_cost_day)
            low_cost_day["activities"].append(movable)
            high_cost_day["activities"].remove(movable)
            changes.append(f"Moved {movable['name']} from day {high_cost_day['day_number']} to {low_cost_day['day_number']}")

    return improved, changes
```

**Priority 3: Pacing Flags**

```python
def address_pacing_flags(draft: dict, flags: list[dict], framework: dict) -> dict:
    """Fix pacing and fatigue issues."""

    improved = draft.copy()
    changes = []
    activity_caps = framework["pacing"]["parameters"]["activity_caps"]

    # Fix overpacked days
    overpacked_flags = [f for f in flags if f["type"] == "overpacked_day"]
    for flag in overpacked_flags:
        day_num = extract_day_number(flag["message"])
        day = improved["days"][day_num - 1]

        # Get cap for this day
        cap = get_cap_for_day(activity_caps, day_num)

        while len(day["activities"]) > cap:
            # Move lowest-interest activity to another day
            activity = find_lowest_interest_activity(day)
            target_day = find_best_alternative_day(improved, activity, exclude=day_num)

            if target_day:
                day["activities"].remove(activity)
                target_day["activities"].append(activity)
                changes.append(f"Moved {activity['name']} to day {target_day['day_number']} (overpacked day {day_num})")
            else:
                # No room, consider dropping
                if activity.get("priority", 50) < 70:  # Not must-see
                    day["activities"].remove(activity)
                    changes.append(f"Dropped {activity['name']} (low priority, no room to reschedule)")
                break

    # Add jet-lag adjustment if missing
    jet_lag_flags = [f for f in flags if f["type"] == "no_jet_lag_adjustment"]
    if jet_lag_flags and len(improved["days"]) >= 2:
        # Reduce day 1 and 2
        improved = apply_jet_lag_reduction(improved)
        changes.append("Applied jet-lag reduction to days 1-2")

    return improved, changes
```

### Step 2: Optimize Geographic Clustering

```python
def optimize_clustering(itinerary: dict, framework: dict) -> dict:
    """Re-cluster activities by area to minimize transit."""

    routing_method = framework["routing"]["method"]
    optimization = framework["routing"]["optimization"]

    if routing_method == "urban_grid":
        return optimize_urban_grid_clustering(itinerary, optimization)
    elif routing_method == "radial_anchor":
        return optimize_radial_clustering(itinerary, optimization)
    elif routing_method == "corridor":
        return optimize_corridor_clustering(itinerary, optimization)
    else:
        return itinerary  # No clustering optimization


def optimize_urban_grid_clustering(itinerary: dict, optimization_method: str) -> dict:
    """Optimize within urban grid structure."""

    # Group all activities by geographic zone
    zones = group_by_zone(itinerary["activities"])

    # Create zone-based day clusters
    day_clusters = []
    for zone_name, activities in zones.items():
        # Optimize order within zone
        ordered = tsp_optimize(activities, method=optimization_method)
        day_clusters.append({
            "zone": zone_name,
            "activities": ordered,
            "estimated_transit_time": calculate_zone_transit(ordered),
            "cluster_efficiency": calculate_cluster_efficiency(ordered)
        })

    # Assign clusters to days
    improved_days = []
    for i, cluster in enumerate(day_clusters):
        improved_days.append({
            "day_number": i + 1,
            "date": itinerary["days"][i]["date"] if i < len(itinerary["days"]) else None,
            "zone": cluster["zone"],
            "activities": cluster["activities"],
            "theme": generate_zone_theme(cluster["activities"]),
            "transit_summary": cluster["estimated_transit_time"],
            "buffers": generate_buffers(cluster["activities"])
        })

    return {"days": improved_days}


def tsp_optimize(activities: list[dict], method: str) -> list[dict]:
    """Optimize activity order using TSP heuristic."""

    if method == "nearest_neighbor":
        return nearest_neighbor_tsp(activities)
    elif method == "2_opt":
        return two_opt_tsp(activities)
    elif method == "genetic":
        return genetic_tsp(activities)
    else:
        return activities


def nearest_neighbor_tsp(activities: list[dict]) -> list[dict]:
    """Nearest neighbor heuristic for TSP."""
    if not activities:
        return []

    unvisited = activities.copy()
    ordered = [unvisited.pop(0)]  # Start from first activity

    while unvisited:
        current = ordered[-1]
        nearest = min(unvisited, key=lambda a: get_transit_time(current, a))
        unvisited.remove(nearest)
        ordered.append(nearest)

    return ordered
```

### Step 3: Insert Buffers and Rest Time

```python
def add_buffers(itinerary: dict, framework: dict) -> dict:
    """Insert buffer and rest time throughout itinerary."""

    buffer_config = framework["pacing"]["parameters"]["buffer_requirements"]
    improved = itinerary.copy()

    for day in improved["days"]:
        activities = day["activities"]
        buffers = []

        # Add between-activity buffers
        for i in range(len(activities) - 1):
            current = activities[i]
            next_act = activities[i + 1]

            # Calculate required buffer
            transit_time = get_transit_time(current, next_act)
            buffer_duration = max(
                buffer_config["rest_between_activities_minutes"],
                transit_time * 0.2  # 20% contingency on transit
            )

            buffers.append({
                "after_activity": current["id"],
                "before_activity": next_act["id"],
                "duration": buffer_duration,
                "type": "transit_buffer",
                "purpose": "Transit + rest between activities"
            })

        # Add midday rest if required
        if buffer_config["midday_rest_minutes"] > 0:
            mid_point = len(activities) // 2
            buffers.append({
                "after_activity": activities[mid_point]["id"],
                "duration": buffer_config["midday_rest_minutes"],
                "type": "midday_rest",
                "purpose": "Scheduled rest break",
                "suggestions": ["lunch", "cafe break", "return to hotel"]
            })

        day["buffers"] = buffers
        day["total_buffer_time"] = sum(b["duration"] for b in buffers)

    return improved
```

### Step 4: Create Budget Breakdown

```python
def create_budget_breakdown(itinerary: dict, framework: dict, profile: dict) -> dict:
    """Generate detailed budget breakdown vs allocated budget."""

    budget = profile["budget"]
    allocation = framework["budget"]["parameters"]["allocation"]

    # Calculate costs by category
    costs = {"transport": 0, "lodging": 0, "food": 0, "activities": 0}

    for day in itinerary["days"]:
        for activity in day["activities"]:
            cat = activity.get("category", "activities")
            if cat in costs:
                costs[cat] += activity.get("estimated_cost", 0)

    total_cost = sum(costs.values())
    contingency = allocation["contingency"]["amount"]
    remaining = budget["converted_to_dest"] - total_cost

    # Generate breakdown
    breakdown = {
        "allocated": {
            "total": budget["converted_to_dest"],
            "by_category": {cat: alloc["amount"] for cat, alloc in allocation.items()}
        },
        "estimated": {
            "total": total_cost,
            "by_category": costs,
            "per_day": total_cost / len(itinerary["days"])
        },
        "contingency": {
            "allocated": contingency,
            "remaining": remaining,
            "utilization_rate": (total_cost / budget["converted_to_dest"]) * 100
        },
        "daily_breakdown": []
    }

    # Daily breakdown
    for day in itinerary["days"]:
        day_total = sum(a.get("estimated_cost", 0) for a in day["activities"])
        breakdown["daily_breakdown"].append({
            "day": day["day_number"],
            "date": day.get("date"),
            "total": day_total,
            "activities": len(day["activities"]),
            "avg_per_activity": day_total / len(day["activities"]) if day["activities"] else 0
        })

    # Status assessment
    if total_cost <= budget["converted_to_dest"] and remaining >= contingency * 0.5:
        status = "ON_TRACK"
        status_color = "green"
    elif total_cost <= budget["converted_to_dest"]:
        status = "TIGHT"
        status_color = "yellow"
    else:
        status = "OVER_BUDGET"
        status_color = "red"

    breakdown["status"] = status
    breakdown["status_color"] = status_color

    return breakdown
```

### Step 5: Add Alternatives and Contingencies

```python
def add_alternatives_and_contingencies(itinerary: dict, profile: dict) -> dict:
    """Add rain-day alternatives and closure contingencies."""

    improved = itinerary.copy()

    for day in improved["days"]:
        alternatives = []

        # Rain-day alternatives
        for activity in day["activities"]:
            if activity.get("outdoor", False):
                indoor_alt = find_indoor_alternative(activity, profile["destination"])
                if indoor_alt:
                    alternatives.append({
                        "for_activity": activity["id"],
                        "type": "rain_day",
                        "trigger": "rain > 50% probability or extreme weather",
                        "alternative": indoor_alt,
                        "cost_difference": indoor_alt.get("estimated_cost", 0) - activity.get("estimated_cost", 0)
                    })

        # Closure contingencies
        for activity in day["activities"]:
            if activity.get("closure_probability", 0) > 0.1:  # 10%+ chance
                closure_alt = find_closure_alternative(activity, day["activities"])
                if closure_alt:
                    alternatives.append({
                        "for_activity": activity["id"],
                        "type": "closure",
                        "trigger": f"{activity['name']} closed on visit day",
                        "alternative": closure_alt,
                        "note": "Call ahead to verify hours"
                    })

        day["alternatives"] = alternatives

    # Add booking notes for time-sensitive activities
    improved = add_booking_notes(improved)

    return improved


def add_booking_notes(itinerary: dict) -> dict:
    """Add booking and timing notes for activities."""

    for day in itinerary["days"]:
        for activity in day["activities"]:
            notes = []

            # Booking requirements
            if activity.get("booking_required", False):
                lead_time = activity.get("booking_lead_time", "7 days")
                notes.append(f"Book {lead_time} in advance")

            # Time-sensitive activities
            if activity.get("time_specific", False):
                notes.append(f"Must visit at {activity.get('optimal_time', 'specified time')}: {activity['start_time']}")

            # Seasonal considerations
            if activity.get("seasonal", False):
                notes.append(f"Seasonal: {activity.get('season_description', 'check availability')}")

            # High-demand warning
            if activity.get("demand_level") == "high":
                notes.append("High demand — book early or arrive at opening")

            activity["booking_notes"] = notes

    return itinerary
```

### Step 6: Generate Improvement Summary

```python
def generate_improvement_summary(
    original_scores: dict,
    improved_itinerary: dict,
    changes_made: list[str]
) -> dict:
    """Document improvements made."""

    return {
        "changes_made": changes_made,
        "flags_addressed": {
            "critical": len([c for c in changes_made if "critical" in c.lower()]),
            "medium": len([c for c in changes_made if "medium" in c.lower()])
        },
        "optimizations_applied": [
            "Geographic clustering to minimize transit",
            "TSP-style ordering within zones",
            "Buffer insertion for rest and transit",
            "Activity rebalancing for budget"
        ],
        "quality_improvements": {
            "transit_reduction": "estimated 20-35% less backtracking",
            "budget_balance": "daily spending variance < 1.3x",
            "pacing_compliance": "all days within activity caps",
            "contingency_coverage": "alternatives for all high-risk activities"
        }
    }
```

## Outputs

### Final Itinerary Package
```python
final_itinerary = {
    "trip_summary": {
        "destination": str,
        "dates": (start, end),
        "length_days": int,
        "budget": {"allocated": float, "estimated": float, "status": str}
    },
    "scores": {
        "original": dict,  # Pre-improvement scores
        "improved": dict,  # Post-improvement scores (re-calculate)
        "improvement": str  # Summary of gains
    },
    "days": [
        {
            "day_number": int,
            "date": date,
            "zone": str,  # Geographic cluster
            "theme": str,  # Day's focus
            "activities": [
                {
                    "id": str,
                    "name": str,
                    "category": str,
                    "start_time": time,
                    "duration_minutes": int,
                    "location": {"name": str, "address": str},
                    "estimated_cost": float,
                    "currency": str,
                    "price_dated": str,  # "YYYY-MM-DD"
                    "volatile": bool,
                    "rating": float,
                    "interest_match": float,
                    "outdoor": bool,
                    "booking_required": bool,
                    "booking_notes": list[str],
                    "categories": list[str],
                    "unique_to_destination": bool
                }
            ],
            "buffers": [
                {
                    "after_activity": str,
                    "duration_minutes": int,
                    "type": str,  # "transit_buffer", "midday_rest"
                    "purpose": str
                }
            ],
            "transit_summary": {
                "total_minutes": int,
                "between_activities": int,
                "modes": list[str]
            },
            "daily_cost": float,
            "alternatives": [
                {
                    "for_activity": str,
                    "type": str,  # "rain_day", "closure"
                    "trigger": str,
                    "alternative": dict,  # Activity object
                    "cost_difference": float
                }
            ],
            "contingencies": list[str]  # Day-specific warnings
        }
    ],
    "budget_breakdown": {
        "allocated": dict,
        "estimated": dict,
        "contingency": dict,
        "daily_breakdown": list,
        "status": str,
        "status_color": str
    },
    "improvements": {
        "changes_made": list[str],
        "flags_addressed": dict,
        "quality_gains": dict
    },
    "metadata": {
        "generated_at": datetime,
        "data_currency": str,  # "Prices as of YYYY-MM-DD"
        "offline_mode": bool,
        "confidence_level": str
    }
}
```

## Quality Gates

### Required (Must Have)
- [ ] All critical flags addressed
- [ ] Geographic clustering applied
- [ ] Buffers inserted (minimum 15% of day)
- [ ] Budget breakdown calculated
- [ ] Alternatives provided for outdoor activities

### Recommended (Should Have)
- [ ] At least one alternative per outdoor activity
- [ ] Booking notes for time-sensitive activities
- [ ] Daily budget variance < 1.5x average
- [ ] Theme/day titles for each day

### Validated (Best Practice)
- [ ] All days within activity caps
- [ ] Transit time < 30% of total time
- [ ] Budget status not OVER_BUDGET
- [ ] Alternatives for 10%+ closure probability activities

## Error Handling

**Cannot Fix Critical Flag:**
```
WARNING: Cannot address budget overrun with available options.
  - Budget: $1000, Estimated: $1500
  - All activities are must-see priority
  - No cheaper alternatives found
  Recommendation: Revisit budget scope or destination
```

**No Room for Activity:**
```
WARNING: Activity cannot be rescheduled.
  - Activity: XYZ Museum
  - All days at capacity
  - Dropped due to low priority (40%)
  Action: User can manually re-add if critical
```

**No Indoor Alternative:**
```
WARNING: No indoor alternative found for outdoor activity.
  - Activity: Hiking Trail
  - Destination lacks indoor nature activities
  - Rain day: Skip and reschedule for clear day
```

## Integration Notes

### Calls Before This Step
- `sub-profile-intake` (constraints for alternatives)
- `sub-framework-selector` (routing method, caps)
- `sub-scoring-engine` (flags to address)

### Calls After This Step
- None (this is the final step before output)

### Data Passed Forward
- Entire `final_itinerary` object → Main harness for rendering
- `improvements.changes_made` → Summary section
- `budget_breakdown` → Budget section
- `days[].alternatives` → Contingencies section
