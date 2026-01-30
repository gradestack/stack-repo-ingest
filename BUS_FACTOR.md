# Bus Factor Mapping

Maps knowledge distribution and identifies single points of failure in your codebase.

## What is Bus Factor?

**Bus factor** = the number of team members who need to get hit by a bus before the project is in serious trouble.

A bus factor of 1 means one person leaving would cripple the project.
A bus factor of 5+ means knowledge is well-distributed.

## What We Extract

### 1. Contributor Distribution
Who's contributing and how much?

```json
{
  "total_contributors": 3,
  "contributors": [
    {"login": "wlonk", "commits": 7},
    {"login": "dmonroy", "commits": 1},
    {"login": "mblhaunted", "commits": 1}
  ]
}
```

### 2. File Ownership Mapping
Who owns which files? (Derived from commit history)

```json
{
  "sole_ownership_files": [
    {
      "file": "scoring/scoring_engine/engine.py",
      "author": "Darwin Monroy",
      "commits": 1
    }
  ]
}
```

### 3. Critical File Analysis
Files with patterns like `auth`, `payment`, `security`, `deploy` owned by single contributors.

```json
{
  "critical_sole_ownership": [
    {
      "file": "auth/security.py",
      "author": "Alice",
      "commits": 5,
      "reason": "critical_pattern_match"
    }
  ]
}
```

### 4. Knowledge Concentration
How concentrated is knowledge in top contributors?

```json
{
  "knowledge_concentration": "very_high",  // or high, medium, distributed
  "estimated_bus_factor": 2
}
```

**Concentration levels:**
- `very_high`: Top contributor > 70% of commits
- `high`: Top contributor 50-70% of commits
- `medium`: Top contributor 30-50% of commits
- `distributed`: Top contributor < 30% of commits

### 5. Estimated Bus Factor
How many people need to leave before you lose 80% of knowledge?

## Real Results from gradestack Org

### 🔴 stacops - CRITICAL RISK

```json
{
  "total_contributors": 3,
  "estimated_bus_factor": 2,
  "knowledge_concentration": "very_high",
  "contributors": [
    {"login": "wlonk", "commits": 7},      // 78% of commits
    {"login": "dmonroy", "commits": 1},
    {"login": "mblhaunted", "commits": 1}
  ],
  "critical_sole_ownership": 106,  // 106 critical files, one owner each
  "total_sole_ownership": 256,      // 256 total files, one owner each
  "insights": [
    {
      "severity": "critical",
      "issue": "low_bus_factor",
      "description": "Bus factor of 2 - project highly vulnerable"
    },
    {
      "severity": "high",
      "issue": "critical_sole_ownership",
      "description": "106 critical files owned by single contributors"
    },
    {
      "severity": "high",
      "issue": "knowledge_concentration",
      "description": "very_high knowledge concentration detected"
    },
    {
      "severity": "medium",
      "issue": "many_sole_ownership_files",
      "description": "256 files owned by single contributors"
    }
  ]
}
```

**What This Means:**
- If wlonk leaves, you lose 78% of project knowledge
- If wlonk AND one other person leave, project is in serious danger
- 106 critical files (auth, config, deploy, etc.) have single owners
- 256 total files have never been touched by more than one person

**Recommendations:**
1. **URGENT**: Cross-train team members on critical systems
2. Implement mandatory code reviews (spread knowledge)
3. Pair programming sessions on critical components
4. Document tribal knowledge before it walks out the door
5. Rotate ownership of critical files

### tfjson - HIGH RISK

```json
{
  "estimated_bus_factor": 0,  // API issue, but analysis still works
  "critical_sole_ownership": 26,
  "total_sole_ownership": 78,
  "insights": [
    {
      "severity": "critical",
      "description": "Bus factor of 0 - project highly vulnerable"
    },
    {
      "severity": "high",
      "description": "26 critical files owned by single contributors"
    },
    {
      "severity": "medium",
      "description": "78 files owned by single contributors"
    }
  ]
}
```

**What This Means:**
- Matthew is the sole contributor
- 26 critical files with single ownership
- Classic "one person project" risk

## How This Enables Context-Aware AI

### Example 1: Refactoring Suggestions

