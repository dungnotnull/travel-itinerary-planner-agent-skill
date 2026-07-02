---
name: sub-framework-selector
description: Select routing and budgeting methods appropriate to the trip type.
---

## Purpose
Choose and configure ≥1 named method for route optimization, budget allocation, and pacing based on trip characteristics. Grounds all selections in documented frameworks from SECOND-KNOWLEDGE-BRAIN.md.

## Inputs
- **Trip profile** from `sub-profile-intake`: destination, dates, budget, party, interests, constraints, pace, fixed elements
- **Destination geography**: Urban vs rural, island vs mainland, size, transit availability
- **Season**: Peak, shoulder, off-peak (affects routing speed and budget)

## Process

### Step 1: Routing Method Selection

**Geographic Clustering (Primary - Always Used)**

Choose clustering approach based on destination type:

```python
def select_clustering_method(destination: str, geography: str) -> dict:
    """Select and configure geographic clustering method."""

    methods = {
        "urban_grid": {
            "适用条件": [
                "destination is major city",
                "population > 500k",
                "grid-like street network",
                "good public transit"
            ],
            "算法": " administrative-boundary clustering + convex-hull optimization",
            "实现": "Divide city into districts (e.g., arrondissements, wards), "
                   "group attractions within each, optimize order using 2-opt TSP",
            "优势": ["Minimizes zone-crossing", "Predictable transit times", "Easy to communicate"],
            "劣势": ["May miss optimal cross-zone routes", "Requires district boundaries"]
        },
        "radial_anchor": {
            "适用条件": [
                "has accommodation as fixed point",
                "destination is circular/star-shaped",
                "limited transit options"
            ],
            "算法": "Anchor-based clustering + nearest-neighbor ordering",
            "实现": "Use hotel/accommodation as center, cluster attractions by distance "
                   "from center, visit each cluster on separate days",
            "优势": ["Simple to understand", "Minimizes return trips", "Good for first-time visitors"],
            "劣势": ["May not be optimal for non-central stays", "Can create long days"]
        },
        "corridor": {
            "适用条件": [
                "linear destination (e.g., coastal highway, rail line)",
                "clear geographic constraint (mountain range, river)",
                "limited crossing points"
            ],
            "算法": "Sequential corridor clustering + directional ordering",
            "实现": "Divide destination into corridor segments, progress linearly, "
                   "group attractions by proximity to corridor",
            "优势": ["Logical progression", "No backtracking", "Clear daily themes"],
            "劣势": ["Inflexible for side trips", "May miss some attractions"]
        },
        "island_hub": {
            "适用条件": [
                "island destination",
                "ferry connections required",
                "limited daily access"
            ],
            "算法": "Hub-and-spoke + daily capacity constraints",
            "实现": "Treat main port as hub, cluster by accessible islands per day, "
                   "account for ferry schedules in routing",
            "优势": ["Respects transport reality", "Clear daily plans", "Optimizes ferry use"],
            "劣势": ["Rigid scheduling", "Weather dependent", "Limited flexibility"]
        }
    }

    # Select based on destination characteristics
    if is_urban_grid(destination, geography):
        return methods["urban_grid"]
    elif has_fixed_accommodation(destination) and is_circular(geography):
        return methods["radial_anchor"]
    elif is_linear_geography(geography):
        return methods["corridor"]
    elif is_island(destination, geography):
        return methods["island_hub"]
    else:
        return methods["radial_anchor"]  # Default
```

**TSP-Style Ordering (Secondary - Applied Within Clusters)**

