export interface AnalysisResultsMock {
    riskScore: number;
    riskLevel: 'pass' | 'warning' | 'phishing'
    summary: string;
    indicators: string[];
}
