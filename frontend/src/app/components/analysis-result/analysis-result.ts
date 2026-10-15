import { Component } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatList, MatListItem } from '@angular/material/list';
import { MatAnchor } from '@angular/material/button';
import { MatButton } from '@angular/material/button';
import { MatDivider } from '@angular/material/list';


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
export class AnalysisResult { }
