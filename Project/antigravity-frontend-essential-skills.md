# Antigravity: Frontend Essential Skills

*The practical setup guide for a functional, aesthetic Prompt War 2026 site — no frontend experience required*

1. **Color & Type Lock-In**
2. **Component Foundation**
3. **Hero Flair**

**Inside:** official links • installation • setup • first workflow • useful commands

---

## 01. Color & Type Lock-In

*Decide the palette before writing any UI code, so nothing defaults to Tailwind's stock blue/gray.*

### What it does

A small, curated palette (Open Color) gives you accessible, pre-tested hex values instead of guessing at colors or falling back to framework defaults — the single fastest way to make a site look unstyled.

### Official project link

[github.com/yeun/open-color](https://github.com/yeun/open-color)

### Install

```bash
npm install open-color
```

No install needed if you're just referencing hex values directly from the repo's README — copy 4–6 values into your Tailwind config or CSS variables.

### First workflow

1. Open the repo, pick one color family as your base, one as your accent.
2. Write down 4–6 hex values and 1–2 font names before touching any component code.
3. One sentence: what should the hero communicate at a glance?

> **Tip:** If the palette would look identical on any other hackathon project, it's not specific enough yet. Adjust before building.

---

## 02. Component Foundation

*Structure before decoration — get the layout functional first.*

### What it does

Gives you accessible, pre-built pieces (buttons, forms, dialogs, nav) to assemble instead of writing them from scratch — the fastest way to a working UI with minimal frontend experience.

### Official project links

- React track: [github.com/shadcn-ui/ui](https://github.com/shadcn-ui/ui)
- Plain HTML track: [github.com/markmead/hyperui](https://github.com/markmead/hyperui)

### Install — React track

```bash
npx shadcn@latest init
npx shadcn@latest add button dialog form
```

### Install — Plain HTML track

No install. Copy the HTML/Tailwind block straight from [hyperui.dev](https://hyperui.dev) into your markup.

### First workflow

```
pick track → init/copy components → build layout → verify responsive
```

> **Tip:** Pick ONE track before writing code. shadcn/ui is React-only; HyperUI needs no framework. They don't mix.

---

## 03. Hero Flair

*One animated moment on the hero — not decoration smeared across every card.*

### What it does

Adds a single piece of visual personality (a spotlight, a gradient border, a text reveal) so the hero doesn't look like a bare template. React-only — skip this section entirely if you're on the plain-HTML track.

### Official project links

- [ui.aceternity.com](https://ui.aceternity.com) — more landing-page feel
- [github.com/magicuidesign/magicui](https://github.com/magicuidesign/magicui) — more app-tool feel

### Install

```bash
npm install framer-motion clsx tailwind-merge
```

Then copy the specific component's source from the library's site into your project.

### How to pick a safe component

Stick to components that only need Framer Motion — spotlight, text reveal, border gradient, animated beam. Skip the 3D/canvas-heavy ones (3D Card, 3D Pin, particle/aurora backgrounds); they often pull in extra dependencies like three.js that can fail to build without an obvious reason why.

> **Design reminder:** Use it once, on the hero only. A cream+terracotta palette, identical rounded cards with the same grey shadow, fade-up animation on every section, all-caps labels above every heading, and a "→" on every button are the tells of a site that looked auto-generated rather than built. None of these are wrong alone — they're wrong by default.

---

## The 3-Skill Workflow

Use them together, in this order, instead of as three unrelated choices.

| Step | Phase | Tool | Purpose |
|------|-------|------|---------|
| 01 | **Decide** | Open Color | Lock palette and type before building anything. |
| 02 | **Build** | shadcn/ui or HyperUI | Get a functional layout, structure before decoration. |
| 03 | **Polish** | Aceternity UI / Magic UI | One deliberate hero moment, React track only. |

---

## Quick Checklist

- [ ] Picked React track or Plain HTML track — not both.
- [ ] 4–6 hex colors and 1–2 fonts locked in before writing UI code.
- [ ] Structural components installed (shadcn/ui or HyperUI blocks copied in).
- [ ] At most one flair component added, on the hero only.
- [ ] Checked on mobile width, keyboard focus visible, text contrast readable.
- [ ] Screenshotted the result (via the browser subagent) and checked it doesn't look swappable onto any other hackathon project.

---

## Start Here

Save this guide. Lock in colors first, then pick your track and build structure, then add one flair moment last — not the other way around.

*Library APIs change; if a command here stops working, check the official docs linked above for the current syntax.*