**Without Bus Factor Intelligence:**
```
User: "Help refactor our auth system"
LLM: "Here's a complete rewrite using modern patterns"
Result: ❌ Only one person understands auth, can't risk breaking it
```

**With Bus Factor Intelligence:**
```
Vector DB Context:
- auth/ directory: sole owner (Darwin Monroy)
- Bus factor: 2 (critical)
- 106 critical files with single owners

LLM: "I see your auth system has a single owner (Darwin) and your bus factor
      is critically low (2). Instead of a risky rewrite, here's a PR to:

      1. Add comprehensive inline documentation
      2. Create an auth system overview doc
      3. Add unit tests that serve as living documentation
      4. Extract a small, well-tested auth utility module

      This makes the system understandable without risking a rewrite."

Result: ✅ Addresses risk-appropriate change, improves bus factor
```

### Example 2: Code Review Priorities

**Without Bus Factor Intelligence:**
```
User: "What should we focus on in code reviews?"
LLM: "Review for style consistency and performance"
Result: ❌ Misses the real problem
```

**With Bus Factor Intelligence:**
```
Vector DB Context:
- 256 sole ownership files
- Knowledge concentration: very_high
- Critical systems: auth, payment, deploy (single owners)

LLM: "Your biggest risk isn't code quality - it's knowledge concentration.
      In code reviews, focus on:

      1. Knowledge transfer (reviewer learns the system)
      2. Questioning 'why' decisions were made
      3. Suggesting alternative approaches (spreads thinking)
      4. Documenting tribal knowledge in PR comments

      Prioritize reviews of auth, payment, and deploy systems - these
      have single owners and losing that person would cripple the project."

Result: ✅ Strategic focus on reducing bus factor risk
```

### Example 3: Onboarding New Developers

**Without Bus Factor Intelligence:**
```
User: "What should new developers work on?"
LLM: "Start with small bug fixes and documentation"
Result: ❌ Generic advice
```

**With Bus Factor Intelligence:**
```
Vector DB Context:
- Bus factor: 2 (critical)
- wlonk owns 78% of commits
- 106 critical files with sole ownership

LLM: "Your bus factor is critically low (2). New developers should:

      1. Pair with wlonk on critical systems (auth, scoring engine)
      2. Shadow wlonk during deploys and incident response
      3. Document what they learn (reduce tribal knowledge)
      4. Make small changes to sole-ownership files (spread knowledge)

      Priority systems to cross-train:
      - scoring/scoring_engine/ (owned by Darwin)
      - .github/workflows/ (owned by Darwin)
      - pyproject.toml configuration (owned by Darwin)

      Goal: Get bus factor to 3+ within 60 days."

Result: ✅ Strategic onboarding that reduces organizational risk
```

## Technical Details

### How File Ownership is Calculated

We analyze the last 200 commits and count how many times each author touched each file:

```python
file_authors = {
    "auth.py": {
        "Alice": 15,
        "Bob": 3
    },
    "payment.py": {
        "Alice": 8
    }  # Sole ownership!
}
```

### Critical File Patterns

Files matching these patterns are flagged as critical:
- `auth`, `authentication`, `security`
- `payment`, `billing`, `checkout`
- `config`, `settings`, `environment`
- `main`, `index`, `server`, `app`
- `deploy`, `deployment`, `release`
- `migration`, `schema`, `database`

### Bus Factor Calculation

Simple heuristic: How many people collectively own 80% of commits?

```python
# Example with 10 contributors, 100 total commits
# If top 2 people have 85 commits combined → bus factor = 2
# If top 5 people needed for 80 commits → bus factor = 5
```

### Knowledge Concentration

```python
concentration_ratio = top_contributor_commits / total_commits

if ratio > 0.7:  very_high     # One person dominates
if ratio > 0.5:  high          # One person has majority
if ratio > 0.3:  medium        # Top person significant but not majority
else:            distributed   # Knowledge well-spread
```

## Insights Generated

### Critical: Low Bus Factor
**Trigger**: Estimated bus factor ≤ 2
**Severity**: Critical
**Meaning**: Losing 2 people would cripple the project

### High: Critical Sole Ownership
**Trigger**: Critical files (auth, payment, deploy) with single owners
**Severity**: High
**Meaning**: Critical systems have single points of failure

