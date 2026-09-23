# Layouts — shells and page types

Contents: App shell · Sidebar nav · Header bar · Collapse + mobile drawer ·
Page toolbar · Content grid · Settings page variants · Profile hero ·
Header-only shell · Auth pages · Landing page · Containers, breakpoints, RTL

---

## App shell (sidebar + header, both fixed)

The default for dashboards, admin panels and SaaS apps.

```html
<html class="h-full" lang="en" dir="ltr">           <!-- + class="dark" / "sidebar-collapsed" / "sidebar-dark" -->
<body class="h-full flex text-2sm">

  <!-- Sidebar: fixed on lg+, drawer below -->
  <aside id="sidebar"
         class="fixed inset-y-0 start-0 z-40 hidden lg:flex flex-col w-(--sidebar-width)
                bg-sidebar text-sidebar-foreground border-e border-sidebar-border
                ">
    <div class="flex items-center justify-between h-(--header-height) px-6 shrink-0">
      <a href="/" class="flex items-center gap-2.5 font-semibold text-mono">LOGO</a>
      <button id="sidebar-toggle" class="… outline icon-only sm absolute start-full top-1/2 -translate-x-1/2 rtl:translate-x-1/2 -translate-y-1/2 rounded-full size-7.5"></button>
    </div>
    <nav class="grow overflow-y-auto scroll-thin py-5 ps-5 pe-3 flex flex-col gap-1"> …nav recipe… </nav>
  </aside>

  <!-- Wrapper: pushed right by the sidebar, down by the header -->
  <div class="flex flex-col grow min-w-0 lg:ps-(--sidebar-width) pt-(--header-height)">

    <header class="fixed top-0 end-0 start-0 lg:start-(--sidebar-width) z-30 h-(--header-height)
                   flex items-stretch bg-background app-seam" data-motion="position">
      <div class="container-fixed flex items-center justify-between gap-4"> …header recipe… </div>
    </header>

    <main class="grow pt-5 pb-10">
      <div class="container-fixed"> …toolbar + content grid… </div>
    </main>

    <footer class="container-fixed flex flex-wrap items-center justify-between gap-2.5 py-5 text-2sm text-muted-foreground">
      <span>© 2026 Company</span> <nav class="flex gap-4"><a class="hover:text-primary-accent">Docs</a> …</nav>
    </footer>
  </div>
</body>
```

`container-fixed` (define once in your CSS `@layer components`):
`w-full grow px-6 xl:mx-auto xl:px-7.5 xl:max-w-(--breakpoint-xl)`.
`container-fluid`: `w-full grow px-6 xl:px-7.5`.

## Sidebar nav

```
heading:    px-2.5 pt-4 pb-1 text-xs font-medium uppercase text-sidebar-muted
link:       group flex items-center gap-3.5 rounded-lg px-2.5 py-2 text-sm text-sidebar-foreground
            hover:bg-sidebar-accent  [&.active]:bg-sidebar-accent [&.active]:text-sidebar-primary [&.active]:font-medium
icon:       size-5 shrink-0 text-sidebar-muted group-hover:text-sidebar-foreground group-[.active]:text-sidebar-primary
title:      grow truncate
badge:      ms-auto  (Badge sm outline)
arrow:      ms-auto size-4 text-sidebar-muted disclosure-chevron   (R4 rotates it; the trigger writes aria-expanded)
              [.open_&]:rotate-90 rtl:rotate-180 rtl:[.open_&]:-rotate-90
children:   flex flex-col gap-1 ms-[22px] ps-2.5 border-s border-sidebar-border   (hidden until parent .open)
child link: relative flex items-center gap-3.5 rounded-lg px-2.5 py-1.5 text-2sm text-sidebar-foreground hover:bg-sidebar-accent
            before:absolute before:-start-[15px] before:top-1/2 before:size-1.5 before:-translate-y-1/2 before:rounded-full before:bg-transparent
            [&.active]:text-sidebar-primary [&.active]:before:bg-sidebar-primary
```

Exactly one `.active` link at a time. Sections: 4–8 items per heading; more
than ~12 top-level items means the product needs a second nav level, not a
longer list.

