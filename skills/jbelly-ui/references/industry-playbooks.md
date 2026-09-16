# Industry playbooks — what buyers of the best-selling templates expect

Derived from a study of the top-selling, highest-rated commercial templates in
each business category (sales in the tens to hundreds of thousands, ratings
4.5–4.9). People bought those experiences repeatedly; the patterns below are
what they were buying. Use them as the *baseline* for a product in that
industry, then apply the personality so the product is not a clone.

Contents: Cross-industry baseline · What top sellers do that average ones don't ·
SaaS / startup · Corporate / consulting / agency · Admin & ops products ·
E-commerce · Restaurant & food · Clinic, wellness & nutrition · Education / LMS ·
Real estate & directories · Finance / fintech · Travel & booking

---

## Cross-industry baseline (every top template ships this)

- **Many demos, one system.** 10–100 variants that are recognisably the same
  product with different personality: that is the tokens + personality model.
- **Header behaviours**: sticky on scroll (shrinks from 70 → 60px), transparent
  over a hero then solid, mega menu for ≥ 6 sections, off-canvas menu on
  mobile with the primary CTA inside it.
- **One-click completeness**: every page state exists (auth, 404/500, empty,
  coming-soon, maintenance, legal); buyers count pages.
- **Dark mode, RTL, i18n** are expected, not premium.
- **Performance is a feature buyers name**: 90+ PageSpeed, lazy images, small
  JS. Budget: first screen < 200KB JS, LCP < 2.5s.
- **Accessibility level named** (WCAG 2.1/2.2 AA) — the newest top sellers
  advertise it.
- **Live customiser**: colour, font, radius, header layout switchable without
  code = tokens + personality file.
- **Documentation and support** rank top-3 in every review set; for a product
  this means in-app help (tooltips for jargon, a `?` shortcut sheet) and a
  docs link in the footer.

## What top sellers do that average ones don't

1. **Niche dashboards / demos** (5+ industries) rather than one generic — a
   product should have role-specific home screens (owner, clinician, agent).
2. **Complete apps inside** (chat, calendar, kanban, invoices, email,
   file manager, tickets) — reuse the patterns file; users expect them to
   look native to the product.
3. **Search that feels instant**: AJAX/autocomplete with grouped results,
   under 100ms perceived.
4. **Sticky conversion element**: sticky add-to-cart, sticky "Enrol", sticky
   booking bar, sticky search on results pages.
5. **Front-end dashboards for end users** (agents, owners, students,
   partners) — the same shell recipe, fewer nav items, softer density.
6. **Trust above the fold**: ratings, sales/patient counts, certifications,
   logos, before/after.
7. **Booking / checkout in ≤ 4 steps** with a visible stepper and a price that
   updates live.
8. **Half-map layouts** for anything with a location (listings, clinics,
   branches).
9. **Layout options per user**: vertical / horizontal / compact / detached
   nav; 2–3 themes; density — all preferences, persisted.
10. **A landing page for the product itself** (one-page, pricing, jobs).

---

## SaaS / startup (marketing site + product)

Feeling: clear, fast, credible. Presets: `theme-neo` (bold) or `theme-mint`
(friendly); B2B → `theme-slate`.

**Pages:** home (≥ 3 home variants over time for A/B), features, pricing,
integrations, customers/case studies, about, careers, blog, changelog, docs,
contact, legal, status; app: auth family, onboarding, dashboard, settings,
billing.

**Home order (layouts.md § Landing)**: hero → trust logos → how it works →
features (bento) → testimonials → pricing → FAQ → CTA → footer. Hero copy:
headline ≤ 8 words, sub ≤ 25 words, 2 CTAs (primary "Start free", outline
"Book a demo"), social proof line under them.

**Rules**
- Pricing: 3 plans, monthly/yearly toggle with the saving badge, popular plan
  highlighted, feature list ≤ 8 rows per plan, one CTA per plan, enterprise
  as "Contact sales".
- One lead form per page maximum; newsletter only in the footer.
- Product screenshots in a device-less rounded frame with a hairline border
  and `shadow-md`, never a floating laptop mock-up.
- Onboarding: 3-step checklist card on the first dashboard visit, dismissable,
  progress persisted.
- Changelog and status pages use the list-card + badge recipes; they signal a
  living product.

## Corporate / consulting / agency

Feeling: established, precise, human. Presets: `theme-slate` or
`theme-editorial` (agency).

