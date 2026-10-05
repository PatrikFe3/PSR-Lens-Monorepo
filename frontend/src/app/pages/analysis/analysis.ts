import { Component } from '@angular/core';
import { AnalysisInput } from '../../components/analysis-input/analysis-input';

@Component({
  imports: [AnalysisInput],
  selector: 'app-analysis',
  styleUrl: './analysis.scss',
  templateUrl: './analysis.html',
})
export class Analysis {}