`group` above is an HTML marker for `group-hover:` / `group-[.active]:` on the
icon. If you turn this recipe into a `.nav-link` class with `@apply`, leave
`group` out and style the icon with `.nav-link:hover svg` / `.nav-link.active svg`
— `@apply group` is a compile error in Tailwind v4.

## Header bar

Left → right (mirrors in RTL): mobile hamburger + logo (`lg:hidden`) · breadcrumb
or mega-menu · `grow` · search trigger (outline sm, icon + “Search” + Kbd `⌘K`, `hidden md:flex`) ·
icon buttons (ghost icon-only) for notifications (with `absolute -top-0.5 -end-0.5 size-2 rounded-full bg-destructive border-2 border-background`),
chat, apps · theme toggle · user avatar `size-9` opening a Dropdown (name + email header, links, Separator, Dark-mode Switch row, Log out as full-width outline button).

Mega menu items: `flex items-center gap-1.5 h-full px-2 text-sm text-secondary-foreground border-b-2 border-transparent hover:text-primary-accent` · active `text-mono border-primary font-medium`.

## Collapse + mobile drawer (12 lines of JS)

```js
const html = document.documentElement;
sidebarToggle.onclick = () => {
  html.classList.toggle('sidebar-collapsed');
  localStorage.setItem('sidebar', html.classList.contains('sidebar-collapsed') ? 'collapsed' : 'open');
};
if (localStorage.getItem('sidebar') === 'collapsed') html.classList.add('sidebar-collapsed');
// mobile
hamburger.onclick = () => { sidebar.classList.remove('hidden'); overlay.classList.remove('hidden'); };
overlay.onclick    = () => { sidebar.classList.add('hidden');    overlay.classList.add('hidden'); };
```

