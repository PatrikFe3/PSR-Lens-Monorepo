import { Component } from '@angular/core';
import { AnalysisResult } from '../../components/analysis-result/analysis-result';

@Component({
  imports: [AnalysisResult],
  selector: 'app-analysis-results',
  styleUrl: './analysis-results.scss',
  templateUrl: './analysis-results.html',
})
export class AnalysisResults {}
