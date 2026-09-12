# Curio — Monetization Strategy (Research-Backed)

## Model: Open Core

Proven by: GitLab ($680M), Grafana ($100M+), Supabase ($50M), PostHog ($45M), CockroachDB ($200M)

```
Free engine (self-hosted) → builds adoption
        ↓
Paid cloud (managed)      → converts 2-5% to revenue
        ↓
Enterprise tier           → provides revenue floor
```

---

## What's free vs paid

### Free forever (the engine)

| Feature | Details |
|---|---|
| CLI | `curio teach`, `observe`, `know`, `gaps`, `progress`, `consolidate` |
| MCP server | Integration with Claude Code, Cursor |
| Full learning loop | Gap detection, selective storage, forgetting, progress |
| Local knowledge graph | SQLite storage on user's machine |
| Unlimited projects | No project count limit |
| Audit trail | Every decision logged locally |
| Web search | DuckDuckGo (no API keys needed) |
| Python API | `from src.curio import Curio` |

**Why free:** This is the distribution engine. Every user is a potential paying customer. The engine must be genuinely useful — not crippled.

### Paid: Curio Cloud ($20/month)

| Feature | Details |
|---|---|
| Cloud sync | Knowledge graph backed up to encrypted cloud |
| Cross-device access | Same knowledge on laptop, desktop, server |
| Web dashboard | Visual knowledge graph, gap analysis, progress charts |
| Weekly learning digest | Email summary of what Curio learned |
| API access | REST API for custom integrations |
| Priority support | Faster response times |

**Why pay:** Individual power users who use Curio across devices and want visibility into what it's learning.

### Paid: Curio Team ($50/user/month)

| Feature | Details |
|---|---|
| Everything in Curio Cloud | |
| Shared team knowledge graph | Team learns together, not in silos |
| Onboarding mode | New devs learn the codebase faster |
| Admin dashboard | See what the team knows and doesn't know |
| SSO / SAML | Enterprise authentication |
| Compliance audit logs | SOC2-ready audit trail |
| Dedicated support | Named support contact |

**Why pay:** Teams where knowledge sharing and onboarding are real pain points. $50/user is below an engineer's hourly rate — if Curio saves 2 hours/month, it pays for itself 10x.

### Enterprise (custom pricing)

| Feature | Details |
|---|---|
| Everything in Team | |
| Self-hosted deployment | Run Curio Cloud on your own infra |
| Custom integrations | Build on Curio's API |
| SLA guarantees | 99.9% uptime |
| Training and onboarding | Dedicated success manager |
| Custom compliance | GDPR, HIPAA, custom data residency |

**Why pay:** Companies with 50+ engineers, strict compliance requirements, or custom deployment needs.

---

## Conversion benchmarks (from research)

| Metric | Benchmark | Source |
|---|---|---|
| Free → paid conversion | 2-5% typical | Industry data |
| Top performers | 8-12% | PostHog, GitLab |
| Enterprise boost | +3-5% | SSO, audit logs, compliance |
| Time to first payment | 2-4 weeks median | Developer tools |
| Self-hosted → cloud | 10-20% try cloud, 3-8% convert | Supabase, PostHog |

### What triggers upgrades (ranked by impact)

1. **Hit free tier limits** — usage caps force upgrade (Supabase: 500MB DB, PostHog: 1M events)
2. **Don't want to self-host** — managed cloud is the product (n8n, Supabase)
3. **Team collaboration** — SSO, RBAC, multi-user (GitLab, Grafana)
4. **Production SLA** — uptime guarantees, support (all enterprises)
5. **Compliance** — SOC2, HIPAA, GDPR (GitLab Ultimate, Grafana Enterprise)

---

## Revenue projections

### Conservative (Year 1-3)

| Year | Free users | Paid users (5%) | Pro ($20) | Team ($50) | MRR | ARR |
|---|---|---|---|---|---|---|
| 1 | 5,000 | 250 | 200 | 50 users | $6,500 | $78K |
| 2 | 20,000 | 1,000 | 800 | 200 users | $26,000 | $312K |
| 3 | 50,000 | 2,500 | 1,800 | 700 users + enterprise | $61,000 | $732K |

### Optimistic (Year 1-3)

| Year | Free users | Paid users (8%) | Pro ($20) | Team ($50) | Enterprise | MRR | ARR |
|---|---|---|---|---|---|---|---|
| 1 | 10,000 | 800 | 600 | 200 users | — | $22,000 | $264K |
| 2 | 40,000 | 3,200 | 2,000 | 1,200 users | 2 contracts | $84,000 | $1M |
| 3 | 100,000 | 8,000 | 5,000 | 3,000 users | 5 contracts | $210,000 | $2.5M |

---

## Unit economics

| Metric | Target |
|---|---|
| Cost per free user | ~$0 (local-only, no infra) |
| Cost per paid user (cloud) | $1-3/mo (storage + compute) |
| Revenue per Pro user | $20/mo |
| Revenue per Team user | $50/mo |
| Gross margin (Pro) | 85-95% |
| Gross margin (Team) | 90-95% |
| LTV:CAC ratio | >3:1 |

---

## Go-to-market sequence

### Phase 1: Community (Month 1-3)
- Open source the core on GitHub
- Write blog posts: "How Curio learns like a child"
- Demo on Twitter/X, Hacker News, Reddit
- Target: 1,000 GitHub stars, 500 active users

### Phase 2: Early Adopters (Month 3-6)
- Launch Curio Cloud (Pro tier)
- Offer lifetime deals to first 100 users ($99 one-time)
- Collect feedback, iterate fast
- Target: 100 paid users, $2K MRR

### Phase 3: Team Sales (Month 6-12)
- Launch Curio Team tier
- Outreach to startups and small teams
- Case studies from early adopters
- Target: 20 team customers, $10K MRR

### Phase 4: Enterprise (Year 2)
- SOC 2 compliance
- SSO / SAML
- Dedicated support
- Custom deployments
- Target: 5 enterprise customers, $50K MRR

---

## Competitive moat

The learning loop is the moat. Anyone can build a memory system (Mem0 has 58K stars). But:

- **Gap detection** — knowing what you don't know
- **Selective learning** — deciding what's worth knowing
- **Forgetting** — removing what doesn't matter
- **Progress tracking** — measuring what you've learned

These four things together form a system that gets better the longer you use it. That's what users pay for.

---

## Key metrics to track

| Metric | Target | Why it matters |
|---|---|---|
| GitHub stars | 1K → 5K → 20K | Community adoption |
| Active users (weekly) | 500 → 2K → 10K | Product usage |
| Free → paid conversion | >5% | Product-market fit |
| Pro monthly retention | >90% | Stickiness |
| Team expansion rate | >20%/mo | Viral growth within orgs |
| Knowledge nodes per user | Growing | Engagement |
| Cost per paid user | <$3/mo | Unit economics |
| CAC payback | <6 months | Sustainable growth |

---

## Open questions to resolve

1. **Should the free tier have usage limits?** Research says yes — limits trigger upgrades. But they must be generous enough that the free tier is genuinely useful.
2. **Should we charge for LLM extraction?** The LLM feature is expensive (API calls). Could be a differentiator: free = basic extraction, paid = full LLM extraction.
3. **Should the MCP server be free forever?** Yes — it's the distribution channel.
4. **Should we offer a self-hosted Team option?** Yes — for privacy-sensitive teams. Price at 2x the cloud rate.
5. **Should we add a marketplace for learning templates?** Later — after product-market fit.
