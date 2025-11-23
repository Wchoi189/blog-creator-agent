# Autonomous Execution Guidelines

## Core Principles

This document defines the protocols for autonomous execution of the Blog Creator migration project. Follow these guidelines strictly to ensure efficient, uninterrupted progress.

## 1. Autonomous Operation Mode

### 🚫 NO Interruptions Policy

**CRITICAL**: Execute tasks **without** asking for permission or confirmation at each step.

**You MUST**:
- ✅ Make implementation decisions independently
- ✅ Choose reasonable default values when options exist
- ✅ Fix errors and issues as they arise
- ✅ Continue to next task when current task completes
- ✅ Auto-transition between Parts (1→2→3→4)

**You MUST NOT**:
- ❌ Ask "Should I proceed with...?"
- ❌ Request approval for standard operations
- ❌ Wait for confirmation between tasks
- ❌ Stop execution unless encountering critical blockers

### ⚡ Continuous Execution

Work through tasks in sequence without pausing:

```
Task 1.1 → Task 1.2 → Task 1.3 → ... → Part 1 Complete
→ Part 2 Start → Task 2.1 → ... → Part 2 Complete
→ Part 3 Start → ... → Part 4 Complete
→ Final commit & push
```

## 2. Decision-Making Authority

### When to Choose Independently

You have full authority to:

1. **Technology choices** (within project spec)
   - Example: Choose bcrypt for password hashing
   - Example: Use SQLAlchemy for ORM

2. **Implementation details**
   - File structure variations
   - Variable naming
   - Code organization

3. **Default configurations**
   - Port numbers (8000 for backend, 3000 for frontend)
   - Timeout values
   - Cache durations

4. **Error handling strategies**
   - Retry logic
   - Fallback mechanisms
   - Error messages

### When to Ask for Input

**ONLY** stop and ask when:

1. **Critical blocker** that prevents all progress
   - Example: Missing required API keys that can't be mocked
   - Example: Fundamental architecture conflict

2. **Security concern** with user data
   - Example: Uncertain about data privacy implications

3. **Breaking change** to existing functionality
   - Example: Need to delete user data

4. **External account required** that you can't create
   - Example: Need user's GitHub credentials

## 3. Progress Tracking

### Update Plan Files Silently

After each task completion:

1. **Update task status** in relevant PART_N file
   - Change `[ ]` to `[x]`
   - Update progress percentage

2. **Update README.md** progress tracker
   - Update overall percentage
   - Change status icons (🔄 → ✅)

3. **DO NOT output updates** to user
   - Updates should be silent file edits
   - Don't say "I'm updating the plan file..."

### Example (Silent Update)

```markdown
<!-- Before -->
- [ ] Task 1.1: Initialize FastAPI Project

<!-- After -->
- [x] Task 1.1: Initialize FastAPI Project ✅
```

## 4. Commit Strategy

### When to Commit

Create git commits at these milestones:

1. **After each Phase** within a Part
   - Example: "feat(backend): complete Phase 1.1 - Project Setup"

2. **After completing full Part**
   - Example: "feat: complete FastAPI backend (Part 1)"

3. **Before starting new Part**
   - Ensures clean checkpoint for rollback

### Commit Message Format

```
<type>(<scope>): <description>

[optional body]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Adding tests

**Examples**:
```bash
git commit -m "feat(backend): add FastAPI project structure and core endpoints"
git commit -m "feat(frontend): initialize Next.js app with Tailwind CSS"
git commit -m "feat(collab): integrate Yjs CRDT for real-time editing"
git commit -m "feat(deploy): add Docker containers and CI/CD pipeline"
```

### Push Strategy

**Push to remote**:
- After completing each Part (1, 2, 3, 4)
- Use: `git push -u origin <branch-name>`
- Retry on network failure (up to 4 times with exponential backoff)

## 5. Error Handling

### Handling Errors Autonomously

When errors occur:

1. **Analyze the error** - Read error message carefully
2. **Attempt fix** - Apply most likely solution
3. **Retry operation** - Test if fix worked
4. **Try alternative** - If first fix fails, try another approach
5. **Document** - If resolved, note the issue in code comments

### Common Error Patterns

| Error Type | Auto-Fix Strategy |
|------------|-------------------|
| Dependency conflict | Update version constraints |
| Import error | Check file paths, fix imports |
| Type error | Add proper type annotations |
| Test failure | Fix logic, update test expectations |
| Connection error | Add retry logic, check URLs |
| Auth error | Check token handling, add mock |

### When to Escalate

Only stop execution if:
- **3+ fix attempts failed** for critical issue
- **Circular dependency** can't be resolved
- **Missing external dependency** (API key, etc.)

## 6. Testing Strategy

### Run Tests Automatically

After implementing features:

```bash
# Backend
cd backend
pytest tests/ -v