### High: Knowledge Concentration
**Trigger**: Top contributor owns >50% of commits
**Severity**: High
**Meaning**: Too much knowledge in one person's head

### Medium: Many Sole Ownership Files
**Trigger**: >20 files with single owners
**Severity**: Medium
**Meaning**: Lack of collaboration and cross-training

## Performance

### API Calls
- 1 call: `get_contributors()` (paginated)
- 1 call: `get_commits()` (last 200 commits)
- N calls: `commit.files` for each commit

**Total**: ~200-250 API calls per repo

### Rate Limit Impact
With 5000/hour limit:
- ~20-25 repos per hour
- For large orgs, this is the most expensive analysis

### Optimization
- Limit to last 200 commits (good proxy for current state)
- Limit to top 50 contributors (reduces API calls)
- Cache results between runs (planned)

## Limitations

### 1. Commits ≠ Expertise
Someone with 1 commit might deeply understand a system.
Our analysis shows activity, not expertise.

### 2. Recent Bias
We analyze last 200 commits, so recent contributors are weighted heavily.
Someone who built the system then left won't show up.

### 3. Commit Size
We count commits, not lines changed.
One person might have 10 small commits, another might have 1 massive commit.

### 4. Pair Programming
If two people pair but one commits, only one gets credit.

### 5. GitHub API Limitations
Contributors endpoint sometimes returns incomplete data.
We fall back to commit analysis when this happens.

## Future Enhancements

### Author Expertise Mapping
Map authors to domains:
```json
{
  "Alice": ["auth", "security", "backend"],
  "Bob": ["frontend", "UI", "testing"]
}
```

### Time-Based Analysis
Track how bus factor changes over time:
```json
{
  "2024-01": {"bus_factor": 1},
  "2024-06": {"bus_factor": 3},
  "2025-01": {"bus_factor": 2}  // Trend: declining!
}
```

### PR Review Patterns
Who reviews whose code? This shows knowledge flow:
```json
{
  "Alice": ["Bob", "Charlie"],  // Alice learns from Bob and Charlie
  "Bob": []  // Bob doesn't get reviews (risk!)
}
```

### Pairing Analysis
From commit co-authorship, detect pairing patterns:
```
Co-authored-by: Alice <alice@example.com>
Co-authored-by: Bob <bob@example.com>
```

### Expertise Decay
Files not touched in 2+ years by their owners = knowledge decay risk

## Usage Tips

### For Startups (Bus Factor 1-2)
- **Critical priority**: Document everything
- Pair programming mandatory
- Every PR needs review from different person
- Rotate on-call and deployment duties

### For Small Teams (Bus Factor 3-5)
- Focus on critical system knowledge sharing
- Cross-train on deployment and incident response
- Regular knowledge sharing sessions

### For Large Teams (Bus Factor 5+)
- Watch for knowledge silos (teams with low internal bus factor)
- Ensure critical systems have >3 people who understand them
- Track expertise distribution across teams

## Integration with Other Intelligence

Bus factor mapping combines powerfully with other extracted intelligence:

### + Commit Archaeology
- Low bus factor + Friday avoidance = Knowledge risk + Deployment fear
- Suggests: Cross-train on deployment before increasing frequency

### + CI Analysis
- Low bus factor + High CI failure = One person knows CI, it's fragile
- Suggests: Document CI, spread knowledge

### + Shadow Infrastructure
- Low bus factor + Many workaround scripts = Tribal knowledge in scripts
- Suggests: Document why scripts exist, what they do

### + PR Intelligence
- Low bus factor + Confusion in comments = Knowledge gaps spreading
- Suggests: Focus documentation efforts

## Actionable Recommendations

Based on your gradestack org's **bus factor of 2**:

1. **Week 1**: Document critical systems (auth, scoring engine, CI/CD)
2. **Week 2**: Schedule pairing sessions (wlonk + others on core systems)
3. **Week 3**: Mandatory code reviews (even for wlonk's changes)
4. **Week 4**: Rotate deployment duties (spread operational knowledge)
5. **Month 2**: Cross-train on incident response
6. **Month 3**: Aim for bus factor of 3+

**Goal**: No single person should be irreplaceable within 90 days.
