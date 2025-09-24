### Stuck Items
- **Context**: Dashboard interactions (F1–F6) remain UNVERIFIED because no browser runtime is available in-container.
- **Hypotheses**:
  - Missing graphical browser to exercise DOM interactions, canvas drawing, and responsive layout shifts.
  - Screen-reader validation requires assistive tooling not present in this environment.
- **Actionable solutions**:
  1. Serve the build locally (e.g., `python -m http.server 4173`) and open index.html in a Chromium/Playwright session to capture navigation/tab behavior.
  2. Use accessibility inspection (Lighthouse, Axe, or VoiceOver) to confirm #full-guide transcript exposure.
- **Verification steps once environment is available**:
  - Execute the manual commands in `features.json`, save screenshots or DOM dumps, and archive evidence under `evidence/` with updated hashes.
