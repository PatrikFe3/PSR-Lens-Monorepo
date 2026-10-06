import { Component, output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatFormField, MatLabel } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatInput } from '@angular/material/input';

@Component({
  imports:
    [
      MatFormField,
      MatLabel,
      MatIconModule,
      MatButtonModule,
      MatInput,
      FormsModule
    ],
  selector: 'app-analysis-input',
  styleUrl: './analysis-input.scss',
  templateUrl: './analysis-input.html',
})
export class AnalysisInput {

  emailContent = '';

  analyze = output<string>();

  onAnalyze() {
    this.analyze.emit(this.emailContent);
  }
}
