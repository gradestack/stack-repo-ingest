# PR Comment Intelligence

Mines PR comments to reveal confusion, technical debt, and fragility signals that traditional metrics miss.

## What It Extracts

### 1. Confusion Signals
Detects when developers ask questions or express uncertainty:

**Patterns:**
- "how does", "why does", "what is"
- "confused", "unclear", "not sure"
- "can you explain", "don't understand"

**Example Output:**
```json
{
  "confusion_signals": [
    {
      "pr": 42,
      "pr_title": "Add authentication middleware",
      "pattern": "how does",
      "snippet": "how does the session handling work with this approach? not sure if we need redis..."
    },
    {
      "pr": 38,
      "pr_title": "Refactor API layer",
      "pattern": "confused",
      "snippet": "confused about the difference between AuthService and SessionManager. what's the..."
    }
  ]
}
```

**What It Reveals:**
- Knowledge gaps in the team
- Complexity hotspots (lots of questions = hard to understand)
- Documentation needs
- Onboarding friction points

### 2. Tech Debt Acknowledgments
Captures admitted shortcuts and future work:

**Patterns:**
- "should probably", "we should"
- "todo", "fixme", "hack"
- "workaround", "technical debt"
- "will fix later", "temporary", "quick fix"

**Example Output:**
```json
{
  "tech_debt_acknowledgments": [
    {
      "pr": 51,
      "pr_title": "Fix production timeout issue",
      "pattern": "workaround",
      "snippet": "this is a workaround for now. we should probably move to async processing but that's a bigger refactor..."
    },
    {
      "pr": 45,
      "pr_title": "Update payment flow",
      "pattern": "todo",
      "snippet": "TODO: need to add proper error handling here. for now just catching everything to unblock prod deploy"
    }
  ]
}
```

**What It Reveals:**
- Known shortcuts that never get fixed
- Areas developers know need improvement
- Process pressure points (deadlines forcing quick fixes)
- Actual vs. claimed code quality

### 3. Fragility Mentions
Identifies brittle code and known failure points:

**Patterns:**
- "breaks", "breaks when", "fails"
- "doesn't work", "broken", "regression"
- "flaky", "intermittent", "sometimes fails"
- "race condition"

**Example Output:**
```json
{
  "fragility_mentions": [
    {
      "pr": 39,
      "pr_title": "Update deployment script",
      "pattern": "breaks when",
      "snippet": "this breaks when running in docker but works locally. think it's an env var issue..."
    },
    {
      "pr": 33,
      "pr_title": "Fix test suite",
      "pattern": "flaky",
      "snippet": "these tests are flaky in CI. they pass locally but fail about 30% of the time in github actions..."
    }
  ]
}
```

**What It Reveals:**
- Known brittle areas
- Environment-specific issues
- Test reliability problems
- Areas to avoid in automated PRs

### 4. Common Discussion Topics
Aggregates patterns to show what the team talks about most:

**Example Output:**
```json
{
  "common_discussion_topics": [
    {"pattern": "how does", "count": 12},
    {"pattern": "should probably", "count": 8},
    {"pattern": "workaround", "count": 5},
    {"pattern": "flaky", "count": 4},
    {"pattern": "race condition", "count": 3}
  ]
}
```

**What It Reveals:**
- Most confusing parts of codebase (frequent "how does")
- Most acknowledged tech debt (frequent "should probably")
- Biggest reliability issues (frequent "flaky")

## How It's Used in RAG Context

### Traditional Approach
```
LLM: "Here's a PR to add async processing to your payment flow"
Reality: Team already tried async, broke production, rolled back
Result: ❌ Wasted effort, loss of trust
```

### With PR Intelligence
```
Vector DB Context:
- PR #51: "workaround for timeout, should use async but too risky"
- PR #48: "rolled back async change, breaks in production"

LLM: "I see you had issues with async in production. Here's a PR to add
      request timeouts at the load balancer level instead - lower risk,
      same outcome"
Result: ✅ Context-aware, addresses real constraints
```

## Real-World Examples

### Example 1: Kubernetes Confusion
If PR comments frequently ask "how does" about Kubernetes configs:
- **Don't suggest**: More K8s migrations
- **Do suggest**: K8s documentation, training resources, or simpler alternatives

### Example 2: Flaky Tests
If comments mention "flaky" tests repeatedly:
- **Don't suggest**: More tests
- **Do suggest**: Test infrastructure improvements, better CI caching, test isolation

### Example 3: Database Workarounds
If comments say "workaround for DB performance":
- **Don't suggest**: Complex query optimization
- **Do suggest**: Caching layer, or completion of the acknowledged workaround

## Technical Implementation

### API Calls Per Repo
- 1 call: `get_pulls()` (paginated)
- N calls: `get_issue_comments()` per PR
- N calls: `get_comments()` per PR (review comments)

**Rate Limit Impact:**
- ~3 calls per PR analyzed
- Limited to 100 most recent PRs per repo
- Typical org (10 repos): ~3000 API calls = well under 5000/hour limit

### Performance
- Analyzed 100 PRs with 500 total comments: ~30 seconds
- Uses pagination to avoid memory issues
- Gracefully handles access errors (skip and continue)

### Privacy Considerations
- Only analyzes comments from repositories with API access
- Respects GitHub permissions (won't see private PRs without token access)
- Stores comment snippets (first 200 chars) not full text
- Can be disabled with flag (future: `--skip-pr-mining`)

## Output Structure

```json
{
  "pr_intelligence": {
    "confusion_signals": [
      {
        "pr": <number>,
        "pr_title": "<title>",
        "pattern": "<matched_pattern>",
        "snippet": "<first_200_chars>"
      }
    ],
    "tech_debt_acknowledgments": [...],
    "fragility_mentions": [...],
    "common_discussion_topics": [
      {"pattern": "<pattern>", "count": <frequency>}
    ],
    "total_prs_analyzed": <count>,
    "total_comments_analyzed": <count>
  }
}
```

## Future Enhancements

- **Sentiment analysis**: Measure frustration vs enthusiasm
- **Author expertise mapping**: Who knows what (from comment patterns)
- **Response time analysis**: How long do questions go unanswered
- **Cross-repo pattern detection**: Same confusion across multiple repos
- **Temporal patterns**: Are recent PRs more confused than old ones?
- **Action item tracking**: "TODO" in comments that never get addressed
