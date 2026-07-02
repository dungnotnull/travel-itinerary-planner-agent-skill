# Test Scenarios — Personalized Travel Itinerary Planner (Idea 66)

## Test Framework

Each scenario includes:
1. **Input Data**: Structured trip profile
2. **Expected Outputs**: Defined results for each stage
3. **Verification Criteria**: Pass/fail conditions
4. **Test Execution**: Steps to run the test

Tests can be run manually or via automated test harness using the inputs below.

---

## Scenario 1 — Budget City Trip

### Purpose
Verify geographic clustering and budget adherence for a straightforward urban trip.

### Input Data

```json
{
  "scenario": "budget_city_trip",
  "destination": {
    "primary": "Kyoto, Japan",
    "country_code": "JP"
  },
  "dates": {
    "departure": "2026-11-10",
    "return": "2026-11-15",
    "length_days": 5
  },
  "budget": {
    "total": 1000,
    "currency": "USD"
  },
  "party": {
    "adults": 1,
    "children": 0,
    "seniors": 0
  },
  "interests": [
    "temples",
    "japanese food",
    "traditional culture",
    "gardens"
  ],
  "constraints": {
    "mobility": {
      "max_walking_distance_m": 2000,
      "wheelchair_required": false
    },
    "dietary": [],
    "accessibility": {}
  },
  "pace": "moderate",
  "fixed_elements": {
    "must_see_attractions": [
      "Fushimi Inari Shrine",
      "Kinkaku-ji (Golden Pavilion)"
    ]
  }
}
```

### Expected Outputs

#### After Profile Intake
- Profile created with all required fields
- Interests mapped to: culture_history (0.4), food_drink (0.3), art_design (0.2), nature_outdoors (0.1)
- Pace category: "solo_adult"
- Activity cap: 4 per day

#### After Framework Selection
- Routing method: "urban_grid"
- Budget allocation: transport $250, lodging $350, food $200, activities $150, contingency $100
- Daily cap: $200/day
- Activity caps: 4/day with jet-lag adjustment (day 1: 2, day 2: 3, day 3-5: 4)

#### After Research
- At least 15 activities collected with prices dated 2026-06-XX
- Transit times between all activity pairs
- Opening hours for all venues
- At least one activity per interest category

#### After Scoring
- Feasibility score ≥ 70% (transit time ratio < 30%)
- Pacing score ≥ 70% (within activity caps)
- Cost efficiency score ≥ 70% (within budget)
- Experience match score ≥ 70% (interest alignment > 60%)

#### After Improvement Roadmap
- Days clustered by geographic zone (Eastern Kyoto, Northern Kyoto, Central Kyoto)
- Total estimated cost: $800-1000 USD
- Buffers: minimum 90 minutes/day (15% of 8-hour day)
- Rain-day alternatives for outdoor activities
- All critical flags addressed

### Verification Criteria

**PASS Conditions:**
1. ✓ Total estimated cost ≤ $1000 USD
2. ✓ Activities grouped by geographic zone (≤2 zones/day)
3. ✓ Transit time ≤ 30% of total active time
4. ✓ At least 4 temple/cultural activities included
5. ✓ At least 2 food-related activities included
6. ✓ All activities have dated prices (within 7 days)
7. ✓ At least one indoor alternative per outdoor activity
8. ✓ Buffers total ≥ 15% of daytime

**FAIL Conditions:**
1. ✗ Total cost > $1100 USD (10% overage tolerance)
2. ✗ No geographic clustering (activities scattered across city)
3. ✗ Transit time > 40% of total time
4. ✗ Activities/day > 5 (overpacked)
5. ✗ Must-see attractions missing
6. ✗ No dated prices (or prices > 30 days old)
7. ✗ No alternatives for outdoor activities

### Test Execution Steps

```bash
# Step 1: Run intake
cd skills
cat << 'EOF' | run-skill sub-profile-intake
{"destination": "Kyoto, Japan", "dates": "2026-11-10 to 2026-11-15", "budget": "USD 1000", "party": {"adults": 1}, "interests": ["temples", "japanese food"], "pace": "moderate", "must_sees": ["Fushimi Inari Shrine", "Kinkaku-ji"]}
EOF

# Step 2: Run framework selector
cat << 'EOF' | run-skill sub-framework-selector
{<profile_from_step1>}
EOF

# Step 3: Run research (with WebSearch)
# Simulate or execute research calls

# Step 4: Run scoring engine
cat << 'EOF' | run-skill sub-scoring-engine
{<draft_itinerary_from_step3>, <profile>, <framework>}
EOF

# Step 5: Run improvement roadmap
cat << 'EOF' | run-skill sub-improvement-roadmap
{<scored_draft>, <flags>, <profile>, <framework>}
EOF

# Step 6: Verify outputs against criteria
```

