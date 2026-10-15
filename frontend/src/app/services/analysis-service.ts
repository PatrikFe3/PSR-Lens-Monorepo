import { Service, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { AnalysisResultsMock } from '../models/analysis-results-mock';

export interface AnalysisRequest {
    text: string;
}

export interface AnalysisResponse {
    message: string;
    received_text: string;
    result: number;
}

@Service()
export class AnalysisService {
    private http = inject(HttpClient);
    private apiUrl = 'http://localhost:5104/api';

    analyze(request: AnalysisRequest) {
        return this.http.post<AnalysisResponse>(
            `${this.apiUrl}/analysis`,
            request
        )
    }

    AnalysisResultsMock = [
        
    ]
}
