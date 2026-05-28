# TradeWind — App UI Kit

A high-fidelity, interactive recreation of the TradeWind web application (the AI-native export-ops console). Open `index.html` — it's a click-through prototype with a working sidebar that routes between four core screens.

## Run it
Open `index.html` in a browser. It loads React + Babel + Tabler Icons from CDN and the shared tokens from `../../colors_and_type.css`. No build step.

## Screens
- **Dashboard** (`Dashboard.jsx`) — manager control room: 5-up KPI strip, alert banners, active-orders table, today's tasks, upcoming deadlines, quick AI query.
- **AI Order Intake** (`AIIntake.jsx`) — chat-first intake. Demonstrates the AI-native patterns: a conversation thread, an **action log** (AI executing steps on your behalf), and an inline **clarifying question** with selectable options, alongside the live "Extracted Order" panel.
- **Sales Order Detail** (`SalesOrderDetail.jsx`) — header KPIs, warning banners, line items, packaging config, documents, and a vertical timeline with an AI summary + NL query.
- **Task Board** (`TaskBoard.jsx`) — auto-generated order checklists with progress, assignees, overdue/in-progress/locked states, plus the SOP library rail.

Nav items not recreated here (Quotes, Analytics, Rule Engine) show a placeholder noting they live in the existing production quotation-builder app.

## Components (`components.jsx`)
Shared primitives exported to `window`: `Badge`, `Btn`, `Avatar`, `Card`, `CardHead`, `Track` (progress), `Alert`, `Sidebar`, `Topbar`, `NotifBell`. All styling lives in `app.css`, keyed to the design-system tokens.

## Notes
These are cosmetic recreations for design reuse, not production logic. State is minimal (route switching, filter pills). Reuse `components.jsx` + `app.css` as the foundation for new TradeWind screens.
