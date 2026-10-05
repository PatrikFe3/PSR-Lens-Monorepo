import { Component } from '@angular/core';
import { MatFormField } from '@angular/material/form-field';
import { MatLabel } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';

@Component({
  imports:
    [
      MatFormField,
      MatLabel,
      MatIconModule,
      MatButtonModule
    ],
  selector: 'app-analysis-input',
  styleUrl: './analysis-input.scss',
  templateUrl: './analysis-input.html',
})
export class AnalysisInput { }
