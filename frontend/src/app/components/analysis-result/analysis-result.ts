import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatList, MatListItem } from '@angular/material/list';
import { MatAnchor } from '@angular/material/button';
import { MatButton } from '@angular/material/button';
import { AnalysisResultsMock } from '../../models/analysis-results-mock';


@Component({
  imports:
    [
      MatCardModule,
      MatIconModule,
      MatList,
      MatListItem,
      MatAnchor,
      MatButton,
    ],
  selector: 'app-analysis-result',
  styleUrl: './analysis-result.scss',
  templateUrl: './analysis-result.html',
})
export class AnalysisResult { 
  analysisResult: AnalysisResultsMock = {
    riskScore: 92,
    riskLevel: 'phishing',
    summary: 'The message contains suspicious characteristicks',
    indicators: [
      'Suspicious URL detected',
      'Link destination may be misleading',
      'Messages uses urgent language',
    ],
  };

  get riskLevelLabel(): string {
    const labels = {
      pass: 'Pass',
      warning: 'Warning',
      phishing: 'High Risk',
    };

    return labels[this.analysisResult.riskLevel];
  }

  get riskIcon(): string {
    const icons = {
      pass: 'verified_user',
      warning: 'warning',
      phishing: 'gpp_bad',
    };

    return icons[this.analysisResult.riskLevel];
  }
}
