import { Component } from '@angular/core';
import {MatSidenavModule} from '@angular/material/sidenav';
import {MatListModule} from '@angular/material/list';
import { RouterLink, RouterOutlet } from '@angular/router';
import { MatButtonToggle, MatButtonToggleGroup } from '@angular/material/button-toggle';
import { MatIconModule } from '@angular/material/icon';

@Component({
  imports: [
    MatSidenavModule,
    MatListModule,
    RouterLink,
    RouterOutlet,
    MatButtonToggle,
    MatButtonToggleGroup,
    MatIconModule
],
  selector: 'app-side-nav',
  styleUrl: './side-nav.scss',
  templateUrl: './side-nav.html',
})
export class SideNav {}
