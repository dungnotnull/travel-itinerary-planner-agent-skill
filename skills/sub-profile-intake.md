---
name: sub-profile-intake
description: Capture destination, dates, budget, party composition, interests, and constraints for trip planning.
---

## Purpose
Assemble the constraints and preferences that shape the itinerary through structured data collection and validation.

## Inputs
User-provided trip parameters (may be incomplete or unstructured):
- Destination (city, region, country)
- Travel dates or trip length
- Total budget (with currency)
- Party composition (adults, children ages, seniors)
- Travel interests and preferences
- Constraints (mobility, dietary, accessibility)
- Pace preference
- Must-see attractions or fixed bookings

## Process

### Step 1: Validate Hard Constraints
Block execution if either dates OR budget is missing. Request both before proceeding.

**Validation Rules:**
```python
# Date validation
if not dates and not trip_length:
    return "ERROR: Please provide your travel dates (YYYY-MM-DD to YYYY-MM-DD) or trip length in days."

# Budget validation
if not budget:
    return "ERROR: Please provide your total budget amount and currency (e.g., 'USD 5000')."

# Date logic validation
if departure_date and return_date and return_date <= departure_date:
    return "ERROR: Return date must be after departure date."

# Budget minimum validation
if budget < 100:  # Arbitrary minimum
    return "WARNING: Budget seems very low. Confirm this is correct."
```

### Step 2: Capture Party Composition
Collect detailed party information for activity and pacing decisions.

**Data Structure:**
```python
party = {
    "adults": int,  # Age 18-64
    "children": int,  # Age 0-17
    "seniors": int,  # Age 65+
    "child_ages": list[int],  # For activity appropriateness
    "total": int  # Sum of all
}
```

**Implications:**
- Children < 5: Stroller access, diaper facilities needed, 2 max activities/day
- Children 5-12: Kid-friendly activities, 2-3 activities/day
- Children 13-17: Adult-like activities with shorter attention
- Seniors 65+: Reduced walking, frequent rest, 2 activities/day
- Seniors 75+: Mobility access priority, 1-2 activities/day

### Step 3: Collect Interests for Experience Weighting
Map freeform interests to standardized categories for matching.

**Interest Categories (Exhaustive):**
- Culture & History: Museums, historical sites, architecture, monuments
- Food & Drink: Local cuisine, food tours, cooking classes, markets, wineries/breweries
- Nature & Outdoors: Parks, hiking, beaches, gardens, wildlife, scenic views
- Entertainment: Shows, concerts, nightlife, gaming, performances
- Adventure: Extreme sports, outdoor activities, water sports, cycling
- Shopping: Markets, malls, boutiques, local crafts
- Relaxation: Spas, beaches, cafes, leisure walking
- Art & Design: Galleries, street art, design districts, workshops
- Spiritual: Temples, churches, meditation, religious sites
- Family: Kid-friendly attractions, theme parks, playgrounds

**Interest Mapping Algorithm:**
```python
def map_interests(user_input: list[str]) -> dict[str, float]:
    """Map user interests to weighted categories."""
    category_scores = {cat: 0.0 for cat in INTEREST_CATEGORIES}

    for interest in user_input:
        similarity = semantic_similarity(interest, INTEREST_CATEGORIES)
        for cat, score in similarity.items():
            category_scores[cat] += score

    # Normalize to 1.0
    total = sum(category_scores.values())
    if total > 0:
        category_scores = {k: v/total for k, v in category_scores.items()}

    return {k: v for k, v in category_scores.items() if v > 0.1}
```

### Step 4: Document Constraints for Feasibility
Collect all constraints that affect feasibility and routing.

**Constraint Types & Data Collection:**

1. **Mobility Constraints**
```python
mobility = {
    "max_walking_distance_m": int,  # Maximum between points
    "wheelchair_required": bool,
    "elevator_access_needed": bool,
    "step_free_only": bool,
    "seating_needed_frequency": str  # "every 30min", "every hour"
}
```

2. **Dietary Constraints**
```python
dietary = {
    "restrictions": list[str],  # ["halal", "kosher", "vegan", "vegetarian"]
    "allergies": list[str],  # ["nuts", "dairy", "gluten"]
    "requirements": list[str]  # ["prayer space", "alcohol-free"]
}
```

3. **Accessibility Needs**
```python
accessibility = {
    "visual_aids": bool,
    "hearing_aids": bool,
    "assistance_animal": bool,
    "companion_required": bool
}
```

### Step 5: Capture Pace Preference
Determine desired travel pace for activity capping.

