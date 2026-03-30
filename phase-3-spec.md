# LifeOS — Phase 3 Build Spec
> Hand this to Claude Code after Phase 2 is fully working.
> Phase 1 and Phase 2 must be complete before starting this.

---

## What Phase 3 Adds

- Embeddings-based matching (replaces difflib)
- Smart daily digest: "What did I do today?"
- Weekly summary
- Search across timeline and tasks
- Edit and delete commands

---

## 1. Embeddings-Based Matching

Replace difflib with local embeddings for smarter deduplication.

### Install dependency:

```bash
pip install sentence-transformers
```

### Implementation (actions.py):

```python
from sentence_transformers import SentenceTransformer
import numpy as np

# Load once at startup, cache in memory
_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def embedding_similarity(a: str, b: str) -> float:
    model = get_model()
    embeddings = model.encode([a, b])
    cos_sim = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    return float(cos_sim)
```

### Updated dedup logic:

```python
SIMILARITY_THRESHOLD = 0.82

def find_duplicate_task(session, title: str) -> Task | None:
    tasks = session.query(Task).filter(Task.status == "pending").all()
    best_match = None
    best_score = 0
    for task in tasks:
        score = embedding_similarity(title, task.title)
        if score > SIMILARITY_THRESHOLD and score > best_score:
            best_match = task
            best_score = score
    return best_match
```

Apply same pattern to `find_duplicate_project()`.

### Why this matters:
- difflib: "math test" vs "maths exam" → low similarity → creates duplicate
- embeddings: "math test" vs "maths exam" → 0.91 similarity → correctly deduplicates

---

## 2. Smart Daily Digest

```bash
life digest
```

Calls LLM to generate a natural language summary of today's activity.

### Implementation (actions.py):

```python
def generate_digest(session) -> str:
    today = datetime.utcnow().date()
    
    # Pull today's data
    entries = session.query(TimelineEntry).filter(
        func.date(TimelineEntry.timestamp) == today
    ).all()
    
    tasks_created = session.query(Task).filter(
        func.date(Task.created_at) == today
    ).all()
    
    tasks_done = session.query(Task).filter(
        Task.status == "done",
        func.date(Task.updated_at) == today
    ).all()
    
    # Build context for LLM
    context = f"""
Timeline entries today:
{chr(10).join([e.content for e in entries])}

Tasks created today:
{chr(10).join([t.title for t in tasks_created])}

Tasks completed today:
{chr(10).join([t.title for t in tasks_done])}
"""
    
    prompt = f"""
Based on this person's activity log, write a brief, friendly daily digest.
2-3 sentences max. Be specific. Mention what they worked on and what they completed.
If nothing happened, say so honestly.

Activity data:
{context}

Respond only with the digest text. No preamble.
"""
    
    # Call Ollama
    response = call_ollama(prompt)
    return response
```

### Output:

```
 📊 Daily Digest — Mar 30, 2026

You worked on LifeOS today, completing both Phase 1 and Phase 2 of the
CLI tool. You also logged a math test due in 3 days and pushed the
project to GitHub. Solid day.
```

---

## 3. Weekly Summary

```bash
life weekly
```

Same pattern as digest but pulls last 7 days.

### Output:

```
 📊 Weekly Summary — Mar 24 to Mar 30, 2026

This week you organized SNUC Hacks, built LifeOS Phase 1 and 2,
and sent corrections on your IITM research paper draft.
3 tasks completed, 5 still pending.

 Most active project: LifeOS (4 days)
 Tasks completed: 3
 Tasks created: 8
 Timeline entries: 12
```

---

## 4. Search

```bash
life search "blockchain"
life search "math"
```

Searches both timeline entries and tasks using embeddings.

### Implementation:

```python
def search(session, query: str, top_k: int = 5):
    model = get_model()
    query_embedding = model.encode([query])[0]
    
    results = []
    
    # Search tasks
    tasks = session.query(Task).all()
    for task in tasks:
        score = embedding_similarity(query, task.title)
        if score > 0.5:
            results.append(("task", task, score))
    
    # Search timeline
    entries = session.query(TimelineEntry).all()
    for entry in entries:
        score = embedding_similarity(query, entry.content)
        if score > 0.5:
            results.append(("timeline", entry, score))
    
    # Sort by score, return top_k
    results.sort(key=lambda x: x[2], reverse=True)
    return results[:top_k]
```

### Output:

```
 🔍 Search: "blockchain"

Tasks:
  • audit blockchain contracts (Project: IITM Research)

Timeline:
  Mar 15 · 14:32  worked on blockchain auditing framework with IITM team
  Mar 10 · 10:15  dockerized the blockchain MCP tool
```

---

## 5. Edit and Delete Commands

```bash
# Edit task title or due date
life edit <id> --title "new title"
life edit <id> --due "next friday"

# Delete a task
life delete <id>

# Delete a project (and unlink its tasks)
life delete-project <id>
```

### Implementation notes:
- `edit` updates only the provided fields
- `delete` sets status to "deleted" (soft delete, don't actually remove)
- Add `status = "deleted"` to filter out in all list views
- `delete-project` sets project as deleted, sets `project_id = null` on linked tasks

---

## 6. Streak Tracking

```bash
life streak
```

Counts consecutive days the user has logged at least one entry.

### Implementation:

```python
def get_streak(session) -> int:
    entries = session.query(TimelineEntry).order_by(
        TimelineEntry.timestamp.desc()
    ).all()
    
    if not entries:
        return 0
    
    dates = sorted(set([e.timestamp.date() for e in entries]), reverse=True)
    streak = 0
    today = datetime.utcnow().date()
    
    for i, date in enumerate(dates):
        expected = today - timedelta(days=i)
        if date == expected:
            streak += 1
        else:
            break
    
    return streak
```

### Show streak in summary:

```
 🔥 Current streak: 3 days
```

---

## Updated Summary Command

Update `life summary` to include streak and digest:

```
 📊 Today's Summary — Mar 30, 2026
 🔥 Streak: 3 days

 Today in one line:
 Built LifeOS Phase 2, pushed to GitHub, logged math test deadline.

 🕐 Timeline (3 entries)
 📌 Tasks Created (2)
 ✅ Tasks Completed (1)
 🗂️  Projects Active (1)
```

---

## Performance Note

`SentenceTransformer` loads a ~90MB model on first run. Cache it in memory after first load. First `life log` after install will be slow (~3-5 seconds). After that, it's fast.

Add a one-time message:

```
First run: loading embedding model (~3 seconds)...
```

---

## Database Changes

No new tables needed. Only changes:
- Tasks: add `status = "deleted"` as valid status value
- All list queries: add `Task.status != "deleted"` filter

---

## Dependencies to Add

```toml
# pyproject.toml additions
"sentence-transformers",
"numpy",
```

---

## Definition of Done

Phase 3 is complete when:
- [ ] `life log "maths exam"` correctly deduplicates with existing "math test"
- [ ] `life digest` generates natural language summary
- [ ] `life weekly` shows 7-day summary with stats
- [ ] `life search "keyword"` returns relevant tasks and timeline entries
- [ ] `life edit <id> --title "x"` updates task title
- [ ] `life delete <id>` soft deletes task
- [ ] `life streak` shows consecutive logging days
- [ ] Embedding model loads once and is cached
- [ ] Phase 1 and 2 data and commands still work