# Complete Intelligence Extraction System

## What We Extract

The ingestion tool now extracts **8 layers of intelligence** from GitHub repositories:

### 1. ✅ Repository Metadata (Baseline)
Languages, size, activity, topics

### 2. ✅ Critical Files (Infrastructure DNA)
Dependencies, IaC, CI/CD configs, deployment files

### 3. ✅ PR Comment Intelligence
Confusion signals, tech debt acknowledgments, fragility mentions

### 4. ✅ Shadow Infrastructure Discovery
Actual workflows (Makefiles, scripts), environment complexity, workaround scripts

### 5. ✅ Commit Archaeology (NEW)
Deployment patterns, revert frequency, commit timing, cultural signals

### 6. ✅ Code Fear Indicators (NEW)
"DO NOT TOUCH" comments, frozen files, defensive code

### 7. ✅ Hidden Dependencies (NEW)
System dependencies, runtime fetches, external API calls

### 8. ✅ CI/CD Performance Analysis (NEW)
Workflow timing, failure rates, bottlenecks

### 9. ✅ Bus Factor Mapping (NEW)
Knowledge distribution, single points of failure, contributor analysis

## Real Results from gradestack Org

### stacops Repo
```json
{
  "commit_archaeology": {
    "total_commits": 9,
    "friday_deploys": 0,
    "weekend_activity": 0,
    "avg_commit_message_length": 121,
    "insights": [{
      "issue": "friday_deploy_avoidance",
      "description": "Very few Friday commits, suggesting deploy fear",
      "suggestion": "Build confidence with better testing and rollback procedures"
    }]
  },
  "ci_analysis": {
    "workflows": [{
      "name": "Scoring CI",
      "avg_duration_minutes": 1.1,
      "failure_rate": 0.43
    }],
    "insights": [{
      "issue": "flaky_ci_workflow",
      "severity": "high",
      "description": "Scoring CI: 43% failure rate",
      "suggestion": "High failure rate suggests flaky tests or environment issues"
    }]
  }
}
```

**Actionable Intelligence:**
- Team avoids Friday deployments (cultural fear)
- CI has 43% failure rate → flaky tests are blocking confidence
- Average commit message is decent (121 chars)
- No weekend work (good work-life balance)

### tfjson Repo
```json
{
  "shadow_infrastructure": {
    "makefile_targets": {
      "targets": ["build", "build-all", "test", "clean", "install", "run"],
      "uses_docker": false,
      "total_targets": 7
    },
    "workaround_scripts": {
      "scripts": [{"name": "install.sh", "location": "root"}]
    }
  },
  "hidden_dependencies": {
    "runtime_fetches": [{
      "file": "install.sh",
      "type": "shell_script"
    }],
    "insights": [{
      "issue": "runtime_fetches_detected",
      "description": "1 scripts with runtime fetches (curl/wget)",
      "suggestion": "Runtime fetches can fail and are hard to version"
    }]
  },
  "ci_analysis": {
    "workflows": [{
      "name": "Integration Tests",
      "failure_rate": 0.75
    }],
    "insights": [{
      "issue": "flaky_ci_workflow",
      "severity": "high",
      "description": "Integration Tests: 75% failure rate"
    }]
  }
}
```

**Actionable Intelligence:**
- Clean Go project with standard Makefile
- install.sh uses curl/wget (runtime dependency)
- Integration tests fail 75% of the time → major reliability issue
- Multi-platform build process (5 platforms)

## How This Enables Context-Aware AI

### Example 1: Test Reliability Problem

**Without Intelligence:**
```
User: "Improve our CI"
LLM: "Here's a PR to add more tests"
Result: ❌ More tests won't help if existing ones are flaky
```

**With Intelligence:**
```
Vector DB Context:
- Scoring CI: 43% failure rate
- Integration Tests: 75% failure rate
- Friday deploy avoidance detected

LLM: "I see your CI has high failure rates (43% in stacops, 75% in tfjson).
      This is likely causing Friday deploy avoidance. Here's a PR to:
      1. Add test retry logic for flaky tests
      2. Improve test isolation
      3. Add test timing analysis

      This will build confidence for Friday deployments."

Result: ✅ Addresses root cause with specific, actionable fixes
```

### Example 2: Runtime Dependencies

**Without Intelligence:**
```
User: "Make deployment more reliable"
LLM: "Use Docker"
Result: ❌ Generic suggestion
```

**With Intelligence:**
```
Vector DB Context:
- install.sh uses curl/wget for runtime fetches
- Shell script in root (workaround)

LLM: "Your install.sh has runtime fetches via curl. Here's a PR to:
      1. Vendor dependencies at build time
      2. Add checksums for security
      3. Add fallback URLs

      This eliminates runtime fetch failures."

Result: ✅ Specific to their actual infrastructure
```

### Example 3: Cultural Signals

**Without Intelligence:**
```
User: "Speed up deployments"
LLM: "Deploy more frequently"
Result: ❌ Doesn't address fear
```

**With Intelligence:**
```
Vector DB Context:
- 0 Friday commits (deploy avoidance)
- 43% CI failure rate
- No revert commits (good)

LLM: "You avoid Friday deploys, likely due to 43% CI failure rate.
      Rather than deploying faster, let's build confidence:
      1. Fix flaky tests first
      2. Add automated rollback testing
      3. Create staging environment parity checks

      Then Friday deploys become safe."

Result: ✅ Addresses psychological blocker, not just technical
```

## Feature Breakdown

### Commit Archaeology
**What it reveals:**
- Deployment patterns (when do they ship?)
- Revert frequency (how often do they break prod?)
- Weekend work (work-life balance issues?)
- Commit message quality (documentation culture?)