**Pages:** home, services (index + detail per service), industries, case
studies (index + detail with results numbers), team (+ profiles), about,
careers (+ job detail), insights/blog, contact (multi-location map), request
a quote / book a consultation, calculators where relevant.

**Rules**
- Hero is split (copy start, image end) or a full-bleed photo with a
  left-aligned copy block; never a centred generic hero.
- Services grid 3-up with an icon chip + title + one sentence + "Learn more"
  link; every service detail ends with a consultation CTA.
- Case study cards show **a number** (result) as the largest element.
- Team profiles: photo aspect 3:4, name, role, 2 links; hover reveals bio.
- Contact: form on the start side, map + locations list on the end side;
  multi-location = tabs above the map.
- Quote / cost calculator: 3–6 inputs, live total, "Get a detailed quote"
  button; result card uses the KPI recipe.
- Sticky "Book a consultation" outline button in the header on inner pages.

## Admin & ops products (internal tools, back-offices, B2B consoles)

Feeling: dense, predictable, fast. Presets: `theme-graphite` (ops/fintech),
`theme-slate` (enterprise), `theme-clinic` (health).

**Screens:** role dashboards (≥ 2 roles), list + detail for every entity,
settings (sidebar variant), members & roles/permissions matrix, audit log,
notifications centre, integrations, API keys, billing & plans, import/export
wizard, activity/timeline, search palette.

**Rules**
- Sidebar ≤ 12 top-level items; group with headings; badge counts on inbox-type
  items only.
- Every list is a Table card with toolbar, saved views, column chooser,
  density toggle, bulk bar, URL-synced filters (ux-behaviours.md).
- Detail in a drawer first; full page for records with > 12 fields or
  sub-lists.
- Permissions: matrix table (roles × capabilities) with Switch cells and a
  "Copy from role" action.
- Import wizard: upload → map columns (Select per column, sample rows) →
  validate (error count + downloadable report) → import (progress) → summary.
- Dashboards follow the blueprint in patterns.md; every KPI drills into its
  filtered list.
- Keyboard: palette, list navigation, `?` sheet — expert users judge the
  product on this.
- Offer layout preferences (collapsed sidebar, density, theme) in
  Settings → Appearance.

## E-commerce

Feeling: product-first, fast, trustworthy. Presets: `theme-mint` (consumer),
`theme-editorial` (fashion/lifestyle), `theme-graphite` (electronics/B2B).

**Pages:** home, category (grid/list, 2–6 columns), product, search results,
cart (page + slide-in panel), checkout (1–3 steps), order confirmation,
account (orders, addresses, wishlist, returns), wishlist, compare, brand /
collection, lookbook, FAQ/shipping/returns, blog.

**Flows & rules**
- Header: logo · search (full-width on mobile, instant suggestions with
  product thumbnails and SKU match) · account · wishlist · cart with count;
  mega menu with category images.
- Category page: filters in a start sidebar on desktop (price slider,
  swatches, checkboxes, active chips + clear), off-canvas on mobile; sort
  select; 24 products per page; **AJAX** filtering without reload; quick-view
  modal; hover shows second image + "Add to cart".
- Product page: gallery (thumbs + zoom + fullscreen), title, price with
  compare-at, rating count, variant swatches (colour/image/label), quantity,
  **sticky add-to-cart bar** on scroll (mobile bottom), delivery estimate,
  trust row (secure payment, returns, support), tabs (description, specs,
  reviews), related + recently viewed.
- Cart panel slides in on add (Drawer recipe) with subtotal and checkout
  button; cart page allows quantity edit, coupon, shipping estimate.
- Checkout: express pay buttons first, guest checkout, 3 steps max
  (information → shipping → payment) or single page; order summary sticky on
  the end side; progress stepper; errors inline.
- Mobile: bottom navigation bar (Home · Categories · Search · Wishlist ·
  Cart) with counts — buyers name this feature.
- Performance: images WebP + lazy, LQIP placeholders; product grid reserved
  heights.

## Restaurant & food

Feeling: appetising, warm, effortless. Presets: `theme-editorial` (fine
dining) or `theme-mint` (casual/delivery).

**Pages:** home, menu (categories, item photos optional, dietary icons,
multiple sizes/prices), reservations, order online / delivery, gallery,
events & private dining, about/chef/team, locations & hours, gift cards,
contact, blog/news.

**Rules**
- Hero: full-bleed photography with a short serif headline, hours + address +
  "Reserve" and "Order" CTAs visible without scrolling; phone number tappable.
