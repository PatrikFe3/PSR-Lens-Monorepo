import { Routes } from '@angular/router';
import { Analysis } from './pages/analysis/analysis';
import { About } from './pages/about/about';
import { Settings } from './pages/settings/settings';
import { Register } from './pages/register/register';
import { Login } from './pages/login/login';

export const routes: Routes = [
    { path: '', redirectTo: 'analysis', pathMatch: 'full' },
    { path: "analysis", component: Analysis },
    { path: "about", component: About },
    { path: "settings", component: Settings },
    { path: "register", component: Register},
    { path: "login", component: Login}
];