**Pace Levels:**
```python
PACE_LEVELS = {
    "relaxed": {
        "description": "Plenty of time, no rushing",
        "activities_per_day": {"solo": 3, "couple": 3, "family": 2, "seniors": 1.5},
        "buffer_ratio": 0.30
    },
    "moderate": {
        "description": "Balanced pace, some free time",
        "activities_per_day": {"solo": 4, "couple": 4, "family": 2.5, "seniors": 2},
        "buffer_ratio": 0.20
    },
    "packed": {
        "description": "Maximize sights, can be tiring",
        "activities_per_day": {"solo": 5, "couple": 5, "family": 3, "seniors": 2.5},
        "buffer_ratio": 0.15
    }
}
```

### Step 6: Note Must-Sees and Fixed Bookings
Anchor points that constrain routing.

**Data Structure:**
```python
fixed_elements = {
    "must_see_attractions": list[str],  # Non-negotiable inclusions
    "booked_accommodation": {
        "name": str,
        "location": str,  # Address or coordinates
        "dates": (start, end)
    },
    "booked_activities": list[{
        "name": str,
        "datetime": datetime,
        "location": str,
        "duration": int  # minutes
    }],
    "transport_bookings": list[{
        "type": str,  # "flight", "train", "bus"
        "departure": datetime,
        "arrival": datetime,
        "origin": str,
        "destination": str
    }]
}
```

## Outputs

### Trip Profile (Structured Object)
```python
trip_profile = {
    "destination": {
        "primary": str,  # Main destination
        "secondary": list[str],  # Day trips or nearby
        "country_code": str,  # ISO 3166-1 alpha-2
    },
    "dates": {
        "departure": date,
        "return": date,
        "length_days": int,
        "nights": int,
        "season": str,  # "peak", "shoulder", "off-peak"
    },
    "budget": {
        "total": float,
        "currency": str,
        "converted_to_dest": float,  # In destination currency
        "per_day": float,
        "contingency_reserve": float,  # 10% of total
    },
    "party": {
        "adults": int,
        "children": int,
        "seniors": int,
        "child_ages": list[int],
        "total": int,
        "pace_category": str,  # "solo", "couple", "family", "seniors"
    },
    "interests": {
        "user_input": list[str],
        "mapped_categories": dict[str, float],  # Normalized scores
        "primary_interest": str,
        "secondary_interests": list[str]
    },
    "constraints": {
        "mobility": mobility,
        "dietary": dietary,
        "accessibility": accessibility
    },
    "pace": {
        "preference": str,  # "relaxed", "moderate", "packed"
        "activities_per_day_target": float,
        "buffer_ratio": float
    },
    "fixed_elements": fixed_elements,
    "metadata": {
        "profile_created_at": datetime,
        "timezone": str,
        "locale": str
    }
}
```

## Validation & Quality Gates

### Required Fields (Must Have)
- [ ] Destination specified (city or country minimum)
- [ ] Dates or trip length provided
- [ ] Budget amount and currency specified
- [ ] Party composition at least "1 adult"

### Recommended Fields (Should Have)
- [ ] At least 2 interest categories mapped
- [ ] Pace preference captured (defaults to moderate)
- [ ] Mobility/dietary constraints noted even if "none"

### Optional Fields (Nice to Have)
- [ ] Must-see attractions listed
- [ ] Fixed bookings documented
- [ ] Secondary destinations for day trips

## Error Handling

### Common Validation Errors

**Missing Dates:**
```
ERROR: Travel dates not provided. Please specify:
- Option 1: Exact dates (e.g., "2026-08-15 to 2026-08-22")
- Option 2: Duration + start date (e.g., "7 days starting August 15")
- Option 3: Duration only (e.g., "5-day trip")
```

**Missing Budget:**
```
ERROR: Budget not provided. Please specify:
- Total amount in your currency (e.g., "$5000 USD")
- Daily budget preference (e.g., "$500/day for 7 days")
- Flexible range (e.g., "$4000-5000 USD")
```

**Unclear Destination:**
```
WARNING: Destination ambiguous. "Paris" could be Paris, France or Paris, Texas.
Please clarify with country code or confirm default (France = FR).
```

**Impossible Constraints:**
```
ERROR: Constraints conflict with destination/season:
- "Switzerland in July" + "$100 budget" → Infeasible
- "Disney with toddlers" + "packed pace" → Not recommended
- "Remote hiking" + "wheelchair required" → Incompatible
Suggestion: Adjust budget OR destination OR constraints.
```

## Integration Notes

### Calls Before This Step
- None (this is the first sub-skill in the harness)

### Calls After This Step
- `sub-framework-selector` (uses profile to select methods)
- `sub-scoring-engine` (uses interests, pace, constraints for scoring)

### Data Passed Forward
- `trip_profile.party.pace_category` → framework selector (activity caps)
- `trip_profile.interests.mapped_categories` → scoring engine (experience match)
- `trip_profile.constraints.*` → improvement roadmap (constraint-aware routing)
- `trip_profile.fixed_elements` → improvement roadmap (routing anchors)