- Menu: sections as anchored tabs (sticky under the header), item rows with
  dotted leaders to prices, dietary/allergen icons with a legend, "Chef's
  pick" badge; PDF download link; prices with currency once per section.
- Reservation: date · time · party size → available slots as pill buttons →
  contact details → confirm; ≤ 3 steps, confirmation by email/SMS;
  fallback link to a booking provider.
- Online ordering: category rail + item cards with add buttons, cart panel,
  pickup/delivery toggle with time slots, checkout ≤ 2 steps.
- Location card: map, hours table with "Open now" badge, parking/transport
  note.
- Photography is the design; keep UI chrome minimal and text short.

## Clinic, wellness & nutrition

Feeling: calm, credible, private. Preset: `theme-clinic`; `theme-mint` for
consumer wellness.

**Marketing pages:** home, services/departments (index + detail),
practitioners (index + profile with credentials, languages, availability),
book an appointment, pricing/packages/plans, patient stories/testimonials,
before & after (with consent), FAQ, insurance/partners, locations & hours,
blog/education, contact, emergency notice.

**Product (patient portal / clinic admin):** appointments (calendar + list),
patients (list + record with tabs: overview, plans, measurements, notes,
files, billing), meal plans / programmes (builder + templates + assignment),
food database, progress tracking (charts), messaging, invoices & payments,
reminders, consent & privacy settings, reports.

**Rules**
- Booking: department/service → practitioner (optional) → date & time from a
  real availability grid → patient details → confirm; ≤ 4 steps; show
  duration and price per service; confirmation with add-to-calendar and
  reschedule/cancel links.
- Practitioner cards: photo, name, credentials, specialities as badges,
  languages, next available slot, "Book" button.
- Timetable/department schedule: week grid with practitioner columns;
  mobile collapses to a per-day list.
- Trust: credentials, accreditations, patient counts, star rating — above
  the fold; privacy statement near every form.
- Patient records: header card (avatar, name, age, key measurements as
  compact KPIs), tab nav, right-side "next appointment" card; clinical values
  use `tabular-nums` and unit labels; out-of-range values badge `warning`, not
  red alone.
- Progress charts: line chart with target band (`primary/10` fill),
  annotations for plan changes; measurement entry via inline edit.
- Meal-plan builder: day tabs × meal rows; drag foods from a searchable panel
  (dnd with keyboard alternative); nutrient totals bar updates live vs
  targets.
- Reminders and messages: templates, quiet hours, opt-out — visible
  settings.
- Copy: plain language, no fear; Arabic-first products set body 14px and
  line-height 1.7.

## Education / LMS

Feeling: encouraging, structured, clear. Presets: `theme-mint` (K-12 /
consumer) or `theme-slate` (university / corporate training).

**Pages:** home (per audience), course catalogue, course detail, instructor
profile, learning screen (player + curriculum), student dashboard, quizzes
and results, certificates, events (+ tickets), pricing/memberships, blog,
about, contact.

**Rules**
- Catalogue: search with autocomplete; filters visible by default: category,
  level, price (free/paid), rating, language; sort by popular/new/rating;
  cards: thumbnail 16:9, category badge, title (2 lines), instructor, rating
  + count, lessons/duration meta, price (with strike-through), wishlist.
- Course detail: hero with title, short pitch, rating, enrolled count,
  instructor chip, price card **sticky on the end side** with "Enrol" and
  what's included; tabs: overview, curriculum (accordion by section with
  lesson durations and preview badges), instructor, reviews, FAQ.
- Learning screen: focus layout (no app sidebar), video/player top, curriculum
  in a collapsible end panel, progress bar in the header, "Next lesson"
  primary button, notes/Q&A tabs below.
- Student dashboard: continue-learning cards with progress rings, upcoming
  live sessions, certificates, streak/goals (gamification kept subtle).
- Quiz: one question per screen, progress, timer visible, review screen with
  explanations; certificates downloadable as PDF with a share link.
- Instructor dashboard: courses table, earnings KPIs, student list, reviews.

## Real estate & directories

Feeling: confident, spatial, informative. Presets: `theme-slate` or
`theme-editorial` (luxury).

**Pages:** home with search hero, results (grid / list / **half-map**),
listing detail, agents & agencies (index + profile), compare, saved searches
with email alerts, submit a listing (front-end wizard), user/agent dashboard
(listings, leads, favourites, invoices), mortgage calculator, neighbourhood
guides, blog, contact.

