---
name: frontend-design
description: Design and build modern, responsive, high-aesthetic web user interfaces and components using Tailwind CSS, React, Vue, HTML/CSS. Trigger whenever the user asks to design a webpage, UI component, dashboard, landing page, or frontend application.
---

# Frontend Design & UI Excellence Skill

Use this skill to guide the creation of modern, visually stunning, highly accessible, and responsive user interfaces. Avoid generic, dated, or AI-cliché layouts.

## Design Philosophy & Standards

1. **Visual Hierarchy & Typography**
   - Use high-contrast, carefully scaled typography (e.g., `text-xs`, `text-sm`, `text-base`, `text-xl`, `text-3xl`).
   - Clean sans-serif font stacks (Inter, system-ui, -apple-system, Segoe UI).
   - Generous line-height (`leading-relaxed` or `leading-loose` for body text, `leading-tight` for large headings).

2. **Color Palette & Contrast**
   - Dark mode: Slate / Zinc / Neutral backgrounds (`bg-zinc-950` / `bg-zinc-900`) with subtle border lines (`border-zinc-800/80` or `border-white/10`).
   - Light mode: Off-white crisp backgrounds (`bg-slate-50` / `bg-white`) with soft borders (`border-slate-200/80`).
   - Accent colors: Refined primary accents (e.g., Indigo, Emerald, Sky, Rose, Violet) with matching muted secondary highlights (`bg-indigo-500/10 text-indigo-400`).

3. **Surface & Micro-Interactions**
   - Subtle backdrop blur (`backdrop-blur-md bg-white/70 dark:bg-zinc-900/70`).
   - Smooth transitions on interactive states: `transition-all duration-200 ease-in-out hover:-translate-y-0.5 hover:shadow-lg`.
   - Polished shadows: Layered, diffuse shadows (`shadow-sm`, `shadow-md`, `shadow-xl shadow-indigo-500/5`).

4. **Component Best Practices**
   - **Cards**: Rounded corners (`rounded-2xl` or `rounded-xl`), subtle borders, consistent padding (`p-6`).
   - **Badges / Tags**: Pill shapes (`rounded-full px-2.5 py-0.5 text-xs font-medium`), distinct background and text tone.
   - **Buttons**: Clear visual hierarchy (Primary filled with subtle hover glow, Secondary with border/ghost, Icon buttons with tooltip feel).
   - **Data Visualizations**: Clean tabular layouts with sticky headers, zebra striping on demand, inline status badges.

5. **Responsive Execution**
   - Mobile-first approach (`grid-cols-1 md:grid-cols-2 lg:grid-cols-3`).
   - Flexible containers with clear max-widths (`max-w-7xl mx-auto px-4 sm:px-6 lg:px-8`).
