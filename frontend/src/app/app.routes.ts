import { Routes } from '@angular/router';
import { Analysis } from './pages/analysis/analysis';
import { About } from './pages/about/about';
import { Settings } from './pages/settings/settings';

export const routes: Routes = [
    { path: '', redirectTo: 'analysis', pathMatch: 'full' },
    { path: "analysis", component: Analysis },
    { path: "about", component: About },
    { path: "settings", component: Settings }
];