**Rules**
- Search hero: status tabs (Buy / Rent / Commercial) + location (autocomplete
  with geolocation) + type + price + beds → Search; advanced filters in a
  modal.
- Results: half-map split `lg:grid-cols-[1fr_minmax(420px,45%)]`, list on the
  start side; sticky search bar; hovering a card highlights its pin; "Search
  as I move the map" toggle; sort; 12–20 results per page; card: image
  carousel, status badge, price prominent, beds/baths/area meta with icons,
  agent avatar, favourite + compare icons.
- Listing detail: gallery grid (1 large + 4) with "View all photos", price +
  address + meta strip, description, features grid, floor plans (tabs), map,
  video/virtual tour, similar listings; **sticky end-side agent card** with
  inquiry form (name, email, phone, message pre-filled) + "Schedule a tour"
  (date/time picker) + WhatsApp/phone buttons.
- Submit listing wizard: 5 steps (basics → location with map pin →
  details/features → media upload → pricing/publish), autosave drafts.
- Compare: up to 4 columns, sticky first column, differences highlighted.
- Directory variant: categories grid on home, listing cards with rating and
  open-now badge, claim-listing flow, reviews with owner replies.

## Finance / fintech

Feeling: precise, secure, calm. Preset: `theme-graphite` (data-heavy) or
`theme-slate` (banking/insurance).

**Pages/screens:** marketing home with a calculator in the hero (loan,
savings, ROI), products/plans comparison, security & compliance page,
rates/fees table, help centre; app: overview with balances and cash-flow
chart, transactions table (search, categories, export), transfers/payments
wizard, cards management, budgets/goals, statements, KYC onboarding wizard,
notifications/alerts, security settings (2FA, sessions, devices).

**Rules**
- Numbers are the interface: `tabular-nums`, right-aligned, consistent
  decimals, currency symbol position by locale, negative in `destructive`
  **with** a minus sign, deltas with arrow icons.
- Transactions: dense table (compact density), category chips with icons,
  merchant logos as avatars, inline search, date grouping headers, running
  balance column, export respects filters.
- Transfer wizard: recipient → amount (with fee and arrival estimate live) →
  review → confirm (2FA) → receipt; ≤ 4 steps; amounts confirmable in words
  on review.
- Calculators: sliders + inputs paired; result card updates live; "Apply"
  CTA next to the result.
- Security signals: last login, device list, session timeout notice, masked
  numbers with reveal; never auto-fill sensitive fields.
- Charts: cash-flow (in/out bars) + balance line; no rainbow; comparison
  period selector.
- Onboarding/KYC: stepper, document upload with camera on mobile, progress
  saved, status page (pending/approved) with next steps.

## Travel & booking (hotels, tours, rentals, activities)

Feeling: inspiring, then reassuring. Presets: `theme-editorial` (boutique),
`theme-mint` (activities), `theme-slate` (business travel).

**Pages:** home with search box over imagery, results (list + map), detail
(rooms/tour/vehicle), booking/checkout, confirmation, user dashboard
(bookings, invoices, messages, wishlist), partner/owner dashboard (listings,
calendar, pricing, bookings, payouts), destination/guide pages, offers,
reviews, FAQ, contact.

**Rules**
- Search box: destination (autocomplete) · dates (range picker with
  presets) · guests (stepper popover) · Search; tabs by product type (Hotel ·
  Tour · Car). Sticky compact version on results.
- Results: filters start side (price, rating, amenities, type, cancellation),
  map toggle / half-map, sort (recommended, price, rating); cards: image
  carousel, name, rating badge + review count, location line, key amenities
  icons, **price per night/person with total for the stay**, "Free
  cancellation" light-success badge.
- Detail: gallery grid, sticky end-side booking card (dates, guests, rate
  options with/without extras, live total with fee breakdown, "Reserve"
  primary), amenities grid, map, policies, reviews with rating breakdown
  bars, similar items.
- Booking: ≤ 3 steps (details → payment → confirmation); guest form with
  password-manager-friendly fields; price summary sticky; countdown for held
  rates only if real.
- Availability calendar: month grid with prices per day, unavailable days
  struck, seasonal pricing visible on hover; owner side edits by drag-select.
- Partner dashboard: calendar-first, booking requests inbox, payouts KPIs,
  iCal sync settings.
- Confirmation: itinerary card, add-to-calendar, map/directions, manage
  booking link; email mirrors the page.
