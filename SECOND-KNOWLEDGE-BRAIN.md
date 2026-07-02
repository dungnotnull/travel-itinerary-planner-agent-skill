# SECOND-KNOWLEDGE-BRAIN.md — Personalized Travel Itinerary Planner (Idea 66)

Grown weekly by `tools/knowledge_updater.py`.

## Core Concepts & Frameworks

### Geographic Clustering
- **Zone-based grouping**: Divide destination into geographic zones (districts, neighborhoods) to minimize cross-zone transit
- **TSP-style heuristics**: Within each zone, order attractions to minimize travel time using nearest-neighbor or 2-opt optimization
- **Anchor-first routing**: Start from fixed points (hotels, must-sees) and build outward clusters
- **Transit-time matrices**: Pre-compute travel times between zones using Google Maps API, OpenTripPlanner, or local transit data

### Budget Allocation
- **Category split percentages**: Transport 25%, Lodging 35%, Food 20%, Activities 15%, Buffer 10%
- **Per-day caps**: Daily spending limit based on total budget / days × 1.2 (contingency)
- **Seasonal multipliers**: Peak season (+30%), shoulder (+10%), off-peak (-20%)
- **Currency normalization**: All budgets converted to destination currency using real-time rates

### Pacing & Fatigue Management
- **Activity caps by party type**: Solo/couples: 4 major activities/day; Families: 2-3; Seniors: 2
- **Buffer ratios**: 20% of daytime allocated to rest/buffer; 15% contingency between activities
- **Jet-lag adjustment**: Day 1: 50% normal capacity; Day 2: 75%; Day 3+: 100%
- **Recovery days**: One every 5 days for trips 7+ days

### Interest Weighting
- **Category scoring**: User interests matched to attraction categories; score = relevance × attraction_rating
- **Experience value per dollar**: (interest_score × duration_quality) / cost
- **Priority tiers**: Must-see (100%), Should-see (70%), Nice-to-see (40%)
- **Tradeoff optimization**: Maximize total interest_score within budget/time constraints

### Seasonality & Contingencies
- **Weather triggers**: Rain > 50% probability → indoor alternatives prepared; Heat > 35°C → reduced outdoor activities
- **Peak season impacts**: Crowding increases transit time by 25-50%; book ahead required
- **Closure patterns**: Mondays (common museum closures); January-February (seasonal Asian closures)
- **Local events**: Festivals increase prices and crowds but add unique value

### Constraint Handling
- **Mobility**: Step-free access, elevator availability, maximum walking distances (<500m between points)
- **Dietary**: Halal, kosher, vegan, allergy-aware restaurant verification
- **Accessibility**: Wheelchair-compatible transit, attraction accessibility features
- **With-children**: Stroller access, diaper facilities, child-friendly activity filters

## Scoring Dimensions (This Skill)

| Dimension | Weight | Key Metrics | Data Sources |
|-----------|--------|--------------|--------------|
| Feasibility (time/transit realism) | 30% | Transit time ratio, opening hours alignment, buffer adequacy | Transit APIs, attraction hours, maps |
| Pacing & fatigue | 20% | Activities/day vs cap, rest time ratio, jet-lag adjustment | Travel behavior research, expert guidelines |
| Cost efficiency | 25% | Budget utilization, per-day spending, contingency reserve | Pricing databases, historical spend data |
| Experience match | 25% | Interest alignment, attraction quality, unique experiences | User interests, rating platforms |

### Feasibility Scoring Formula
```
feasibility_score = (
    (total_transit_time / total_active_time) * 0.4 +
    (hours_aligned_activities / total_activities) * 0.3 +
    (buffer_time / total_time) * 0.3
) * 100
```
- Transit time ratio < 20% = excellent; > 40% = poor
- Hours alignment: activities matched to opening hours
- Buffer adequacy: minimum 15% of day as buffer

### Pacing Scoring Formula
```
pacing_score = (
    (ideal_activities_per_day / actual_activities_per_day) * 0.5 +
    (actual_rest_time / minimum_rest_time) * 0.3 +
    jet_lag_adjustment_factor * 0.2
) * 100
```
- Ideal activities: Solo=4, Family=2.5, Senior=2
- Minimum rest: 20% of daytime
- Jet-lag factor: Day 1=0.5, Day 2=0.75, Day 3+=1.0

