# Shadow Infrastructure Discovery

Discovers the **actual** workflows, tools, and processes developers use - not what's in the documentation.

## The Problem

**Documentation**: "Run `npm test` to run tests"
**Reality**: Developers run `make test-fast` because regular tests take 45 minutes

**Documentation**: "We have automated CI/CD"
**Reality**: Makefile has `deploy-prod` target with manual backup step

**Documentation**: "Just clone and run"
**Reality**: Requires Postgres, Redis, and 18 environment variables

## What We Extract

### 1. Makefile Targets

Reveals the **real** workflow commands developers use.

**Example Output:**
```json
{
  "makefile_targets": {
    "exists": true,
    "targets": ["build", "test", "deploy-prod", "dev"],
    "commands": {
      "deploy-prod": [
        "./scripts/backup-db.sh",
        "git pull origin main",
        "docker-compose -f docker-compose.prod.yml up -d"
      ]
    },
    "has_deploy_target": true,
    "has_test_target": true,
    "uses_docker": true
  }
}
```

**Insight Triggered:**
- `deploy-prod` target exists → Manual deployment detected
- Backup script called → Low confidence in rollback
- **Suggestion**: "Implement automated deployments with proper rollback mechanisms"

### 2. npm Scripts (Node.js)

Discovers hidden complexity and workarounds in package.json.

**Example Output:**
```json
{
  "npm_scripts": {
    "exists": true,
    "scripts": {
      "test": "jest",
      "test:fast": "jest --testPathIgnorePatterns=integration",
      "test:e2e": "cypress run",
      "postinstall": "patch-package"
    },
    "has_fast_test": true,
    "has_debug_mode": true,
    "postinstall_hook": true,
    "test_script_count": 3,
    "total_scripts": 12
  }
}
```

**Insights Triggered:**
- `test:fast` exists → Slow tests detected
  - **Suggestion**: "Optimize test suite or implement test parallelization"

- `postinstall: patch-package` → Dependency patching
  - **Suggestion**: "Investigate dependency issues and consider alternatives"

### 3. Python Scripts (pyproject.toml)

Extracts scripts from pyproject.toml for Python projects.

**Example Output:**
```json
{
  "python_scripts": {
    "exists": true,
    "scripts": {
      "gradestack-scoring": "scoring_engine.cli:main",
      "dev": "uvicorn app.main:app --reload"
    },
    "total_scripts": 2
  }
}
```

### 4. Environment Variable Complexity

Analyzes .env.example to measure configuration burden.

**Example Output:**
```json
{
  "env_complexity": {
    "exists": true,
    "total_vars": 23,
    "variables": [
      "DATABASE_URL",
      "REDIS_URL",
      "AWS_ACCESS_KEY_ID",
      "STRIPE_SECRET_KEY",
      "MAGIC_NUMBER_DONT_CHANGE",
      "LEGACY_API_COMPATIBILITY"
    ],
    "categories": {
      "database": 4,
      "cache": 2,
      "cloud": 5,
      "auth": 3,
      "observability": 2,
      "feature_flags": 2
    },
    "red_flags": [
      "MAGIC_NUMBER_DONT_CHANGE",
      "LEGACY_API_COMPATIBILITY"
    ],
    "complexity": "high"
  }
}
```

**Insights Triggered:**
- 23 vars → High config complexity
  - **Suggestion**: "Consider secrets manager to reduce onboarding friction"

- Red flags detected → Suspicious configuration
  - **Suggestion**: "Document these variables or refactor to remove magic values"

### 5. Workaround Scripts

Finds shell scripts that shouldn't exist in a well-automated system.

**Example Output:**
```json
{
  "workaround_scripts": {
    "found": true,
    "count": 3,
    "scripts": [
      {
        "name": "fix-permissions.sh",
        "path": "fix-permissions.sh",
        "location": "root"
      },
      {
        "name": "restart-worker.sh",
        "path": "scripts/restart-worker.sh",
        "location": "scripts",
        "suspicious_name": true
      },
      {
        "name": "manual-db-backup.sh",
        "path": "manual-db-backup.sh",
        "location": "root"
      }
    ]
  }
}
```

**What It Reveals:**
- `fix-permissions.sh` → Docker/deployment issues
- `restart-worker.sh` → Worker crashes frequently
- `manual-db-backup.sh` → Don't trust automated backups

**Insight Triggered:**
- **Suggestion**: "These scripts indicate manual processes that should be automated"

### 6. Docker Compose Local Stack

Discovers what local development **actually** requires.

**Example Output:**
```json
{
  "docker_compose_stack": {
    "exists": true,
    "services": ["app", "postgres", "redis", "mailcatcher", "elasticsearch"],
    "service_count": 5,
    "has_database": true,
    "has_cache": true,
    "has_queue": false,
    "complexity": "high"
  }
}
```

