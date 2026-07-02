# Contributing to Travel Itinerary Planner

Thank you for your interest in contributing! This document outlines the standards and processes for contributing to this project.

## Code Standards

### Production-Grade Requirements

This is a production-ready, open-source project. All contributions must meet these standards:

1. **No Dummy Code**
   - All code must be functional and complete
   - No TODO comments in production code paths
   - No placeholder functions
   - All algorithms fully implemented

2. **No Comment-Only Implementations**
   - Code should be self-documenting
   - Comments explain WHY, not WHAT
   - No commented-out code in final submissions
   - If it's not needed, remove it

3. **Citation Requirements**
   - All methodology must cite sources (SECOND-KNOWLEDGE-BRAIN.md)
   - Prices must be dated (YYYY-MM-DD format)
   - Research claims need DOI-backed citations
   - APIs and data sources must be credited

4. **Error Handling**
   - All user-facing errors have clear, actionable messages
   - Graceful degradation for missing external data
   - No silent failures
   - Validation at system boundaries

## Testing Requirements

### All Test Scenarios Must Pass

Before submitting any changes:

```bash
# Verify all scenarios pass
python tests/run_scenarios.py --all

# Expected: 6/6 PASS (100%)
```

The six test scenarios:
1. Budget city trip (geographic clustering, budget adherence)
2. Family low-fatigue (pacing constraints)
3. Interest-weighted (experience scoring)
4. Infeasible budget (rescope behavior)
5. Rainy-day alternatives (contingencies)
6. Offline mode (degradation)

### Adding New Test Scenarios

When adding features:
1. Create new scenario in `tests/test-scenarios.md`
2. Include: input data, expected outputs, verification criteria
3. Must pass before merge
4. Update test coverage in README

## Documentation Requirements

### Sub-Skill Documentation

Each sub-skill (`.md` file in `skills/`) must include:

1. **Purpose** — Clear, one-sentence objective
2. **Inputs** — All required and optional parameters with types
3. **Process** — Step-by-step algorithm with code examples
4. **Outputs** — Structured output with field definitions
5. **Quality Gates** — Required, recommended, and validated criteria
6. **Error Handling** — Common errors and responses
7. **Integration Notes** — Calls before/after, data passed forward

### Knowledge Base Updates

When adding to `SECOND-KNOWLEDGE-BRAIN.md`:

1. **Sources** — Only authoritative sources (Tier 1-3)
   - Tier 1: .gov domains, official sources
   - Tier 2: Official tourism boards, .org domains
   - Tier 3: Major transit/transport authorities

2. **Research** — Academic sources with DOI
   - Peer-reviewed tourism research
   - Published within 5 years preferred
   - Include findings and relevance

3. **Entry Format**
   ```markdown
   - [YYYY-MM-DD] Title — Source — Summary — URL — Volatility:HIGH/LOW <!--h:HASH-->
   ```

### API Documentation

When adding API integrations:

1. Document rate limits
2. Store keys in environment variables
3. Include fallback strategies
4. Document authentication flow
5. Note data freshness requirements

## Pull Request Process

### Before Submitting

1. **Update Tests**
   - Add test case for new feature
   - All existing tests must pass
   - Update test coverage in README

2. **Update Documentation**
   - Update relevant sub-skill docs
   - Update SECOND-KNOWLEDGE-BRAIN.md if adding sources
   - Update README.md if user-facing feature

3. **Code Review Checklist**
   - [ ] No dummy or placeholder code
   - [ ] All code paths implemented
   - [ ] Error handling complete
   - [ ] Prices/volatile data dated
   - [ ] Sources cited
   - [ ] Comments explain WHY only
   - [ ] No commented-out code

### Pull Request Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
- [ ] All 6 test scenarios pass
- [ ] New test cases added (if applicable)
- [ ] Manual testing completed

## Documentation
- [ ] Sub-skill docs updated
- [ ] Knowledge base updated (if applicable)
- [ ] README updated (if user-facing)