CSS for the collapsed state. Keep it **outside every `@layer`** (unlayered rules beat both the `:root` variables and Tailwind's utility layer; inside `@layer components` the toggle silently does nothing):

```css
@media (width >= 64rem) {
  html.sidebar-collapsed { --sidebar-width: var(--sidebar-width-collapsed); }
  html.sidebar-collapsed #sidebar:hover:not(.no-peek) { width: 280px; }        /* peek on hover */
  html.sidebar-collapsed #sidebar:is(:not(:hover), .no-peek) :is(.nav-title, .nav-badge, .nav-arrow, .nav-children, .logo-full) { display: none !important; }
  html.sidebar-collapsed #sidebar:is(:not(:hover), .no-peek) .logo-mark { display: flex; }
  html.sidebar-collapsed #sidebar:is(:not(:hover), .no-peek) .nav-heading { visibility: hidden; height: 1.75rem; padding: 0; }
  html.sidebar-collapsed #sidebar:is(:not(:hover), .no-peek) :is(.nav-link, .nav-child) { justify-content: center; }
  html.sidebar-collapsed #sidebar-toggle svg { transform: rotate(180deg); }
}
```

The toggle button sits on the sidebar edge, so the pointer is still hovering after the click. Add `no-peek` on click and drop it on `mouseleave`, otherwise the peek rule keeps the sidebar open and the button looks broken:

```js
toggle.onclick = () => { html.classList.toggle('sidebar-collapsed'); sidebar.classList.add('no-peek');
  sidebar.addEventListener('mouseleave', () => sidebar.classList.remove('no-peek'), { once: true }); };
// every nav link gets a title for the collapsed state; clicks move the active state and close the mobile drawer
sidebar.querySelectorAll('.nav-link').forEach(a => { const t = a.querySelector('.nav-title'); if (t) a.title = t.textContent.trim(); });
sidebar.querySelectorAll('.nav-link:not([data-toggle-group]), .nav-child').forEach(a => a.addEventListener('click', () => {
  sidebar.querySelectorAll('.active').forEach(x => { x.classList.remove('active'); x.removeAttribute('aria-current'); });
  a.classList.add('active'); a.setAttribute('aria-current', 'page');
  if (innerWidth < 1024) { sidebar.classList.add('hidden'); overlay.classList.add('hidden'); }
}));
```

Below `lg`: sidebar is `hidden`, shown as a drawer with an overlay
`fixed inset-0 z-30 bg-black/30 lg:hidden`. Header height drops to 60px
(tokens.css does this).

## Page toolbar

```html
<div class="flex flex-wrap items-center justify-between gap-5 pb-7.5">
  <div class="flex flex-col gap-1">
    <h1 class="text-xl font-medium text-mono">Team Members</h1>
    <div class="flex items-center gap-2 text-2sm text-secondary-foreground">
      <span>Overview of all team members and roles.</span>   <!-- or a Breadcrumb -->
    </div>
  </div>
  <div class="flex items-center gap-2.5">
    <a class="… outline">Import</a>
    <a class="… primary">Add member</a>
  </div>
</div>
```

## Content grid

```
page:    grid gap-5 lg:gap-7.5
row:     grid lg:grid-cols-3 gap-5 lg:gap-7.5 items-stretch      (2/3 + 1/3 → lg:col-span-2 on the wide card)
kpis:    grid sm:grid-cols-2 xl:grid-cols-4 gap-5 lg:gap-7.5
narrow:  max-w-3xl (forms, articles)      two-pane: lg:grid-cols-[1fr_360px]
```

Every card `h-full` so rows align. Never place bare text on the page
background between cards; give it a card or a toolbar.

## Settings page variants

- **Plain** — stacked cards, each one topic (Profile, Password, Notifications), `max-w-3xl` or full width. Save in each card footer.
- **Sidebar** — `grid lg:grid-cols-[230px_1fr] gap-5 lg:gap-7.5`; left is a sticky (`lg:sticky lg:top-[calc(var(--header-height)+1.25rem)]`) vertical Tabs list driven by scrollspy; right is the plain stack.
- **Tabs** — line Tabs under the toolbar, one card group per tab. Use when sections are unrelated.
- **Modal** — the whole settings form inside a `max-w-2xl` Modal; for quick-edit from a list.
- **Enterprise** — sidebar variant + a top summary card (plan, seats, usage bars) + danger zone card at the bottom (`border-destructive/30`, destructive outline button).

Settings row inside a card section: `grid lg:grid-cols-[200px_1fr] items-center gap-2.5 py-4` →
label `text-2sm font-medium text-mono` (+ helper `text-xs text-muted-foreground`), control in column 2, `max-w-md`.

## Profile hero (public profile, team page, company page)

```
band:     border-b border-border bg-background   (optional cover: h-40 bg-cover rounded-none)
inner:    container-fixed flex flex-col items-center lg:flex-row lg:items-end gap-5 py-7.5
avatar:   size-24 rounded-full ring-4 ring-background -mt-12 (over a cover)
name:     text-lg font-semibold text-mono   + verified icon size-4 text-primary-accent
meta:     flex flex-wrap items-center gap-4 text-2sm text-secondary-foreground [&_svg]:size-4 [&_svg]:text-muted-foreground
stats:    flex gap-7.5 → each: text-lg font-semibold text-mono / text-2sm text-secondary-foreground
tabs:     line Tabs below, in the same band (border-b already provided)
```

## Header-only shell (no sidebar)

For content-light apps and portals: header 70px with the primary nav as
mega-menu items, `container-fixed` content, optional secondary sticky sub-nav
(`sticky top-(--header-height) z-20 bg-background border-b`). Same header bar
recipe; logo goes on the start side.

## Auth pages

Two families; pick one per product and keep it for every auth screen.

**Classic** — centred card on `bg-background` (optionally a faint radial
`bg-[radial-gradient(ellipse_at_top,var(--accent),transparent_60%)]`):

```
page:   min-h-screen flex items-center justify-center p-5
card:   w-full max-w-[370px] rounded-xl border border-border bg-card shadow-xs p-10 flex flex-col gap-5
logo:   mx-auto h-8 mb-2
title:  text-lg font-semibold text-mono text-center     sub: text-2sm text-secondary-foreground text-center (with a Link)
social: grid grid-cols-2 gap-2.5 → outline buttons with brand SVG size-4
or:     Separator with label “or”
fields: Field × n · row: flex items-center justify-between → Checkbox “Remember me” + Link “Forgot password?”
submit: primary lg w-full
legal:  text-xs text-muted-foreground text-center
```

**Branded** — split screen `grid lg:grid-cols-2 min-h-screen`; start pane is
the classic form (`max-w-[370px] mx-auto`), end pane `hidden lg:flex` with
`bg-primary` (or a token gradient `bg-[linear-gradient(135deg,var(--primary),color-mix(in_oklab,var(--primary)_70%,black))]`),
logo, one headline `text-3xl font-semibold text-primary-foreground`, one
sentence, and a product screenshot in a rounded frame. In RTL the panes swap
automatically (`grid` + logical order).

Screens in the family: sign-in, sign-up, 2FA (six `size-12 text-center text-lg font-semibold` inputs with `gap-2.5`, auto-advance),
reset flow (enter email → check email → change password → password changed — each a card with an illustration `size-32` or icon
`size-12 rounded-full bg-primary/10 text-primary-accent`), welcome, account deactivated, 404 / 500
(`text-5xl font-semibold text-mono`, one line, primary button “Back to home”).

## Landing page (marketing)

Section order that converts, top to bottom — drop sections, do not reorder:

1. **Header** — `sticky top-0 z-40 bg-background/80 backdrop-blur border-b border-border`, logo · nav links `text-sm text-secondary-foreground hover:text-mono` · outline “Sign in” + primary “Get started”.
2. **Hero** — `py-20 lg:py-32 text-center`, background = token gradient wash + 2–3 soft blobs (`absolute rounded-full bg-primary/10 blur-3xl`), eyebrow Badge pill, `h1 text-4xl lg:text-6xl font-bold tracking-tight text-mono leading-[1.1] max-w-4xl mx-auto`, sub `text-lg lg:text-xl text-muted-foreground max-w-[600px] mx-auto`, two CTAs (primary lg + outline lg), social proof row (Avatar group + 5 `text-warning-accent` stars + `text-sm text-muted-foreground`).
3. **Trusted by** — `py-10` grey logos `opacity-60 grayscale hover:grayscale-0`, 5–7 logos, marquee on mobile.
4. **How it works** — 3 steps `grid md:grid-cols-3 gap-7.5`, numbered `size-10 rounded-full bg-primary/10 text-primary-accent font-semibold`.
5. **Features** — bento `grid md:grid-cols-6 gap-5` with one `md:col-span-4` hero card and `md:col-span-2` cards; each card = icon chip + title `text-lg font-semibold text-mono` + `text-secondary-foreground`.
6. **Testimonials** — 3 cards, quote `text-sm`, author row (Avatar + name `font-medium text-mono` + role `text-xs text-muted-foreground`).
7. **Pricing** — monthly/yearly pill Tabs (yearly shows a `light-success` “Save 20%” badge); 3 cards; popular plan `border-primary ring-1 ring-primary` with a primary Badge; price `text-4xl font-bold text-mono` + `/month text-muted-foreground`; features list with `size-4 text-success-accent` checks; CTA full width (primary on popular, outline elsewhere).
8. **FAQ** — `max-w-2xl mx-auto`, accordion rows `border-b border-border py-4`, question `text-sm font-medium text-mono`, chevron rotates.
9. **CTA band** — `rounded-2xl bg-primary text-primary-foreground p-10 lg:p-16 text-center`, headline + one button (`bg-background text-foreground`).
10. **Contact** — 2-col: text + form card.
11. **Footer** — `border-t border-border py-12`, `grid md:grid-cols-4 gap-7.5`, brand column + 3 link columns, bottom row `text-xs text-muted-foreground` with © and social icons.

Section rhythm `py-16 lg:py-24`, inner `max-w-6xl mx-auto px-6`, section
eyebrow (Badge pill) + `h2 text-3xl lg:text-4xl font-bold tracking-tight text-mono` + `p text-muted-foreground max-w-2xl mx-auto`, centred.

## Containers, breakpoints, RTL

- Breakpoints (Tailwind defaults): `sm 40rem · md 48rem · lg 64rem · xl 80rem · 2xl 96rem`. The shell switches at `lg`.
- `container-fixed` caps at `xl` (80rem); data-heavy screens may use `container-fluid`.
- **RTL**: set `dir="rtl"` on `<html>` only. Use `ps/pe/ms/me/start/end` and `inset-inline-*`; mirror chevrons with `rtl:rotate-180`; never `left/right` or `ml/mr` in new code. Arabic copy: keep Inter for Latin digits/UI and add `"Noto Sans Arabic"` (already in `--font-sans`), bump body to `text-sm` if the product is Arabic-first — Arabic glyphs read smaller at 13px.
- Print: `print:hidden` on sidebar/header; tables get `print:text-xs`.