**Insight Triggered:**
- 5 services required → Complex local dev
  - **Suggestion**: "High onboarding friction - consider dev environment improvements or remote dev options"

## Synthesized Insights

The tool automatically generates actionable insights:

```json
{
  "insights": [
    {
      "category": "deployment",
      "issue": "manual_deployment_detected",
      "severity": "medium",
      "description": "Makefile contains deploy target, suggesting manual deployments",
      "suggestion": "Consider automated deployments with proper rollback mechanisms"
    },
    {
      "category": "testing",
      "issue": "slow_tests",
      "severity": "medium",
      "description": "Fast test variant exists, indicating regular tests are too slow",
      "suggestion": "Optimize test suite or implement test parallelization in CI"
    },
    {
      "category": "dependencies",
      "issue": "postinstall_patches",
      "severity": "high",
      "description": "postinstall hook detected, likely patching dependencies",
      "suggestion": "Investigate dependency issues and consider alternatives"
    },
    {
      "category": "configuration",
      "issue": "high_config_complexity",
      "severity": "medium",
      "description": "23 environment variables required",
      "suggestion": "Consider secrets manager to reduce onboarding friction"
    }
  ]
}
```

## Real-World Example: tfjson Repo

From your actual gradestack/tfjson repo:

```json
{
  "makefile_targets": {
    "targets": ["build", "build-all", "test", "clean", "install", "run"],
    "commands": {
      "build-all": [
        "GOOS=linux GOARCH=amd64 go build...",
        "GOOS=darwin GOARCH=arm64 go build..."
      ],
      "install": [
        "sudo mv $(BINARY_NAME) $(INSTALL_PATH)/$(BINARY_NAME)",
        "sudo chmod +x $(INSTALL_PATH)/$(BINARY_NAME)"
      ]
    }
  },
  "workaround_scripts": {
    "found": true,
    "scripts": [
      {
        "name": "install.sh",
        "path": "install.sh",
        "location": "root"
      }
    ]
  },
  "insights": [
    {
      "category": "process",
      "issue": "workaround_scripts_found",
      "description": "1 workaround scripts detected"
    }
  ]
}
```

**What This Tells Us:**
- Go project with cross-platform builds (5 platforms)
- Manual installation via Makefile (`sudo mv` and `chmod`)
- Install script in root for easier distribution
- Clean, focused tooling (no tech debt signals)

## How This Feeds RAG Context

### Traditional Approach
```
LLM: "Here's a PR to add CI/CD automation"
Reality: You already have GitHub Actions, but deploy manually because you don't trust it
Result: ❌ Misses the actual problem
```

### With Shadow Infrastructure Discovery
```
Vector DB Context:
- Has GitHub Actions CI
- Makefile has manual deploy-prod target
- Deploy script includes backup step
- No automated rollback testing

LLM: "I see you have CI but still deploy manually with backups. Here's a PR to add
      automated rollback testing to your CI pipeline, plus staging environment parity
      checks. This will build confidence to move to automated deployments."

Result: ✅ Addresses the real constraint (lack of confidence, not lack of automation)
```

## Use Cases

### 1. Onboarding Friction Detection
If `.env.example` has 20+ variables and `docker-compose.local.yml` requires 5 services:
- **Don't suggest**: More features
- **Do suggest**: Dev environment improvements, better documentation

### 2. Test Performance Issues
If `test:fast` exists in package.json:
- **Don't suggest**: More tests
- **Do suggest**: Test parallelization, CI caching, test optimization

### 3. Deployment Confidence Issues
If Makefile has `deploy-prod` with backup scripts:
- **Don't suggest**: Faster deployments
- **Do suggest**: Rollback testing, staging environment improvements

### 4. Dependency Problems
If `postinstall: patch-package` exists:
- **Don't suggest**: Upgrade dependencies
- **Do suggest**: Investigation of why patches are needed, alternative packages

## Technical Details

### API Calls
- 1-5 calls per repo (depending on which files exist)
- Minimal rate limit impact
- Gracefully handles missing files

### Performance
- Parses files without downloading full content when possible
- Basic text parsing (no heavy YAML/TOML libraries needed)
- Typical runtime: <2 seconds per repo

### Supported Files
- `Makefile`
- `package.json`
- `pyproject.toml`
- `.env.example`
- `*.sh` scripts
- `docker-compose*.yml`

## Future Enhancements

- **Commented-out code detection**: Find abandoned approaches
- **Git history analysis**: See how often workaround scripts are modified
- **Cross-repo patterns**: Find common pain points across organization
- **Temporal analysis**: Track complexity growth over time
- **Dockerfile analysis**: Extract system dependencies, multi-stage attempts
