# PSR Print Studio: Frontend

Angular web app for PSR Print Studio. It sends design specs to the backend and shows the
result in a 3D viewer built with three.js: assembled parts, their joints, and the hardware
they hold.

**Stack:** Angular 22 (standalone components, signals) · Angular Material · three.js

## Run it

The backend must be running first (`uvicorn src.api.app:app --reload` in `backend/`, port 8000).

```bash
npm install
ng serve
```

Open http://localhost:4200. During development, `proxy.conf.json` forwards `/designs`,
`/catalog` and `/health` to the backend on port 8000, so there are no CORS problems and
no hardcoded backend URLs in the code.

## Structure

| Folder | What it holds |
|---|---|
| `src/app/pages/` | Routed screens: `viewer` (3D view), `about`, `settings` |
| `src/app/components/` | Reusable UI: `side-nav` (app layout, navigation, theme toggle) |
| `src/app/services/` | `DesignApi` (backend calls, error mapping), `ColorTheme` (light/dark, saved in localStorage) |
| `src/app/models/` | `design.models.ts`: TypeScript types matching the backend's JSON (spec, manifest, plates) |
| `src/app/layout/` | `breakpoints.ts`: responsive breakpoints for TypeScript |
| `src/styles/` | Theme variables and `_breakpoints.scss` |

## How the viewer works

1. `DesignApi.build()` sends a `DesignSpec` to `POST /designs`.
2. The backend returns a **manifest**: every part, its mesh URLs and its 4×4 world matrix.
3. The viewer loads each part's GLB mesh with `GLTFLoader` and places it with that matrix
   (row-major in the manifest, transposed for three.js).
4. `OrbitControls` handles rotate and zoom (mouse and touch).

The viewer does no geometry itself; the backend computes every position.

## Patterns and conventions

- **Standalone components + signals:** no NgModules; component state lives in signals.
- **Services via dependency injection:** components never call `HttpClient` directly.
- **Error mapping:** `DesignApi` turns HTTP errors into one `DesignFailure` type
  (422 check issues, 409 questions from the AI, 0 backend not reachable).
- **Responsive layout:** below 840 px the side nav becomes an overlay (`BreakpointObserver`).
  Breakpoints are defined twice: keep `_breakpoints.scss` and `layout/breakpoints.ts` in sync.
  Supported down to 320 px width (WCAG reflow).
- **Theming:** colours come only from the CSS variables in `src/styles/`, never hardcoded.
- **Comments:** TSDoc (`/** … */`) on services and public methods.

## Tests

```bash
ng test
```

## Status

The viewer shows the assembled design. Planned next: a build-plate view with STL download,
opening saved designs by id, and real Settings and New design pages.
