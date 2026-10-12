import { Service, signal } from '@angular/core';

export type ThemeColor = 'light-theme' | 'dark-theme';

@Service()
export class ColorTheme {
    private readonly storageKey = 'psr-theme';

    readonly theme = signal<ThemeColor>(
        this.getInitialTheme()
    );
    
    constructor() {
        this.applyTheme(this.theme());
    }

    toggleTheme(): void {
        const nextTheme: ThemeColor =
            this.theme() === 'light-theme'
            ? 'dark-theme' : 'light-theme';

        this.setTheme(nextTheme);
    }

    setTheme(theme: ThemeColor): void {
        this.theme.set(theme);
        this.applyTheme(theme);
        localStorage.setItem(this.storageKey, theme);
    }
    
    private applyTheme(theme: ThemeColor): void {
        const root = document.documentElement;

        root.classList.remove('light-theme', 'dark-theme');
        root.classList.add(theme);
    }

    private getInitialTheme(): ThemeColor {
        const savedTheme = localStorage.getItem(this.storageKey);

        if (
            savedTheme === 'light-theme' ||
            savedTheme === 'dark-theme'
        ) {
            return savedTheme;
        }

        return 'light-theme';
        }
    }