## Checklist
- [ ] Code is production-ready (no dummy code)
- [ ] All sources cited
- [ ] Prices/volatile data dated
- [ ] Error handling complete
- [ ] Offline degradation considered
```

## Development Workflow

### Setting Up Development Environment

```bash
# Clone repository
git clone <repository-url>
cd travel-itinerary-planner

# Verify structure
ls skills/  # Should see: main.md and 4 sub-skills
ls tools/   # Should see: knowledge_updater.py
ls tests/   # Should see: test-scenarios.md

# Run tests
python tests/run_scenarios.py --all
```

### Making Changes

1. **Create feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement changes**
   - Follow code standards above
   - Add/update tests
   - Update documentation

3. **Local verification**
   ```bash
   # Run all tests
   python tests/run_scenarios.py --all

   # Check documentation
   # Verify all .md files are well-formatted
   ```

4. **Submit pull request**
   - Include clear description
   - Reference any related issues
   - Complete PR template

## Knowledge Base Contribution

### Adding Authoritative Sources

When adding new data sources to SECOND-KNOWLEDGE-BRAIN.md:

1. **Verify source authority**
   - Official government/tourism board preferred
   - Check domain: .gov, .org, official tourism sites
   - Verify content is current

2. **Format entry correctly**
   ```markdown
   ### Source Category
   **Source Name** (URL) — Brief description — Volatility:HIGH/LOW
   ```

3. **Add to appropriate section**
   - Official Tourism Boards
   - Transit & Route Data
   - Pricing & Availability
   - Weather & Seasonality
   - Travel Advisories
   - Accessibility Resources

4. **Update crawler** (if applicable)
   - Add to SOURCES list in tools/knowledge_updater.py
   - Include fetch logic for source structure

### Adding Research Citations

When adding academic research:

1. **Verify publication quality**
   - Peer-reviewed journal preferred
   - DOI available
   - Recent (5 years) preferred

2. **Format citation**
   ```markdown
   | Title | Source | Year | DOI | Relevance |
   |-------|--------|------|-----|-----------|
   | Paper Title | Journal | YYYY | doi:XXXX | Brief finding |
   ```

3. **Document relevance**
   - How it informs methodology
   - Which framework it supports
   - Key findings applicable to itinerary planning

## Issues and Bug Reports

### Reporting Issues

When reporting issues, include:

1. **Scenario details**
   - Destination
   - Budget
   - Party composition
   - Expected vs actual behavior

2. **Environment**
   - Offline vs online mode
   - Which test scenarios fail
   - Error messages

3. **Steps to reproduce**
   - Input data
   - Expected output
   - Actual output

### Issue Template

```markdown
## Scenario
- Destination: [city, country]
- Budget: [amount, currency]
- Party: [description]

## Expected Behavior
[What should happen]

## Actual Behavior
[What actually happened]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Environment
- Offline mode: [yes/no]
- Test scenarios affected: [list]

## Additional Context
[Logs, screenshots, etc.]
```

## Code Review Criteria

Pull requests are reviewed against:

1. **Code Quality**
   - Production-ready implementation
   - No dummy/placeholder code
   - Clear, self-documenting code
   - Appropriate error handling

2. **Testing**
   - All scenarios pass
   - New features have tests
   - Edge cases covered

3. **Documentation**
   - Sub-skill docs complete
   - Knowledge base updated
   - README current

4. **Citations**
   - Sources cited for methodology
   - Prices dated
   - APIs credited

## Community Guidelines

### Be Respectful
- Constructive feedback only
- Assume good intentions
- Credit contributors

### Ask Questions
- Use issues for questions
- Label appropriately (question, enhancement, bug)
- Provide context

### Share Knowledge
- Document learnings in SECOND-KNOWLEDGE-BRAIN.md
- Share useful sources
- Contribute test scenarios

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md (when created)
- Release notes
- Git commit history (proper attribution)

## License

Contributions are licensed under the same MIT License as the project. By submitting, you agree that your contributions can be licensed under MIT.

---

Thank you for contributing to the Travel Itinerary Planner!
