# FRAME Design System

## 1. Atmosphere & Identity

FRAME is a quiet evidence review workspace. It uses generous white space, thin rules, dark text, and underlined actions so reviewers can move from a claim to its source without visual noise. The comparison surface keeps the same editorial tone and adds a simple side-by-side reading moment for other candidates.

## 2. Color

| Role | Token | Value | Usage |
|---|---|---:|---|
| Surface | `--bg` | `#FFFFFF` | Page and modal surfaces |
| Text | `--ink` | `#202124` | Primary text and controls |
| Muted text | `--muted` | `#666666` | Supporting copy and metadata |
| Divider | `--line` | `#E5E5E5` | Section and card separators |
| Focus | `--focus` | `#555555` | Keyboard focus outline |

## 3. Typography

- Primary: `Noto Sans KR`, sans-serif
- UI/meta: `Manrope`, sans-serif
- Body text uses 14–15px with 1.75–1.95 line height.
- Headings use 18–25px with tight tracking.

## 4. Spacing & Layout

- Base rhythm: 4px increments, with 12px, 16px, 20px, 24px, and 32px as the common steps.
- Review workspace: two-column grid on desktop, single-column flow below 850px.
- Reading areas own their scroll; the page shell stays in the viewport.
- Modals use a 32px minimum viewport gutter and a 740px maximum wide layout.

## 5. Components

### Evidence actions
- **Structure:** timestamp button, context button, comparison button, remove button.
- **States:** default, hover, focus, playing, disabled.
- **Accessibility:** every action has visible text or an accessible label; keyboard focus is visible.

### Criterion presets
- **Structure:** job-role select, six editable criterion rows, add/remove actions.
- **States:** preset loaded, edited, reduced to the minimum three rows, and full six-row limit.
- **Accessibility:** the role select and every criterion row have a visible label and keyboard-accessible controls.

### Comparison modal
- **Structure:** native dialog, title, explanatory copy, candidate summary list, close action.
- **States:** populated, empty, focus, reduced motion.
- **Layout:** vertical stack with dividers; summaries wrap naturally for Korean text.

## 6. Motion & Interaction

- Existing workspace motion is limited to the loading spinner and native dialog behavior.
- The comparison modal opens from the clicked evidence action and respects `prefers-reduced-motion`.

## 7. Depth & Surface

The surface strategy is borders-only: thin gray rules separate reading groups, while dialogs use a single gray border and a dimmed backdrop.

## 8. Accessibility Constraints & Accepted Debt

- Keep keyboard focus visible and preserve native dialog keyboard behavior.
- Keep body text at or above 14px in the comparison surface.
- Accepted debt: the current workspace uses icon hiding rules in CSS for its restrained visual style; new comparison actions follow the same pattern to avoid a mixed visual language.
