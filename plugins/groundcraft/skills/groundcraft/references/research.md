# Research

Use research to change a decision, not to decorate it.

## Trigger

Research when the task depends on current, external, unfamiliar, disputed, high-stakes, or explicitly requested information. Read any URL the user provides. Do not browse for stable local facts that code, runtime, tests, or configuration can establish more directly.

## Route

1. State the decision or uncertainty the research must resolve.
2. Inspect local evidence first for repository behavior.
3. Prefer current primary sources: official documentation, source code, standards, and release notes.
4. Read changelogs and migration guides when versions or behavior may have changed.
5. Use issues, pull requests, and maintainer discussions for known failures, maintenance, and unresolved edges.
6. Use forums and social discussion for lived experience and failure discovery, not as sole proof of API, security, or compatibility claims.
7. Compare source date, product version, environment, and author incentives.

Use specialized documentation, web, repository, browser, or social-research tools already available in the host. Do not add a dependency merely to perform routine research.

## Evidence record

Keep only evidence that changes the decision:

- `finding`: what the evidence supports;
- `source`: direct link or local artifact;
- `scope`: version/environment where it applies;
- `uncertainty`: contradiction or missing proof;
- `decision`: consequence for the work.

Cite current external claims near the claim. Clearly label inference.

## Stop

Stop when authoritative sources answer the decision, independent sources converge, or another search is unlikely to change the recommendation. If evidence remains conflicting, present the conflict and choose the safest reversible experiment.
