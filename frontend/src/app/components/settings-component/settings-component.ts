import { Component } from '@angular/core';
import { MatDrawerContainer, MatDrawer, MatDrawerContent } from '@angular/material/sidenav';
import { MatListModule } from '@angular/material/list';
import { MatFormFieldModule, MatLabel } from '@angular/material/form-field';
import { ColorThemeMock, ColorThemeId } from '../../models/color-theme-mock';
import { MatOption } from '@angular/material/core';
import { MatSelect } from '@angular/material/select';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import {MatSlideToggleModule} from '@angular/material/slide-toggle';

type SettingsSection = 'theme' | 'language' | 'general';

@Component({
  imports: [
    MatDrawerContainer,
    MatDrawer,
    MatListModule,
    MatDrawerContent,
    MatFormFieldModule,
    MatLabel,
    MatOption,
    MatSelect,
    MatIconModule,
    MatButtonModule,
    MatSlideToggleModule
  ],
  selector: 'app-settings-component',
  styleUrl: './settings-component.scss',
  templateUrl: './settings-component.html',
})
export class SettingsComponent {
  selectedSection: SettingsSection = 'theme';

  get sectionTitle(): string {
    const titles: Record<SettingsSection, string> = {
      theme: 'Theme',
      language: 'Language',
      general: 'General',
    };

    return titles[this.selectedSection];
  }

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
