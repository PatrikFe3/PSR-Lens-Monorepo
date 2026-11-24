export const BREAKPOINTS = { phoneMin: 320, tablet: 600, desktop: 840 } as const;
export const COMPACT_LAYOUT = `(max-width: ${BREAKPOINTS.desktop - 0.02}px)`;