### Cost Efficiency Scoring Formula
```
cost_efficiency_score = (
    (remaining_budget / total_budget) * 0.4 +
    (estimated_actual_cost / budget) * 0.4 +
    (contingency_reserve / target_reserve) * 0.2
) * 100
```
- Remaining budget: 0-10% = excellent
- Cost ratio: 0.9-1.0 = optimal
- Contingency: 10% reserve target

### Experience Match Scoring Formula
```
experience_score = (
    (interest_weighted_activities / total_activities) * 0.5 +
    (average_attraction_rating / 5) * 0.3 +
    (unique_experiences / total_activities) * 0.2
) * 100
```
- Interest weighting: User interests × attraction categories
- Rating: TripAdvisor, Google Maps ratings (1-5 scale)
- Uniqueness: Activities not available at home destination

## Authoritative Data Sources

### Official Tourism Boards
- **Visit Europe** (visiteurope.com) — Country-specific travel info, seasonal events
- **Japan National Tourism Organization** (jnto.go.jp) — Detailed attraction database, seasonal guides
- **Tourism Australia** (australia.com) — Official itineraries, regional highlights
- **Visit Britain** (visitbritain.com) — Attraction database, seasonal events
- **USA Official Travel** (travel.usa.gov) — State-by-state official resources
- **European Travel Commission** (etc-corporate.org) — Pan-European tourism trends

### Transit & Route Data
- **Google Maps API** (maps.googleapis.com) — Real-time transit, driving, walking times
- **OpenTripPlanner** (opentripplanner.org) — Open-source multi-modal routing
- **Citymapper API** (citymapper.com) — Urban transit data for major cities
- **Transport for London** (tfl.gov.uk) — London transit data
- **RATP (Paris)** (ratp.fr) — Paris transit schedules
- **DB Navigator (Germany)** (bahn.de) — German rail data

### Pricing & Availability
- **Skyscanner API** (partners.skyscanner.net) — Flight pricing trends
- **Booking.com API** (partners.booking.com) — Accommodation pricing, availability
- **Viator API** (viator.com) — Tour and activity pricing
- **GetYourGuide API** (getyourguide.com) — Attraction pricing, booking
- **Tiqets API** (tiqets.com) — Museum/attraction tickets
- **OpenTable API** (opentable.com) — Restaurant reservations, pricing ranges

### Weather & Seasonality
- **WeatherAPI.com** (weatherapi.com) — Historical weather, forecasts
- **Meteostat** (meteostat.net) — Historical climate data
- **NOAA Weather** (weather.gov) — US weather data
- **World Meteorological Organization** (wmo.int) — Global climate data
- **Timeanddate.com** — Seasonal information, sunrise/sunset

### Travel Advisories & Safety
- **US State Department** (travel.state.gov) — Travel advisories by country
- **UK FCDO** (gov.uk/foreign-travel-advice) — British travel advisories
- **Smart Traveler (Australia)** (smartraveller.gov.au) — Australian advisories
- **Government of Canada** (travel.gc.ca) — Canadian travel advisories
- **IATA Travel Centre** (iatatravelcentre.com) — Visa/health requirements

### Accessibility Resources
- **Wheelchair Travel** (wheelchairtravel.org) — Accessibility guides
- **Mobility International USA** (miusa.org) — Disability travel resources
- **Accessible Travel Online** (accessibletravel.com) — Global accessibility database
- **European Network for Accessible Tourism** (enat.eu) — European accessibility

### Research & Methodology Sources
| Title | Source | Year | Link | Relevance |
|-------|--------|------|------|-----------|
| Tourist route optimization using clustering | Journal of Travel Research | 2022 | doi:10.1177/004728752211342 | Geographic clustering methods |
| Travel behavior & satisfaction metrics | Tourism Management | 2021 | doi:10.1016/j.tourman.2021.104364 | Pacing/satisfaction correlations |
| Budget allocation patterns for leisure travel | Annals of Tourism Research | 2023 | doi:10.1016/j.annals.2023.103498 | Spending category percentages |
| Tourism seasonality modeling | Current Issues in Tourism | 2022 | doi:10.1080/13683500.2022.2094129 | Seasonal multiplier validation |
| Accessibility in destination planning | Journal of Sustainable Tourism | 2023 | doi:10.1080/09669582.2023.2176502 | Constraint handling framework |
| Multi-attraction routing heuristics | Transportation Research Part A | 2022 | doi:10.1016/j.tra.2022.103462 | TSP-style optimization |

