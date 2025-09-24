### Stuck Items
- **Context**: UI interaction features (F1–F9) remain UNVERIFIED due to lack of browser automation in this environment.
- **Hypotheses**:
  - Missing graphical browser runtime to execute canvas rendering and pointer/keyboard events.
  - Clipboard and download APIs require secure context not present in container.
- **Actionable solutions**:
  1. Launch a static server (e.g., `python -m http.server 4173`) and run Playwright/Chromium against `http://localhost:4173/index.html`.
  2. Capture screenshots and network traces confirming PNG export and clipboard functionality.
- **Verification steps once environment is available**:
  - Execute scripted checks referenced in `features.json` and attach resulting evidence to `evidence/`.
