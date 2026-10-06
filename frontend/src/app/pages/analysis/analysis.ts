import { Component, inject } from '@angular/core';
import { AnalysisInput } from '../../components/analysis-input/analysis-input';
import { AnalysisService } from '../../services/analysis-service';

@Component({
  imports: [AnalysisInput],
  selector: 'app-analysis',
  styleUrl: './analysis.scss',
  templateUrl: './analysis.html',
})
export class Analysis {

  private analysisService = inject(AnalysisService);

  onAnalyze(message: string) {

    console.log('Sending to backend:', message);

    this.analysisService.analyze({
      text: message
    }).subscribe(response => {
      console.log('Backend response:', response);
    })
  }
}
