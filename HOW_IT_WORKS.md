# How This Feeds Your RAG

## What We're Extracting

The ingester grabs **engineering fingerprints** - files that define HOW a customer builds and deploys:

### 1. Dependencies (What they use)
- `package.json` → "Uses Express, React, PostgreSQL driver"
- `requirements.txt` → "Uses Django, Celery, Redis"
- **RAG Impact**: LLM knows what libraries they have, can suggest compatible updates

### 2. Infrastructure (How they deploy)
- `Dockerfile` → "Uses Node 18, runs on port 3000"
- `Procfile` → "Deploys to Heroku"
- `kubernetes/*.yaml` → "Uses K8s with 3 microservices"
- **RAG Impact**: LLM won't suggest K8s migrations to a Heroku shop

### 3. CI/CD (How they ship)
- `.github/workflows/*.yml` → "Runs tests on PR, deploys on merge"
- **RAG Impact**: LLM can suggest improvements to THEIR pipeline, not generic ones

### 4. Team Size Signals
- Repo activity, open issues, number of contributors
- **RAG Impact**: Small team? Suggest simple solutions. Large team? Can suggest complex refactors

## The RAG Flow (Your Part → Darwin's Part)

```
[1] YOU: GitHub → Extract files → JSON documents
    Output: {
      "repo": "api-service",
      "files": {
        "package.json": "{ express: 4.18.0, pg: 8.11.0 }",
        "Dockerfile": "FROM node:18...",
        "Procfile": "web: node server.js"
      }
    }

[2] DARWIN: JSON → Chunk → Embeddings → Vector DB
    - Splits into chunks: "This service uses Express 4.18"
    - Converts to numbers: [0.234, -0.812, 0.456, ...]
    - Stores with metadata: {repo: "api-service", type: "dependency"}

[3] QUERY TIME: Customer asks "How can we improve our API?"
    - Search vector DB for "api improvements" + customer_id
    - Retrieves: "Uses Express on Heroku, Node 18, no caching"
    - LLM gets context: "This customer runs Express on Heroku..."
    - LLM suggests: "Add Redis caching (compatible with Heroku)"

    NOT: "Migrate to Kubernetes" (wrong context)
    NOT: "Use .NET" (wrong stack)
```

## Why This Creates Repeatable Value

**Without RAG:**
- LLM: "You should use microservices and Kubernetes"
- Customer: "We're 2 people on Heroku..."

**With RAG:**
- Vector DB retrieves: Small team, Heroku, Node.js, no Redis
- LLM: "Add Redis caching via Heroku addon, here's a PR"
- Customer: "Perfect, matches our stack exactly"

## Key Insight: Embeddings = Meaning Search

Traditional DB: "Find repos with 'redis' in files" (keyword match)
Vector DB: "Find repos similar to 'caching layer'" (finds Redis, Memcached, etc.)

This is why we can ask "How does this customer handle background jobs?" and it finds:
- Celery configs (Python)
- Sidekiq configs (Ruby)
- Bull configs (Node.js)

All different tools, but similar MEANING → similar embeddings → retrieved together
