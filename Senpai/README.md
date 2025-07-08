# Multimodal AI Agent

This project is a minimal prototype of a multimodal AI agent that observes a live browser session, plans a task based on a natural language command, and takes actions in the browser automatically.

## MVP Task

Use natural language (e.g., “check today’s weather on weather.com”) to trigger an agent that:

1.  Opens a browser (headless or not),
2.  Navigates to https://weather.com,
3.  Enters a ZIP code (default 10001),
4.  Clicks on the “Today” tab,
5.  Takes a screenshot of the summary panel,
6.  Outputs both a step log and screenshot.
