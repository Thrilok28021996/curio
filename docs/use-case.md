# Curio — Use Case & Code Tasks

## Use Case

**A solo developer building and maintaining a FastAPI REST API with PostgreSQL, deployed on a single VPS.**

The developer ships features, handles incidents, manages dependencies, and iterates on deployment config. They don't have a team to bounce questions off. They encounter the same categories of problems repeatedly — dependency breakages, deployment failures, performance regressions — and each time they Google, Stack Overflow, and trial-and-error their way to a fix. Curio should learn from every one of these cycles and improve its ability to help next time.

---

## Target User

An independent developer (solo, bootstrapped, or side-project) who:

- Maintains one or two production services they built themselves
- Deploys to a VPS (Hetzner, DigitalOcean, AWS EC2) or a simple PaaS (Fly.io, Railway)
- Uses Python/FastAPI with a PostgreSQL or SQLite database
- Has no dedicated DevOps, SRE, or backend team — they are all of those
- Spends 30-60 minutes per week on "why is this broken?" type problems
- Wants to stop solving the same problem twice

---

## 3 Code Tasks Curio Should Improve Over Time

### Task 1: Debug and resolve deployment/build failures

**What happens:** The developer pushes code, the CI pipeline or deploy script fails. They read the error, search for it, try fixes, and eventually get it working.

**What Curio should learn:**

- After fixing a deployment failure, Curio should ask: "What was the problem, and what fixed it?" and store the error-to-fix mapping.
- Over time, Curio should recognize recurring failure patterns (e.g., "this error usually means the database migration ran out of memory" or "this Docker build fails when the base image changes").
- Curio should build a **project-specific runbook** — a growing set of "when X error shows up, do Y" patterns that it learned from the developer's own history.

**Concrete improvement:** If the same error class (e.g., database connection timeout during migration) recurs, Curio should proactively suggest the fix that worked last time, before the developer even asks. Measured by: number of problems Curio can diagnose correctly on first encounter after seeing the error pattern at least once.

---

### Task 2: Track and resolve dependency version compatibility

**What happens:** The developer runs `pip install` or `npm install` and something breaks because a transitive dependency updated and is now incompatible. Or they upgrade a major version and existing code stops working.

**What Curio should learn:**

- Record which dependency versions were working, what broke when, and which pin/upgrade resolved it.
- Track the relationship between dependency versions and the project's own code — "project X uses Pydantic v1 patterns, but Pydantic v2 changed `validator` to `field_validator`."
- Maintain a **dependency health log** that tracks when key dependencies released new versions and whether those releases caused issues in this project.

**Concrete improvement:** When a dependency is updated, Curio should proactively check its learned knowledge for known breaking changes and flag them before they cause a runtime error. Measured by: percentage of dependency-related issues that Curio could have predicted based on its learned compatibility map.

---

### Task 3: Diagnose and improve deployment config and performance

**What happens:** The app is slow or using too much memory. The developer needs to tune Gunicorn workers, adjust PostgreSQL connection pooling, configure Nginx reverse proxy settings, or tweak Docker resource limits.

**What Curio should learn:**

- Record the deployment environment: how many CPU cores, how much RAM, what services run on the same VPS.
- Track what config changes were tried and what effect they had (e.g., "increasing Gunicorn workers from 2 to 4 dropped p95 latency from 800ms to 200ms" or "adding a Redis cache for this endpoint cut DB queries by 90%").
- Learn the project's performance profile — which endpoints are slow, what database queries are expensive, what the traffic pattern looks like.

**Concrete improvement:** Curio should be able to answer "why is my app slow?" with context-specific advice based on its learned model of this particular project's infrastructure, not generic advice. Measured by: number of performance recommendations that are specific to this project's setup (vs. generic "add caching" type suggestions).

---

## Why This Use Case

1. **High repeat frequency.** Deployment failures, dependency issues, and performance tuning recur regularly for solo developers. This gives Curio many learning opportunities per week.

2. **Concrete, measurable outcomes.** Each task has a clear success state (deploy succeeds, app runs, latency improves). Curio's learning can be evaluated against real results.

3. **Solo developer pain is real and underserved.** Teams have Slack channels, SRE teams, and institutional memory. Solo developers have Google and hope. Curio fills that gap by becoming their institutional memory.

4. **Local-first is natural.** A solo developer's codebase, deployment config, and error history are private — they won't send this to a cloud service. Local-first architecture (Curio's chosen architecture) fits perfectly.

5. **Path to generalization.** If Curio can learn project-specific patterns for one developer's FastAPI app, the same loop applies to any developer's any project. This is the narrow wedge that proves the autonomous learning model before broadening.
