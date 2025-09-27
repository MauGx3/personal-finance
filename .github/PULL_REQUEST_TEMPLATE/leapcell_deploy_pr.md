Leapcell deploy PR template
===========================

Purpose
-------

Minimal instructions and checklist for branch-based Leapcell deployments.

Checklist
---------

- Add secrets in the Leapcell environment UI (do not commit secrets in the repo).
- Verify health probe: HTTP GET /kaithhealth -> 200 (if alias present).
- Optionally run a staging deploy to confirm build/start.

Files (examples)
-----------------

- deploy/leapcell/stack.env.example
- deploy/leapcell/README_LEAPCELL.md

Notes
-----

- Do not commit secrets. Use environment/secret manager for deploy targets.