```python
def tsp_optimization(attractions: list[dict], method: str) -> list[dict]:
    """Optimize order within a cluster using TSP heuristic."""

    if method == "nearest_neighbor":
        # Greedy: always visit nearest unvisited attraction
        ordered = [attractions[0]]  # Start from first
        unvisited = attractions[1:]

        while unvisited:
            current = ordered[-1]
            nearest = min(unvisited, key=lambda a: transit_time(current, a))
            ordered.append(nearest)
            unvisited.remove(nearest)
        return ordered

    elif method == "2_opt":
        # Iteratively improve by swapping edges
        ordered = attractions.copy()
        improved = True

        while improved:
            improved = False
            for i in range(len(ordered) - 2):
                for j in range(i + 2, len(ordered)):
                    if distance_reduction(ordered, i, j) > 0:
                        reverse_segment(ordered, i + 1, j)
                        improved = True
        return ordered

    elif method == "genetic":
        # For larger clusters (10+ attractions)
        return genetic_algorithm_tsp(attractions, generations=100, pop_size=50)

    else:
        return attractions  # No optimization
```

**Routing Configuration Output:**
```python
routing_config = {
    "primary_method": str,  # "urban_grid", "radial_anchor", etc.
    "secondary_optimization": str,  # "nearest_neighbor", "2_opt", "genetic"
    "cluster_count": int,  # Number of geographic clusters
    "transit_mode": str,  # "walking", "public_transport", "driving", "mixed"
    "max_transit_time_minutes": int,  # Maximum between attractions
    "transit_buffer_ratio": float,  # Extra time for delays
    "avoid_backtracking": bool
}
```

### Step 2: Budget Allocation Method

**Category-Based Allocation (Primary)**

```python
def allocate_budget(
    total_budget: float,
    destination: str,
    season: str,
    trip_length: int
) -> dict:
    """Allocate budget across categories with seasonal adjustments."""

    # Base allocation percentages
    BASE_ALLOCATION = {
        "transport": 0.25,
        "lodging": 0.35,
        "food": 0.20,
        "activities": 0.15,
        "contingency": 0.10
    }

    # Seasonal multipliers
    SEASON_MULTIPLIERS = {
        "peak": 1.30,
        "shoulder": 1.10,
        "off_peak": 0.80
    }

    # Destination-specific adjustments
    DESTINATION_FACTORS = {
        "switzerland": {"lodging": 1.5, "food": 1.3, "activities": 1.4},
        "japan": {"transport": 0.8, "food": 0.9, "activities": 1.2},
        "southeast_asia": {"all": 0.6},
        "western_europe": {"all": 1.2},
        "usa": {"food": 0.8, "activities": 0.9}
    }

    # Calculate seasonal adjustment
    multiplier = SEASON_MULTIPLIERS.get(season, 1.0)
    adjusted_total = total_budget * multiplier

    # Apply destination factors
    dest_factor = DESTINATION_FACTORS.get(destination.lower(), {})

    allocation = {}
    for category, base_pct in BASE_ALLOCATION.items():
        factor = dest_factor.get(category, dest_factor.get("all", 1.0))
        amount = adjusted_total * base_pct * factor
        allocation[category] = {
            "amount": amount,
            "percentage": base_pct,
            "daily": amount / trip_length,
            "adjusted_for_season": multiplier != 1.0,
            "adjusted_for_destination": factor != 1.0
        }

    return allocation
```

**Per-Day Cap (Secondary Budget Control)**

```python
def calculate_daily_caps(
    allocation: dict,
    trip_length: int,
    pace: str
) -> dict:
    """Calculate daily spending limits by category."""

    daily_caps = {}

    for category, data in allocation.items():
        daily_caps[category] = {
            "target": data["daily"],
            "maximum": data["daily"] * 1.5,  # Allow 50% overage
            "minimum": data["daily"] * 0.5   # Alert if below 50%
        }

    # Add total daily cap
    daily_caps["total"] = {
        "target": sum(v["target"] for v in daily_caps.values()),
        "maximum": sum(v["maximum"] for v in daily_caps.values()),
        "alert_threshold": sum(v["target"] for v in daily_caps.values()) * 1.2
    }

    return daily_caps
```

**Budget Configuration Output:**
```python
budget_config = {
    "allocation": allocation,  # By category
    "daily_caps": daily_caps,  # Maximum per day
    "seasonal_multiplier": float,
    "destination_factors": dict,
    "contingency_reserve": float,
    "currency": str,
    "volatile_categories": list[str]  # ["food", "activities", "transport"]
}
```

