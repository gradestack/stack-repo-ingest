# stack-repo-ingest

GitHub repository ingestion tool for extracting complete engineering context. Part of the gradestack platform engineering system.

## Overview

Extracts the "engineering DNA" from customer GitHub repositories - not just code, but the critical files that define HOW they build, deploy, and operate. This context feeds into RAG systems to enable AI-powered, context-aware engineering suggestions.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         GRADESTACK SYSTEM                               │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐
│   Customer GitHub    │
│      Organization    │
│                      │
│  ┌────┐  ┌────┐     │
│  │Repo│  │Repo│ ... │
│  └────┘  └────┘     │
└──────────┬───────────┘
           │
           │ GitHub API
           │ (Token Auth)
           ↓
    ┌──────────────────────────────────┐
    │   stack-repo-ingest (THIS TOOL)  │◄── YOU ARE HERE
    │                                  │
    │  • Fetches repo metadata         │
    │  • Extracts critical files       │
    │    - Dependencies (package.json) │
    │    - IaC (Terraform, K8s)        │
    │    - CI/CD (.github/workflows)   │
    │    - Deployment (Dockerfile)     │
    │  • Analyzes structure            │
    │  • Outputs structured JSON       │
    └──────────┬───────────────────────┘
               │
               │ JSON Documents
               │ (Engineering Context)
               ↓
    ┌─────────────────────────┐
    │  Processing Pipeline    │
    │  (Darwin's Backend)     │
    │                         │
    │  • Chunk documents      │
    │  • Generate embeddings  │
    │  • Store in Vector DB   │
    └──────────┬──────────────┘
               │
               │ Semantic Search
               │
    ┌──────────▼──────────────┐
    │     Vector Store        │
    │     (Qdrant/Chroma)     │
    │                         │
    │  [Context Indexed by    │
    │   Semantic Meaning]     │
    └──────────┬──────────────┘
               │
               │ Retrieval
               │
    ┌──────────▼──────────────┐
    │      RAG System         │
    │                         │
    │  Query → Retrieve       │
    │  Relevant Context       │
    └──────────┬──────────────┘
               │
               │ Context + Prompt
               │
    ┌──────────▼──────────────┐
    │     LLM (Claude/GPT)    │
    │                         │
    │  "This customer uses    │
    │   Heroku + Node.js..."  │
    └──────────┬──────────────┘
               │
               │ Context-Aware Response
               │
    ┌──────────▼──────────────┐
    │   Draft PR Generator    │
    │                         │
    │  • Tailored to stack    │
    │  • Respects constraints │
    │  • Proactive fixes      │
    └─────────────────────────┘
```

## Why This Matters

**Traditional Approach:**
- AI suggests: "Migrate to Kubernetes"
- Customer reality: 2-person team on Heroku
- Result: ❌ Unusable suggestion

**With Context-Aware RAG:**
- Ingestion captures: Small team, Heroku, Node.js, no caching
- Vector DB retrieves relevant context for query
- LLM sees: "This customer runs Express on Heroku with 2 developers"
- AI suggests: "Add Redis caching via Heroku addon (here's a PR)"
- Result: ✅ Perfectly tailored, immediately actionable

## What Gets Ingested

### 1. Repository Metadata
- Languages, frameworks, activity metrics
- Team size signals (contributors, issue count)
- Repository age and update frequency

### 2. Dependency Files
```
Node.js:    package.json, package-lock.json
Python:     requirements.txt, Pipfile, pyproject.toml
Go:         go.mod, go.sum
Ruby:       Gemfile
Rust:       Cargo.toml
Java:       pom.xml, build.gradle
PHP:        composer.json
```

### 3. Infrastructure as Code
```
Docker:     Dockerfile, docker-compose.yml
Kubernetes: k8s/*.yaml, kubernetes/*.yaml
Terraform:  *.tf files
```

### 4. CI/CD Configuration
```
GitHub Actions:  .github/workflows/*.yml
GitLab CI:       .gitlab-ci.yml
CircleCI:        .circleci/config.yml
Jenkins:         Jenkinsfile
```

### 5. Deployment Configuration
```
Heroku:     Procfile, app.json
Vercel:     vercel.json
Netlify:    netlify.toml
AWS:        appspec.yml, buildspec.yml
```

### 6. Documentation
```
README.md, CONTRIBUTING.md, docs/
```

## Installation

```bash
# Clone repository
git clone https://github.com/gradestack/stack-repo-ingest.git
cd stack-repo-ingest

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GitHub token and org name
```

## Configuration

Create a `.env` file:

```env
GITHUB_TOKEN=ghp_your_token_here
GITHUB_ORG=your-org-name
```

### Creating a GitHub Token

1. Go to https://github.com/settings/tokens/new
2. Select scopes:
   - `repo` (full control of private repositories)
   - `read:org` (read organization membership)
3. Generate token and store securely

## Usage

### Basic Ingestion

```bash
# Activate virtual environment
source venv/bin/activate

# Run ingestion
python ingest.py --org your-org-name
```

### With Custom Token

```bash
python ingest.py --org your-org-name --token ghp_your_token
```

## Output Format

Results are saved to `output/` directory:

```
output/
├── summary.json           # Overview of ingestion run
├── repo-name-1.json      # Complete context for repo 1
├── repo-name-2.json      # Complete context for repo 2
└── ...
```

### Example Output Structure

```json
{
  "metadata": {
    "name": "api-service",
    "language": "JavaScript",
    "languages": {"JavaScript": 45000, "TypeScript": 12000},
    "size_kb": 1250,
    "created_at": "2024-01-15T10:30:00Z",
    "pushed_at": "2024-01-29T14:22:33Z"
  },
  "files": {
    "nodejs_deps": {
      "path": "package.json",
      "content": "{ \"dependencies\": { \"express\": \"^4.18.0\" } }"
    },
    "docker": {
      "path": "Dockerfile",
      "content": "FROM node:18-alpine\nWORKDIR /app..."
    },
    "heroku": {
      "path": "Procfile",
      "content": "web: node server.js"
    },
    "github_actions": [
      {
        "name": "ci.yml",
        "path": ".github/workflows/ci.yml",
        "content": "name: CI\non: [push, pull_request]..."
      }
    ]
  },
  "structure": {
    "has_tests": true,
    "has_docs": true,
    "has_ci": true,
    "has_docker": true,
    "has_iac": false,
    "directories": [".github", "src", "tests", "docs"]
  },
  "ingested_at": "2026-01-29T23:15:42.123456Z"
}
```

## Integration with RAG Pipeline

The JSON output from this tool feeds into the embedding pipeline:

1. **Chunking**: Documents split into semantic chunks
2. **Embedding**: Converted to vector representations
3. **Storage**: Indexed in vector database with metadata
4. **Retrieval**: Queried by semantic similarity
5. **Context**: Fed to LLM for context-aware responses

## Use Cases

### Platform Engineering Automation
- Identify outdated dependencies across organization
- Detect missing security configurations
- Suggest infrastructure improvements tailored to stack

### Compliance & Security
- Audit deployment configurations
- Check for required security files (.github/SECURITY.md)
- Validate CI/CD security practices

### Technical Debt Analysis
- Find repos without tests or CI
- Identify outdated deployment patterns
- Prioritize modernization efforts

### AI-Powered PR Generation
- Context-aware dependency updates
- Infrastructure optimization suggestions
- Security patch recommendations

## Extending the Ingester

### Adding New File Patterns

Edit `CRITICAL_FILES` dict in `ingest.py`:

```python
CRITICAL_FILES = {
    'your-file.yml': 'your_file_type',
    # ...
}
```

### Custom Processing

Add new methods to `RepoIngester` class:

```python
def _fetch_custom_data(self, repo: Repository.Repository) -> Dict[str, Any]:
    # Your custom logic here
    pass
```

## Performance & Rate Limits

- GitHub API rate limit: 5,000 requests/hour (authenticated)
- Typical ingestion: ~10-20 API calls per repository
- For large orgs (100+ repos), ingestion takes ~5-10 minutes

### Handling Large Organizations

The tool respects rate limits automatically. For very large orgs:

```bash
# Process in batches if needed
python ingest.py --org your-org --limit 50
```

(Note: --limit flag not yet implemented but planned)

## Development

### Project Structure

```
stack-repo-ingest/
├── ingest.py              # Main ingestion script
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── HOW_IT_WORKS.md       # Technical deep dive
└── output/               # Ingestion results (gitignored)
```

### Running Tests

```bash
# Run against test organization
python ingest.py --org gradestack

# Validate output
python -m json.tool output/summary.json
```

## Roadmap

- [ ] Incremental updates (only process changed repos)
- [ ] Webhook support for real-time ingestion
- [ ] Private repo support via SSH keys
- [ ] GitLab and Bitbucket support
- [ ] Enhanced terraform file parsing
- [ ] Monorepo subdirectory detection
- [ ] Cost estimation integration

## Contributing

Contributions welcome! This tool is part of the gradestack platform engineering system.

## License

MIT License

## Related Projects

- [stacops](https://github.com/gradestack/stacops) - Platform engineering scoring framework
- [tfjson](https://github.com/gradestack/tfjson) - Terraform JSON CLI tool

## Support

Issues and questions: https://github.com/gradestack/stack-repo-ingest/issues

---

Built with ❤️ by [Gradestack](https://gradestack.io)