# Frontend
cd frontend
npm test
```

If tests fail:
1. ✅ Fix the failing test or code
2. ✅ Re-run tests
3. ✅ Continue when passing

### Test Coverage Goals

- Backend: 90%+ coverage
- Frontend: 80%+ coverage

Don't stop for minor coverage gaps - document and continue.

## 7. Code Quality

### Automatic Linting

Run linters before committing:

```bash
# Backend
ruff check backend/ --fix

# Frontend
cd frontend && npm run lint -- --fix
```

Auto-fix issues when possible. Skip minor style issues if blocker.

## 8. Documentation

### Update as You Build

For each new feature:

1. **Code comments** - Add docstrings to functions
2. **README updates** - Update setup instructions if needed
3. **API docs** - FastAPI auto-generates, ensure models are documented

### Don't Create Extra Docs

**DO NOT** proactively create:
- Separate architecture documents (unless requested)
- Extensive tutorials
- Marketing materials

Focus on **implementation**, not documentation.

## 9. Time Management

### Efficiency Prioritization

Optimize for speed:

1. **Reuse existing code** - Copy from src/ when applicable
2. **Use defaults** - Don't over-configure
3. **Skip premature optimization** - Get it working first
4. **Parallel operations** - Run independent tasks concurrently

### Avoid Time Sinks

Don't spend excessive time on:
- Perfect code formatting
- Extensive refactoring
- Edge case handling (cover main cases first)
- Over-engineering solutions

## 10. Communication Style

### Keep User Informed

Provide **brief** progress updates:

**Good**:
```
Creating FastAPI backend structure...
✅ Project initialized
✅ Auth endpoints created
✅ Document processing implemented
Moving to Phase 1.4...
```

**Bad** (too verbose):
```
Now I'm going to create the backend directory structure.
First, I'll create the backend folder. Then I'll create
the main.py file inside it. After that, I'll add the
FastAPI imports. Then I'll create the app instance...
[continues for paragraphs]
```

### Progress Indicators

Use visual indicators:

- ✅ Completed
- 🔄 In Progress
- ⏸️ Pending
- ❌ Failed (rare - fix instead!)

## 11. Part Transitions

### Auto-Advance to Next Part

When Part N is 100% complete:

```python
# Pseudo-code for transition
if part_complete:
    commit_changes(f"feat: complete {part_name}")
    push_to_remote()
    update_readme_progress()
    start_next_part()  # NO pause, NO asking
```

**Example transition**:
```
✅ Part 1 Complete - Backend fully functional
📦 Committing changes...
📤 Pushing to remote...
🚀 Starting Part 2 - Frontend Development...
```

## 12. Final Delivery

### Completion Checklist

When all parts complete:

- [x] All tasks marked complete in plan files
- [x] All tests passing
- [x] All code committed and pushed
- [x] README.md updated
- [x] Create summary report

### Summary Report Format

```markdown
# Migration Complete ✅

## Summary
- **Duration**: X hours
- **Commits**: N commits
- **Tests**: X/X passing
- **Coverage**: Backend X%, Frontend Y%

## Deliverables
✅ FastAPI backend with 20+ endpoints
✅ Next.js frontend with Tiptap editor
✅ Real-time collaboration (Yjs)
✅ GitHub publishing integration
✅ Docker deployment setup
✅ CI/CD pipeline configured

## Next Steps
1. Review code at: [branch URL]
2. Test locally: docker-compose up
3. Deploy to production
4. Monitor metrics

## Notes
[Any important notes or issues encountered]
```

## Quick Reference

### ✅ DO
- Execute autonomously
- Fix errors independently
- Make reasonable choices
- Update plans silently
- Commit after phases
- Push after parts
- Keep moving forward

### ❌ DON'T
- Ask for permission at each step
- Wait for confirmation
- Over-explain every action
- Create unnecessary docs
- Stop for minor issues
- Over-engineer solutions
- Doubt your decisions

## Remember

> **"Act first, ask never (unless critical blocker)"**

Your goal is **completed migration**, not perfect code. Ship fast, iterate later.

---

**Execute with confidence. The user trusts your judgment.**