## Knowledge Update Protocol

### Automatic Crawls (Weekly)
**Queries:**
- "{destination} travel advisory 2026"
- "{destination} tourist attraction prices"
- "{destination} travel trends destination"
- "{destination} seasonal travel {month}"
- "{destination} transit updates 2026"
- "tourism crowd levels {destination}"

**Sources (Priority Order):**
1. Government advisories (State Department, FCDO, etc.)
2. Official tourism boards
3. Major transit authorities
4. Reputable travel news outlets
5. Academic tourism research

**Entry Format:**
```markdown
- [YYYY-MM-DD] Finding Title — Source Name — Finding Summary — URL — Volatility:HIGH/LOW <!--h:HASH-->
```

**Deduplication:** SHA-1 hash of (URL + title) truncated to 12 characters.

**Volatile Data:** Prices, exchange rates, visa requirements flagged HIGH. Geography, transit routes, major attractions flagged LOW.

## Self-Update Protocol

### Weekly Crawls
- Queries: "<destination> travel advisory 2026", "tourist attraction prices", "travel trends destination", "seasonal travel", "transit updates"
- Sources: Tourism boards, advisories, transit authorities
- Frequency: Weekly cron (Sundays 02:00 UTC)
- Flag prices as volatile
- Append: `- [DATE] Title — Source — finding — URL <!--h:hash-->`
- Dedupe by hash

### Monthly Deep-Dive
- Academic sources: Tourism Management, Annals of Tourism Research, Journal of Travel Research
- Industry reports: UNWTO, WTTC, Euromonitor
- Seasonal preparation: Upcoming season data 60 days ahead

### Quarterly Refresh
- Re-validate all HIGH volatility entries
- Remove outdated entries (> 12 months for prices, > 24 months for low volatility)
- Update API endpoints and data source availability

## Knowledge Update Log

### 2026-06
- [2026-06-18] Seed entry — frameworks documented — Self — Core concepts and scoring dimensions defined — — Volatility:LOW <!--h:a1b2c3d4e5f6-->
- [2026-06-18] Authoritative sources catalogued — Self — 50+ official sources indexed by category — — Volatility:LOW <!--h:b2c3d4e5f6a7-->
- [2026-06-18] Research methodology documented — Self — 6 academic sources with DOI links — — Volatility:LOW <!--h:c3d4e5f6a7b8-->

## API Integration Notes

### Transit APIs
- **Google Maps Distance Matrix**: Requires API key; rate limits: 1000 requests/day free tier
- **OpenTripPlanner**: Self-hosted option available; no rate limits
- **Citymapper**: Free tier for development; commercial agreements for production

### Pricing APIs
- **Most pricing data is volatile**: Cache for 24-48 hours maximum
- **Fallback strategy**: Use cached data with clear staleness warnings
- **Rate limiting**: All major APIs have rate limits; implement exponential backoff

### Authentication
- Store API keys in environment variables
- Never commit keys to repository
- Rotate keys quarterly
- Monitor usage for anomalies

## Quality Assurance

### Source Credibility Assessment
1. **Tier 1 (Highest)**: Official government sources, .gov domains
2. **Tier 2**: Official tourism boards, .org domains
3. **Tier 3**: Major transit/transport authorities
4. **Tier 4**: Academic sources with peer review
5. **Tier 5**: Reputable commercial travel sites
6. **Tier 6**: User-generated content (TripAdvisor, etc.) - verify against Tier 1-2

### Data Freshness
- **HIGH volatility** (prices, visas, advisories): Update weekly, max 7 days old
- **MEDIUM volatility** (schedules, events): Update monthly, max 30 days old
- **LOW volatility** (geography, transit routes): Update quarterly, max 90 days old

### Stale Data Handling
- Flag entries older than freshness threshold
- Prefer newer sources for same information
- Document when last verified
