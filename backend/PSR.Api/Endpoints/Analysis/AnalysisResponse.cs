namespace PSR.Api.Endpoints.Analysis
{
    public class AnalysisResponse
    {
        public string Message { get; set; } = string.Empty;

        public string ReceivedText { get; set; } = string.Empty;

        public int Risk { get; set; }
    }
}
