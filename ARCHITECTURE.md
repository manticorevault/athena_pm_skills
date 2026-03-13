# PM Skills Marketplace — Architecture & Engineering Decisions

This document outlines the architectural patterns, technical decisions, and AI integration principles utilized in the **PM Skills Marketplace for Antigravity**.

As AI capabilities evolve from simple text generation into complex, automated "Harness Engineering," the structure of prompts and workflows must evolve alongside them. This project adheres to **2026 Best Practices for Context Engineering and Token Efficiency**.

---

## 🏗 System Architecture

The project is structured entirely natively for the Antigravity IDE. It relies on two fundamental concepts: **Skills** and **Workflows**.

- **`/skills` (The Knowledge Base)**: Static, markdown-based domain knowledge (e.g., Teresa Torres' Opportunity Solution Tree). They act as standard operating procedures (SOPs) for the AI.
- **`/workflows` (The Runbook)**: User-triggered commands (e.g., `/strategy` or `/discover`) that *chain* multiple skills together in a sequential, deterministic flow.
- **`/scripts` (Deterministic Delegation)**: Traditional Python scripts executed by Antigravity to handle deterministic tasks (like web scraping or mathematical formatting) that LLMs struggle with.

---

## 🧠 Context Engineering & Token Efficiency

In 2026, blindly dumping paragraphs into YAML front matter is an anti-pattern known as "Context Bloat." As the number of available skills scales (65+ and counting), Antigravity expends costly compute tokens just scanning the directory surface area to figure out what tools are available.

### High-Density Keyword Tagging
To combat context bloat without losing intent, we utilize **Modular Prompt Architecture**:

1. **Surface Area Minification**: The YAML `description` headers of `SKILL.md` and workflow files are stripped of conversional filler (e.g., "This skill is used for mapping user assumptions...").
2. **Density Tags**: Descriptions are replaced with hyper-dense, comma-separated keywords and capability tags (e.g., `capabilities: [pricing_analysis, battlecard_generation]`). 
3. **Optimized Routing**: This gives the Antigravity router model a microscopic token footprint to scan when deciding *which* tool is right for the user's intent.

### Deferred Context Loading
We do not truncate or destroy the detailed instructional intent just to save tokens. Instead, the rich, nuanced instructions (the "SOP") are moved *below* the YAML divider into the Markdown body. 

Antigravity only loads this heavy instructional context into its active working memory **after** it has decided to execute the specific tool based on the density tags. This ensures 100% intent preservation while saving thousands of tokens on every user query.

---

## 🕸️ Tooling & Harness Engineering

### The "Self-Healing" Web Scraper (Playwright)
Product Managers spend hours on competitive analysis. Instead of relying on the LLM's static training data or requiring the user to manually paste competitor pricing, we delegate this to a deterministic Python script.

**Decision: Playwright over BeautifulSoup**
- **The Tradeoff**: BeautifulSoup is incredibly fast and lightweight. However, it cannot execute JavaScript. 
- **The Reality**: The vast majority of modern B2B SaaS competitor websites (React, Vue, Next.js) render pricing tables and positioning statements dynamically on the client side. 
- **The Solution**: We utilize **Playwright** (`playwright install chromium`) to launch headless browsers. It seamlessly renders modern JavaScript apps and bypasses basic anti-bot blockers.

**The Harness Flow (`/competitive-analysis`)**:
1. The user provides a list of competitor URLs.
2. The Antigravity agent executes the Playwright Python script (`.agents/scripts/market_research/scrape_competitor.py`).
3. The script extracts live `<title>`, `<h1>`, `<h2>`, and pricing DOM elements into a structured JSON.
4. Antigravity reads the deterministic JSON and feeds it into the `pm-market-research` analytical frameworks to generate a real-time, highly accurate battlecard.

### The Power of Markdown
All AI logic remains in `.md` files. Markdown is the native language of Large Language Models. By structuring YAML headers, `##` Headings, and `[User Intent]` brackets mathematically, we ensure the agent perfectly follows deterministic runbooks without writing complex traditional code orchestrators.
