# HTML & CSS

## HTML - semantics and accessibility are the same task

1. **Semantic elements first:** `button` for actions, `a` for navigation, `nav`/`main`/`header`/`footer`/`section` for structure, `ul`/`ol` for lists, `table` for tabular data. A `div` with a click handler is a broken button (no keyboard, no focus, no screen reader role).
2. **One `h1` per page; heading levels descend without skipping.** Headings are the document outline, not font-size shortcuts.
3. **Every input has a `<label>`** (wrapping or `for`/`id`); placeholder text is not a label. Group related fields with `fieldset`/`legend`.
4. **Every `img` has an `alt`:** descriptive for content images, empty (`alt=""`) for decorative ones - omitting it entirely is the only wrong choice. Set `width`/`height` (or aspect-ratio) to prevent layout shift; `loading="lazy"` below the fold.
5. **ARIA is a repair kit, not a foundation:** no ARIA is better than wrong ARIA. Native elements before `role=` attributes; if you write `role="button"` you now owe keyboard handling, focus, and `aria-pressed` semantics by hand.
6. **Interactive elements are keyboard-reachable and focus-visible.** Never `outline: none` without a replacement focus style. Logical DOM order = logical tab order; avoid positive `tabindex`.

## CSS - architecture

7. **Follow the project's styling system** (Tailwind, CSS Modules, styled-components, BEM, vanilla) - never introduce a second one for convenience.
8. **Keep specificity low and flat:** classes over IDs and element chains; avoid `!important` (it's a specificity bankruptcy filing - acceptable only to override third-party inline styles). Modern option: `:where()` to zero out specificity, `@layer` for ordering.
9. **Design tokens as custom properties:** colors, spacing, radii, fonts as `--vars` (or the framework's theme), never hardcoded hex scattered through components. Dark mode and theming hang off this.
10. **Layout: flexbox for one dimension, grid for two.** `gap` over margin-hacks between siblings. No absolute positioning for things that should flow; no magic-number margins to "make it line up."

## CSS - correctness

11. **Responsive by default:** relative units (`rem` for type/spacing, `%`/`fr` for layout), `min()`/`max()`/`clamp()` for fluidity, mobile-first media queries (`min-width`), container queries where component-scoped response fits. Never fixed pixel widths on text containers.
12. **Respect user settings:** `rem` honors font-size preferences; wrap animation in `@media (prefers-reduced-motion: no-preference)`; support `prefers-color-scheme` if the app themes.
13. **Contrast meets WCAG AA** (4.5:1 body text, 3:1 large text/UI); color is never the only signal (add icons/text to error states).
14. **Animate `transform` and `opacity` only** (compositor-friendly); animating `width`/`top`/`margin` causes layout thrash.
15. **Don't style state in JS when CSS can:** `:hover`, `:focus-visible`, `:disabled`, `[aria-expanded="true"]` selectors over class-toggling for pure presentation.
