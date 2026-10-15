import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatList, MatListItem } from '@angular/material/list';


@Component({
  imports: [MatCardModule, MatIconModule, MatList, MatListItem],
  selector: 'app-analysis-result',
  styleUrl: './analysis-result.scss',
  templateUrl: './analysis-result.html',
})
export class AnalysisResult {}