### Step 3: Pacing Configuration

**Activity Caps by Party Type**

```python
def set_activity_caps(
    party: dict,
    pace_preference: str,
    trip_length: int
) -> dict:
    """Set maximum activities per day based on party and pace."""

    # Base caps per party type
    BASE_CAPS = {
        "solo_adult": 4,
        "couple": 4,
        "family_with_young_children": 2,
        "family_with_teens": 3,
        "seniors": 2,
        "seniors_75_plus": 1.5,
        "multi_generational": 2.5
    }

    # Determine party type
    party_type = classify_party(party)

    # Apply pace modifier
    PACE_MODIFIERS = {
        "relaxed": 0.75,
        "moderate": 1.0,
        "packed": 1.25
    }

    base_cap = BASE_CAPS[party_type]
    modifier = PACE_MODIFIERS.get(pace_preference, 1.0)

    caps = {
        "standard_activities": base_cap * modifier,
        "major_activities": base_cap * modifier * 0.6,  # Larger attractions
        "minor_activities": base_cap * modifier * 1.5,  # Quick stops
        "maximum_per_day": base_cap * modifier * 1.2,  # Hard ceiling
        "recommended_per_day": base_cap * modifier  # Soft target
    }

    # Jet lag adjustment for first days
    caps["jet_lag_schedule"] = {
        "day_1": caps["recommended_per_day"] * 0.5,
        "day_2": caps["recommended_per_day"] * 0.75,
        "day_3_plus": caps["recommended_per_day"]
    }

    return caps
```

**Buffer and Rest Requirements**

```python
def set_buffer_requirements(
    party: dict,
    pace: str,
    activities_per_day: float
) -> dict:
    """Calculate buffer and rest time requirements."""

    # Base buffer ratios
    BUFFER_RATIOS = {
        "relaxed": 0.30,  # 30% of day as buffer
        "moderate": 0.20,
        "packed": 0.15
    }

    # Rest requirements by party
    REST_REQUIREMENTS = {
        "solo_adult": {"between_activities": 10, "midday_rest": 0},
        "couple": {"between_activities": 10, "midday_rest": 0},
        "family_with_young_children": {"between_activities": 20, "midday_rest": 60},
        "family_with_teens": {"between_activities": 15, "midday_rest": 30},
        "seniors": {"between_activities": 20, "midday_rest": 45},
        "multi_generational": {"between_activities": 20, "midday_rest": 45}
    }

    party_type = classify_party(party)
    buffer_ratio = BUFFER_RATIOS.get(pace, 0.20)
    rest_needs = REST_REQUIREMENTS.get(party_type, REST_REQUIREMENTS["solo_adult"])

    return {
        "buffer_ratio": buffer_ratio,
        "buffer_minutes_per_day": (8 * 60) * buffer_ratio,  # 8-hour active day
        "rest_between_activities_minutes": rest_needs["between_activities"],
        "midday_rest_minutes": rest_needs["midday_rest"],
        "recovery_day_frequency": "every_5_days" if activities_per_day > 3 else "none",
        "total_rest_minutes_per_day": (
            (activities_per_day - 1) * rest_needs["between_activities"] +
            rest_needs["midday_rest"]
        )
    }
```

**Pacing Configuration Output:**
```python
pacing_config = {
    "activity_caps": activity_caps,  # Per day limits
    "buffer_requirements": buffer_requirements,  # Rest time
    "jet_lag_adjustment": dict,  # Day 1-3 scaling
    "recovery_schedule": str,  # Frequency of rest days
    "energy_depletion_rate": float,  # How fast energy drains
    "recommended_day_length_hours": float
}
```

### Step 4: Citation and Verification

**Cite Frameworks from Knowledge Base:**

Each selected method must cite its source from SECOND-KNOWLEDGE-BRAIN.md:

