using Microsoft.AspNetCore.Http.HttpResults;

namespace PSR.Api.Endpoints.Analysis
{
    public static class AnalysisEndpoints
    {
        public static void MapAnalysisEndpoints(this WebApplication app)
        {
            app.MapPost("/api/analysis", async
                (HttpClient httpclient,
                AnalysisRequest request) =>
            {   
                // returned value of this variable is HttpResponseMessage
                var response = await httpclient.PostAsJsonAsync(
                    "http://127.0.0.1:8000/analyze",
                    request
                );

                response.EnsureSuccessStatusCode();

                var result = await response.Content.ReadFromJsonAsync<AnalysisResponse>();
                return Results.Ok(result);
            });
        }
    }
}
