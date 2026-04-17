# HT-02 - Add linked resource discovery and controlled loading

## Status
- [ ] To Do
- [ ] In Progress
- [x] Done

## Purpose
Extend the HTTP tool so it can discover and selectively load the related resources needed to give the LLM a fuller view of the page.

## Context
The prompt requires the tool not only to fetch HTML, but also to resolve and load relevant JavaScript, CSS, and other assets when applicable. That must happen under explicit limits to avoid accidental crawling.

## Requirements
- Extract relevant resource links from the fetched HTML.
- Load linked resources through a controlled policy with domain, count, and size limits.
- Report which resources were loaded, skipped, or failed and why.

## Implementation Notes
- Parse `link`, `script`, and other relevant tags as needed for the MVP.
- Use same-origin or an explicit allowlist policy to avoid uncontrolled expansion.
- Log skip reasons deterministically so runs are easy to analyze.

## Definition of Done
- [ ] Relevant linked resources are discovered from the page
- [ ] Resource loading follows clear policy limits
- [ ] The result includes a transparent summary of loaded and skipped assets
- [ ] Code is clean and consistent
- [ ] Documentation is updated where needed

## Affected Files / Components
- `src/agent/tools.py`
- `src/config.py`
- `docs/algorithms.md`

## Risks / Dependencies
- Dependency: `HT-01` must provide the base page fetch.
- Risk: uncontrolled resource loading could increase latency or pull third-party content unnecessarily.

## Validation Steps
1. Run the tool on a page with external CSS and JavaScript and confirm the summary lists discovered resources.
2. Verify same-origin or allowlist enforcement and confirm skipped resources are reported clearly.
3. Test resource count and size limits.

## Follow-ups (optional)
- Add a separate future mode for broader crawl behaviour outside the MVP.
