import { Routes } from '@angular/router';
import { Analysis } from './pages/analysis/analysis';
import { About } from './pages/about/about';
import { Settings } from './pages/settings/settings';
import { Register } from './pages/register/register';
import { Login } from './pages/login/login';
import { AnalysisResults } from './pages/analysis-results/analysis-results';

export const routes: Routes = [
    { path: '', redirectTo: 'studio', pathMatch: 'full' },
    {
        path: 'studio',
        loadComponent: () => import('./features/studio-layout/studio-layout').then(m => m.StudioLayout),
    },
    { path: 'viewer', loadComponent: () => import('./pages/viewer/viewer').then(m => m.Viewer) },
    { path: "analysis", component: Analysis },
    { path: "about", component: About },
    { path: "settings", component: Settings },
    { path: "register", component: Register},
    { path: "login", component: Login},
    { path: "analysis-results", component: AnalysisResults}
];
