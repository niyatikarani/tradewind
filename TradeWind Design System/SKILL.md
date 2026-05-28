---
name: tradewind-design
description: Use this skill to generate well-branded interfaces and assets for TradeWind, an AI-native B2B export-operations SaaS for Indian food & spice exporters, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files.

Key files:
- `README.md` — product context, content & visual foundations, iconography, and a full file manifest. Read this first.
- `colors_and_type.css` — the source of truth for all design tokens (colors, type scale, spacing, radii, shadows). Link or copy this into anything you build.
- `assets/` — logo and logomark (SVG). Placeholder mark — replace if a real one is supplied.
- `preview/` — small specimen cards (colors, type, spacing, components incl. the AI-native chat / action-log / clarifying-question patterns). Good reference for exact component styling.
- `ui_kits/app/` — the TradeWind app UI kit: reusable JSX components (`components.jsx`, `Dashboard.jsx`, `AIIntake.jsx`, `SalesOrderDetail.jsx`, `TaskBoard.jsx`) and an interactive `index.html`. Copy these as a starting point for new screens.

Quick rules of thumb (full detail in README): Inter font, Tabler Icons (webfont CDN), slate-neutral UI on `#f1f5f9`, a single emerald accent (`#10b981`), white cards with 1px `#e2e8f0` borders + `10px` radius + a soft `0 1px 3px` shadow, and a strict green/amber/red status language. Sentence case everywhere; no emoji in chrome; SKUs and order numbers are monospace. The product is AI-native — lean on the conversation, action-log, and clarifying-question patterns.

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, copy assets and read the rules here to become an expert in designing with this brand.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.
