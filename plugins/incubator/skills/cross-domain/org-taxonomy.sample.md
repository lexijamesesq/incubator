# Organizational Structural Reference

Reference file for cross-domain discovery. Describes your JPD project's organizational taxonomy so the LLM can evaluate functional overlap from summary + structural metadata.

Put this content on a Notion page, fill in your organization's structure, and name the page's URL in the Configuration key `cross_domain.org_reference`. The reference is optional: without it `/cross-domain` judges from JPD's own summaries and field values.

**Last updated:** YYYY-MM-DD
**Update cadence:** When org changes are noticed (team renames, new squads, domain restructuring). Structure changes slowly.

---

## Product Brands

List your organization's product brands. Mark your own brand for exclusion in cross-domain queries.

- **Oakwood** — Route planning and navigation platform. Flagship product for territory management.
- **Acorn** — Foraging and cache management products. **YOUR_BRAND — exclude in Phase 1.5 Step A.**
- **Burrow** — Storage infrastructure, inventory tracking, seasonal logistics.
- **Canopy** — Shared infrastructure: identity, APIs, data sync, developer tools. Cross-brand services.

## Product Domains

Domains represent functional areas within brands. List the ones most relevant for cross-domain overlap with your work.

- **Territory Management** — Oakwood core: routes, boundaries, seasonal mapping, resource tracking, collaboration. Highest overlap surface with foraging work.
- **AI** — Canopy AI capabilities: predictive models, pattern recognition, agent infrastructure. Any AI-driven foraging idea likely intersects here.
- **Analytics** — Reporting, dashboards, admin visibility. Overlaps when foraging ideas involve data, metrics, or colony-wide visibility.
- **Canopy Platform** — Shared services: identity, APIs, data sync, developer tools, interoperability. Overlaps when ideas require infrastructure.

## Squads

Squads are the teams that build features. Knowing what a squad owns helps evaluate whether a JPD idea's summary indicates functional overlap.

### Territory Management Squads

- **TM Evaluate** — Cache assessment, quality scoring, site ranking workflows. **Highest foraging overlap.** Any idea touching cache quality, site evaluation, or retrieval optimization likely intersects with this squad's work.
- **TM Navigate** — Route planning, path optimization, territory traversal. Overlaps for foraging route efficiency, seasonal path adjustment.
- **TM Resources** — Resource mapping, yield estimation, seasonal availability tracking. **High foraging overlap.** Resource forecasting, supply chain modeling.
- **TM Collaborate** — Shared territory management, colony coordination. Overlaps for multi-forager coordination, territory sharing.

### Canopy Platform Squads

- **CP Identity** — Authentication, authorization, colony member management. Overlaps for access control, role management.
- **CP Interop** — Third-party integration, partner tools, marketplace. **High marketplace overlap.** Any idea involving content marketplace, partner tools, or interoperability.
- **CP Data** — Data analytics platform. Overlaps for foraging analytics, data infrastructure.

### Analytics Squads

- **AN Insights** — Admin analytics, colony-wide reporting. Overlaps for foraging reporting, dashboard visibility.
- **AN Predictive** — AI-powered analytics. Overlaps for AI-driven foraging insights, predictive models.

### Burrow Squads

- **BU Storage** — Cache storage management, inventory systems. **High cache overlap.** Storage-based foraging ideas, inventory tracking.
- **BU Seasonal** — Seasonal logistics, winter preparation workflows. Overlaps for seasonal foraging planning.

## Product Surface Areas

Surface areas are finer-grained feature zones within squads. Most relevant for foraging:

- **OW Route Planner** — Oakwood route planning interface (TM Navigate)
- **OW Site Scoring** — Oakwood cache site evaluation tools (TM Evaluate)
- **OW Resource Map** — Oakwood resource availability mapping (TM Resources)
- **CP Marketplace** — Partner tool marketplace (CP Interop)
- **AN Dashboards** — Admin/colony dashboards (AN Insights)
- **BU Inventory** — Cache inventory management (BU Storage)

---

## Our Domain Identifiers (for exclusion)

When filtering in Phase 1.5 Step A, exclude items with:

- **Product Brand** = Acorn

These are our own domain's items — not cross-domain signals.
