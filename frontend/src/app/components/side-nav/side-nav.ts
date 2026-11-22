import { Component, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { BreakpointObserver } from '@angular/cdk/layout';
import { map } from 'rxjs';
import { MatSidenavModule, MatDrawer} from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink, RouterOutlet, RouterLinkActive } from '@angular/router';
import { MatButtonToggle, MatButtonToggleGroup } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';
import { ColorTheme, ThemeColor } from '../../services/color-theme';
import { COMPACT_LAYOUT } from '../../layout/breakpoints';

@Component({
  imports: [
    MatSidenavModule, MatListModule, 
    MatToolbarModule, MatButtonModule,
    MatButtonToggle, MatButtonToggleGroup, 
    MatIconModule, RouterLink, 
    RouterLinkActive, RouterOutlet
  ],
  selector: 'app-side-nav',
  styleUrl: './side-nav.scss',
  templateUrl: './side-nav.html',
})
export class SideNav {
  readonly colorTheme = inject(ColorTheme);
  private readonly breakpoints = inject(BreakpointObserver);

  readonly compact = toSignal(
    this.breakpoints.observe(COMPACT_LAYOUT).pipe(map(state => state.matches)),
    { initialValue: this.breakpoints.isMatched(COMPACT_LAYOUT)},
  );

  closeIfCompact(drawer: MatDrawer): void {
    if (this.compact()) drawer.close();
  }

  onThemeChange(value: ThemeColor | null): void {
    if (value != null) {
      this.colorTheme.setTheme(value);
    }
  }
}