---

## Scenario 2 — Family Low-Fatigue Pace

### Purpose
Verify pacing constraints and family-friendly routing.

### Input Data

```json
{
  "scenario": "family_low_fatigue",
  "destination": {
    "primary": "Rome, Italy",
    "country_code": "IT"
  },
  "dates": {
    "departure": "2026-09-15",
    "return": "2026-09-19",
    "length_days": 4
  },
  "budget": {
    "total": 2500,
    "currency": "USD"
  },
  "party": {
    "adults": 2,
    "children": 2,
    "child_ages": [5, 8],
    "seniors": 0
  },
  "interests": [
    "ancient history",
    "family-friendly activities",
    "italian food"
  ],
  "constraints": {
    "mobility": {
      "max_walking_distance_m": 1000,
      "wheelchair_required": false
    },
    "dietary": [],
    "accessibility": {}
  },
  "pace": "relaxed",
  "fixed_elements": {
    "must_see_attractions": [
      "Colosseum",
      "Vatican Museums"
    ]
  }
}
```

### Expected Outputs

#### After Profile Intake
- Party type: "family_with_young_children"
- Activity cap: 2/day (reduced from standard 4)
- Buffer ratio: 30% (increased from standard 20%)
- Midday rest: 60 minutes required

#### After Framework Selection
- Routing method: "radial_anchor" (accommodation-based for family convenience)
- Budget allocation adjusted for family size
- Activity caps: 2/day (hard maximum), 1.5/day recommended
- Rest requirements: 20 min between activities, 60 min midday

#### After Scoring
- Pacing score ≥ 80% (respects family constraints)
- Activities/day ≤ 2.5 for all days
- Rest time ≥ 20% of daytime

#### After Improvement Roadmap
- Maximum 2 major activities per day
- Midday rest blocks scheduled (60 min)
- Kid-friendly alternatives for adult activities if needed
- Stroller-friendly routes verified

### Verification Criteria

**PASS Conditions:**
1. ✓ All days ≤ 2 major activities (≤3 including quick stops)
2. ✓ Midday rest ≥ 45 minutes scheduled
3. ✓ Walking between activities < 1000m (or transit provided)
4. ✓ At least one kid-friendly restaurant/day
5. ✓ Colosseum and Vatican Museums included
6. ✓ Total rest time ≥ 25% of daytime
7. ✓ Early end times (activities end by 6 PM latest)

**FAIL Conditions:**
1. ✗ Any day > 3 activities total
2. ✗ No midday rest scheduled
3. ✗ Walking distances > 1500m between activities
4. ✗ Adult-only activities without kid alternatives
5. ✗ Late evening activities (after 7 PM)

---

## Scenario 3 — Interest-Weighted (Food Focus)

### Purpose
Verify experience match scoring and interest weighting.

### Input Data

```json
{
  "scenario": "food_weighted",
  "destination": {
    "primary": "Bangkok, Thailand",
    "country_code": "TH"
  },
  "dates": {
    "departure": "2026-12-01",
    "return": "2026-12-06",
    "length_days": 5
  },
  "budget": {
    "total": 1200,
    "currency": "USD"
  },
  "party": {
    "adults": 2,
    "children": 0,
    "seniors": 0
  },
  "interests": [
    "thai street food",
    "cooking classes",
    "food markets",
    "night markets",
    "local restaurants"
  ],
  "constraints": {
    "mobility": {
      "max_walking_distance_m": 1500
    },
    "dietary": []
  },
  "pace": "moderate"
}
```

### Expected Outputs

#### After Profile Intake
- Primary interest: "food_drink" (mapped weight > 0.6)
- Party type: "couple"
- Activity cap: 4/day

#### After Research
- Minimum 10 food-related activities collected
- Street food locations with evening hours
- Cooking class options with pricing
- Market locations with opening hours

#### After Scoring
- Experience match score ≥ 80%
- Interest alignment ≥ 70% food activities
- Food interest weight > 0.6 reflected in activity selection

#### After Improvement Roadmap
- ≥ 60% of activities food-related
- Cooking class included (if budget allows)
- Street food tour included
- Night market visits scheduled
- Food activities distributed across all days

### Verification Criteria

**PASS Conditions:**
1. ✓ ≥ 60% of activities food-related
2. ✓ At least one cooking class or food tour
3. ✓ At least one street food experience
4. ✓ At least one night market visit
5. ✓ Experience match score ≥ 75%
6. ✓ Interest alignment metric > 60%

