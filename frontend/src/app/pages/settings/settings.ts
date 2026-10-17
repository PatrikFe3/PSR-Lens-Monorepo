import { Component } from '@angular/core';
import { MatDrawerContainer, MatDrawer, MatDrawerContent } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { ColorThemeMock, ColorThemeId } from '../../models/color-theme-mock';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
@Component({
  imports: [
    MatDrawerContainer,
    MatDrawer,
    MatListModule,
    MatDrawerContent,
    MatFormField,
    MatLabel,
    MatOption,
    MatSelect,
    MatIconModule,
    MatButtonModule
],
  selector: 'app-settings',
  styleUrl: './settings.scss',
  templateUrl: './settings.html',
})
export class Settings {
  colorId: ColorThemeId = 'autumn';
  colorThemeData: ColorThemeMock[] = [
    {
      id: 'jungle',
      name: 'Jungle',
    },
    {
      id: 'autumn',
      name: 'Autumn',
    },
    {
      id: 'aqua',
      name: 'Aqua',
    },
    {
      id: 'custom',
      name: 'Custom',
    }
  ]

  
}