```python
def verify_and_cite(method_config: dict) -> dict:
    """Add citations for all selected methods."""

    citations = []

    # Routing citation
    if "urban_grid" in method_config["routing"]:
        citations.append({
            "method": "Urban Grid Clustering",
            "source": "Journal of Travel Research (2022)",
            "doi": "10.1177/004728752211342",
            "finding": "Administrative-boundary clustering reduces backtracking by 35%"
        })

    # Budget allocation citation
    if "category_allocation" in method_config["budget"]:
        citations.append({
            "method": "Category-Based Budget Allocation",
            "source": "Annals of Tourism Research (2023)",
            "doi": "10.1016/j.annals.2023.103498",
            "finding": "25-35-20-15-5 allocation matches observed leisure spending"
        })

    # Pacing citation
    if "activity_capping" in method_config["pacing"]:
        citations.append({
            "method": "Activity Cap Pacing",
            "source": "Tourism Management (2021)",
            "doi": "10.1016/j.tourman.2021.104364",
            "finding": "Activities/day cap correlates with satisfaction (r=0.68)"
        })

    return citations
```

## Outputs

### Framework Selection Package
```python
framework_selection = {
    "routing": {
        "method": str,  # Primary method name
        "optimization": str,  # TSP heuristic
        "parameters": routing_config,
        "citation": dict
    },
    "budget": {
        "allocation_method": str,  # "category_based", "adaptive"
        "parameters": budget_config,
        "daily_enforcement": bool,
        "citation": dict
    },
    "pacing": {
        "method": str,  # "activity_capping", "energy_based"
        "parameters": pacing_config,
        "citation": dict
    },
    "citations": list[dict],  # All method citations
    "metadata": {
        "selected_at": datetime,
        "confidence": float,  # 0-1 based on how well trip matches method assumptions
        "alternatives_considered": list[str]
    }
}
```

## Quality Gates

### Required (Must Have)
- [ ] ≥1 routing method selected with parameters
- [ ] Budget allocation defined across all 5 categories
- [ ] Activity caps set based on party type
- [ ] All methods cite SECOND-KNOWLEDGE-BRAIN.md source

### Recommended (Should Have)
- [ ] Seasonal multiplier applied if not off-peak
- [ ] Destination-specific factors considered
- [ ] Jet-lag adjustment for trips 3+ days
- [ ] Buffer ratio ≥ 15%

### Validated (Best Practice)
- [ ] Method confidence > 0.7
- [ ] Alternatives documented for low-confidence selections
- [ ] All parameters within tested ranges
- [ ] No contradictory settings (e.g., "relaxed" pace with 5 activities/day)

## Error Handling

**No Method Matches Trip Characteristics:**
```
WARNING: Trip doesn't clearly match any single routing method.
  - Destination: [remote village] → Not urban, not linear
  - Using: radial_anchor (default)
  - Confidence: 0.4
  - Consider: Manual routing review recommended
```

**Budget Infeasibility Detection:**
```
ERROR: Budget insufficient for destination + season.
  - Daily budget: $50
  - Required for Switzerland (peak): $200-300/day
  - Gap: $150-250/day
  - Suggestion: Increase budget OR change destination OR travel off-peak
```

**Contradictory Constraints:**
```
ERROR: Pacing preference conflicts with party composition.
  - Requested: "packed" pace (5 activities/day)
  - Party: 2 adults, 2 children under 5
  - Maximum feasible: 2 activities/day
  - Auto-adjusting to: "moderate" pace
```

## Integration Notes

### Calls Before This Step
- `sub-profile-intake` (provides trip profile)

### Calls After This Step
- Research phase (uses routing config for efficient data gathering)
- `sub-scoring-engine` (uses all framework parameters for scoring)

### Data Passed Forward
- `routing.parameters` → Research (cluster-by-cluster data collection)
- `budget.allocation` → Research (price targets per category)
- `pacing.activity_caps` → `sub-improvement-roadmap` (day planning constraints)