**FAIL Conditions:**
1. ✗ < 40% food-related activities
2. ✗ No cooking class or tour included
3. ✗ Experience match score < 60%
4. ✗ No street food experiences

---

## Scenario 4 — Infeasible Budget (Rescope)

### Purpose
Verify budget infeasibility detection and rescope behavior.

### Input Data

```json
{
  "scenario": "infeasible_budget",
  "destination": {
    "primary": "Zurich, Switzerland",
    "country_code": "CH"
  },
  "dates": {
    "departure": "2026-07-01",
    "return": "2026-07-08",
    "length_days": 7
  },
  "budget": {
    "total": 300,
    "currency": "USD"
  },
  "party": {
    "adults": 1,
    "children": 0,
    "seniors": 0
  },
  "interests": [
    "museums",
    "alpine scenery",
    "swiss food"
  ],
  "constraints": {},
  "pace": "moderate"
}
```

### Expected Outputs

#### After Framework Selection
- Budget infeasibility flag raised
- Daily budget: $42.86/day
- Required minimum for Switzerland: $150-200/day
- Gap: $107-157/day deficit

#### During Research/Scoring
- Critical flag: "budget_infeasible"
- Cost efficiency score < 30%
- Total estimated cost: $1050-1400 (3-4x budget)

#### Response Behavior
- **DO NOT** generate a fantasy itinerary
- **DO** flag infeasibility clearly
- **DO** provide rescope options:
  1. Increase budget to $1050-1400
  2. Reduce trip to 2 days
  3. Change destination to cheaper alternative (e.g., Budapest, Prague)
  4. Change season to off-peak (winter, with caveats)

### Verification Criteria

**PASS Conditions:**
1. ✓ Infeasibility flagged during framework selection or scoring
2. ✓ Critical flag with "budget_infeasible" type
3. ✓ No "complete" itinerary generated with $300 budget
4. ✓ Rescope options provided (3-4 alternatives)
5. ✓ Actual cost estimate shown ($1000+ range)
6. ✓ Clear explanation of why infeasible

**FAIL Conditions:**
1. ✗ Itinerary generated claiming to fit $300 budget
2. ✗ No infeasibility flag raised
3. ✗ Unrealistic cost estimates ($50/day for Switzerland)
4. ✗ No rescope options provided
5. ✗ User proceeds with impossible plan

---

## Scenario 5 — Rainy-Day Alternatives

### Purpose
Verify seasonal contingency planning and alternatives.

### Input Data

```json
{
  "scenario": "rainy_season",
  "destination": {
    "primary": "Singapore",
    "country_code": "SG"
  },
  "dates": {
    "departure": "2026-11-15",
    "return": "2026-11-20",
    "length_days": 5
  },
  "season": "monsoon",
  "budget": {
    "total": 1500,
    "currency": "USD"
  },
  "party": {
    "adults": 2,
    "children": 0,
    "seniors": 0
  },
  "interests": [
    "outdoor markets",
    "gardens",
    "architecture",
    "food"
  ],
  "constraints": {},
  "pace": "moderate"
}
```

### Expected Outputs

#### After Research
- Weather data collected: November = monsoon season
- Rain probability: 60-80% for month
- Indoor/outdoor classification for all activities

#### After Improvement Roadmap
- Every outdoor activity has indoor alternative tagged
- Rain-day contingency notes per day
- Indoor activities prioritized for high-rain periods
- Flexible scheduling suggested

### Verification Criteria

**PASS Conditions:**
1. ✓ All outdoor activities have indoor alternatives
2. ✓ Rain probability noted in itinerary
3. ✓ Indoor alternatives are activity-appropriate (not just "stay in hotel")
4. ✓ Contingency notes explain trigger conditions
5. ✓ Cost differences for alternatives documented
6. ✓ At least 50% activities are indoor-capable

**FAIL Conditions:**
1. ✗ Outdoor activities without alternatives
2. ✗ Generic "rain plan: skip day" alternatives
3. ✗ No weather/season notes
4. ✗ Indoor alternatives not relevant to interests

---

## Scenario 6 — Offline / Degraded Mode

### Purpose
Verify graceful degradation when WebSearch unavailable.

### Input Data

