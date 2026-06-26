---
name: check-runner
description: "Run the Phase 2 solver check workflow and report PASS or FAIL."
tools: Bash, Read
---

# Robust Optimize Sanity Check

From the workspace root, run this self-check workflow before you stop editing and again
after any meaningful change.

1. Verify Python syntax on all editable modules:

```bash
cd output && find src/robust_optimize -name "*.py" -exec python3 -m py_compile {} +
```

2. Run the boundary check command:

```bash
{{BOUNDARY_CHECK_COMMAND}}
```