**Key metrics:**
- `friday_deploys`: Low = deploy fear
- `revert_commits`: High = stability issues
- `weekend_activity`: High = incident response or crunch time
- `avg_commit_message_length`: Low = poor documentation

### Code Fear Indicators
**What it reveals:**
- Sacred cow code (areas with "DO NOT TOUCH")
- Frozen files (not modified in years)
- Defensive coding (excessive try-catch)

**Key patterns:**
- `DO NOT TOUCH`, `DON'T CHANGE` → fear-based development
- `FRAGILE`, `DANGEROUS` → known brittle areas
- `XXX`, `HACK HACK` → technical debt acknowledgment

**Note:** GitHub code search API may be rate-limited. This feature has graceful degradation.

### Hidden Dependencies
**What it reveals:**
- System packages (apt-get, yum, apk)
- Runtime fetches (curl, wget in scripts)
- External APIs called from code

**Why it matters:**
- System deps = deployment complexity
- Runtime fetches = failure points
- External APIs = service dependencies

### CI/CD Performance Analysis
**What it reveals:**
- Workflow timing (where is time spent?)
- Failure rates (flaky tests?)
- Recent run history

**Key metrics:**
- `avg_duration_minutes`: >15 = slow CI
- `failure_rate`: >20% = flaky tests
- Workflow count: Many workflows = complexity

### Bus Factor Mapping
**What it reveals:**
- Knowledge distribution (who knows what?)
- Single points of failure (critical files with one owner)
- Contributor concentration (is knowledge in one person's head?)
- Organizational risk (bus factor = how many people before trouble?)

**Key metrics:**
- `estimated_bus_factor`: ≤2 = critical risk, 3-5 = moderate, 5+ = healthy
- `knowledge_concentration`: very_high/high = risky, medium/distributed = healthy
- `critical_sole_ownership`: Critical files (auth, payment, deploy) with single owners
- `sole_ownership_files`: Total files never touched by >1 person

**Real data from gradestack/stacops**:
- Bus factor: **2** (CRITICAL - losing 2 people = project crippled)
- Knowledge concentration: **very_high** (78% in one person - wlonk)
- Critical sole ownership: **106 files** (auth, config, CI/CD)
- Total sole ownership: **256 files** (never cross-trained)

This is your HIGHEST PRIORITY RISK. Before worrying about test flakiness or deploy speed, you need to spread knowledge. One person leaving could end the project.

## Output Structure

```json
{
  "metadata": { ... },
  "files": { ... },
  "structure": { ... },
  "pr_intelligence": {
    "confusion_signals": [...],
    "tech_debt_acknowledgments": [...],
    "fragility_mentions": [...]
  },
  "shadow_infrastructure": {
    "makefile_targets": {...},
    "npm_scripts": {...},
    "env_complexity": {...},
    "insights": [...]
  },
  "commit_archaeology": {
    "total_commits": 0,
    "commit_times": {...},
    "revert_commits": [...],
    "friday_deploys": 0,
    "weekend_activity": 0,
    "insights": [...]
  },
  "code_fear_indicators": {
    "sacred_cows": [...],
    "total_fear_signals": 0,
    "insights": [...]
  },
  "hidden_dependencies": {
    "system_dependencies": [...],
    "runtime_fetches": [...],
    "total_hidden_deps": 0,
    "insights": [...]
  },
  "ci_analysis": {
    "workflow_count": 0,
    "workflows": [...],
    "insights": [...]
  },
  "bus_factor": {
    "total_contributors": 0,
    "estimated_bus_factor": 0,
    "knowledge_concentration": "unknown",
    "contributors": [...],
    "sole_ownership_files": [...],
    "critical_sole_ownership": [...],
    "insights": [...]
  }
}
```

## Performance & Rate Limits

### API Calls Per Repo
- PR comments: ~3 calls per PR × 100 PRs = 300 calls
- Commit analysis: 1 call (200 commits)
- Code search: ~10 calls (may hit rate limit)
- CI workflows: ~15 calls (5 workflows × 3 calls each)
- File fetching: ~20 calls

**Total: ~350 API calls per repo**

With 5000/hour limit, can ingest ~14 repos per hour without issues.

### Graceful Degradation
- Code search fails → Skip fear indicators
- Workflow API unavailable → Skip CI analysis
- Rate limit hit → Continue with other features

## Future Enhancements

### Cultural Analysis
- Sentiment analysis on commit messages
- Author expertise mapping (who knows what)
- Response time in PR comments

### Bus Factor Mapping
- Knowledge distribution (git blame analysis)
- Single points of failure
- Expertise concentration

### Dependency Archaeology
- Parse CHANGELOGs to understand why stuck on old versions
- Breaking change analysis
- Upgrade difficulty estimation

### Cross-Repo Intelligence
- Code duplication across repos
- Config drift detection
- Migration patterns (moving from X to Y)
- Org-wide technology adoption

### Postmortem Mining
- Extract incident patterns
- Recurring root causes
- Incomplete action items

## Usage Tips

### For Small Teams (2-5 people)
Focus on:
- Shadow infrastructure (actual vs. documented workflows)
- CI performance (time is precious)
- Code fear (limited knowledge distribution)

### For Medium Teams (5-20 people)
Focus on:
- PR intelligence (communication patterns)
- Commit archaeology (deployment culture)
- Bus factor (knowledge silos)

### For Large Teams (20+ people)
Focus on:
- Cross-repo patterns (code duplication)
- Cultural signals (team health)
- Postmortem mining (recurring issues)