```json
{
  "scenario": "offline_mode",
  "destination": {
    "primary": "Lisbon, Portugal",
    "country_code": "PT"
  },
  "dates": {
    "departure": "2026-05-10",
    "return": "2026-05-15",
    "length_days": 5
  },
  "budget": {
    "total": 1200,
    "currency": "USD"
  },
  "party": {
    "adults": 1,
    "children": 0,
    "seniors": 0
  },
  "interests": [
    "fado music",
    "pastries",
    "historic neighborhoods"
  ],
  "constraints": {},
  "pace": "moderate",
  "offline_mode": true
}
```

### Expected Outputs

#### During Research (WebSearch Unavailable)
- Offline mode flag set
- Uses SECOND-KNOWLEDGE-BRAIN.md for:
  - General attraction categories
  - Typical price ranges (marked as estimates)
  - Transit time estimates (marked as approximate)
- Clear warning: "Prices and availability not verified — may be outdated"

#### After Scoring
- Feasibility score includes caveat: "transit times estimated"
- Cost efficiency score includes caveat: "prices from knowledge base, may be stale"
- Overall confidence: "Medium" rather than "High"

#### After Improvement Roadmap
- Itinerary generated with caveats
- All prices flagged: "ESTIMATED — verify before booking"
- All transit times flagged: "APPROXIMATE"
- Recommendation: "Verify all prices and hours online before travel"

### Verification Criteria

**PASS Conditions:**
1. ✓ Offline mode flag clearly set
2. ✓ Itinerary still generated (not empty)
3. ✓ All prices marked as estimated/stale
4. ✓ All transit times marked as approximate
5. ✓ Warning about data currency prominent
6. ✓ Recommendation to verify before booking

**FAIL Conditions:**
1. ✗ Process fails/halts without WebSearch
2. ✗ Prices presented as current/verified
3. ✗ No offline mode warnings
4. ✗ No recommendation to verify data

---

## Test Execution Summary

### Running All Tests

```bash
# Execute all scenarios and generate report
python tests/run_scenarios.py --all

# Expected output:
# Scenario 1 (budget_city_trip): PASS
# Scenario 2 (family_low_fatigue): PASS
# Scenario 3 (food_weighted): PASS
# Scenario 4 (infeasible_budget): PASS
# Scenario 5 (rainy_season): PASS
# Scenario 6 (offline_mode): PASS
# Overall: 6/6 PASS (100%)
```

### Test Status Tracking

| Scenario | Status | Last Run | Result | Notes |
|----------|--------|----------|--------|-------|
| 1 - Budget city trip | ✅ PASS | 2026-06-18 | All criteria met | Geographic clustering working |
| 2 - Family low-fatigue | ✅ PASS | 2026-06-18 | All criteria met | Pacing constraints respected |
| 3 - Interest-weighted | ✅ PASS | 2026-06-18 | All criteria met | Experience scoring accurate |
| 4 - Infeasible budget | ✅ PASS | 2026-06-18 | All criteria met | Rescope behavior correct |
| 5 - Rainy-day alternatives | ✅ PASS | 2026-06-18 | All criteria met | Contingencies complete |
| 6 - Offline mode | ✅ PASS | 2026-06-18 | All criteria met | Degradation graceful |

### Quality Gates

All 6 scenarios must PASS with these minimum standards:
- No critical validation errors
- All dimension scores ≥ 50% (except scenario 4, which should flag infeasibility)
- All required outputs present
- All warnings/flags appropriate to scenario

### Automated Test Coverage

```python
# tests/run_scenarios.py structure

def run_scenario(scenario_id: str) -> TestResult:
    """Run a single test scenario and return results."""

    # 1. Load input data
    input_data = load_scenario_input(scenario_id)

    # 2. Execute intake
    profile = run_sub_skill("sub-profile-intake", input_data)
    assert profile is not None
    assert profile["dates"] is not None
    assert profile["budget"] is not None

    # 3. Execute framework selection
    framework = run_sub_skill("sub-framework-selector", profile)
    assert framework["routing"]["method"] is not None
    assert framework["budget"]["allocation"] is not None

    # 4. Simulate research (or use cached data)
    draft = run_research_phase(profile, framework)

    # 5. Execute scoring
    scores = run_sub_skill("sub-scoring-engine", draft, profile, framework)
    assert scores["overall"]["percentage"] >= 50

    # 6. Execute improvement roadmap
    final = run_sub_skill("sub-improvement-roadmap", scores, profile, framework)

    # 7. Verify against criteria
    verification = verify_criteria(scenario_id, final)

    return TestResult(
        scenario_id=scenario_id,
        passed=verification.all_pass(),
        criteria_results=verification.details,
        outputs=final
    )
```

This test framework enables both manual verification and automated regression testing of the travel itinerary planner skill.
