using System.IO;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using SmartShop.Models;

namespace SmartShop.Network;

public class ChatStream
{
    private readonly HttpClient _http = new() { Timeout = Timeout.InfiniteTimeSpan };

    public string BaseUrl { get; set; } = "http://127.0.0.1:8000";

    public Action<string> OnDelta = _ => { };
    public Action<ProductCardModel> OnCard = _ => { };
    public Action OnDone = () => { };
    public Action<string> OnError = _ => { };
    public Action<string> OnMeta = _ => { };

    public async Task SendAsync(ChatInput input, CancellationToken ct = default)
    {
        var json = JsonSerializer.Serialize(input);
        var req = new HttpRequestMessage(HttpMethod.Post, $"{BaseUrl}/chat")
        {
            Content = new StringContent(json, Encoding.UTF8, "application/json")
        };

        try
        {
            using var resp = await _http.SendAsync(req, HttpCompletionOption.ResponseHeadersRead, ct);
            resp.EnsureSuccessStatusCode();
            await using var stream = await resp.Content.ReadAsStreamAsync(ct);
            using var reader = new StreamReader(stream);

            var currentEvent = "message";
            string? line;
            while ((line = await reader.ReadLineAsync(ct)) is not null)
            {
                if (line.StartsWith("event: "))
                {
                    currentEvent = line[7..].Trim();
                }
                else if (line.StartsWith("data: "))
                {
                    var payload = line[6..];
                    if (payload == "[DONE]") break;
                    Dispatch(currentEvent, payload);
                }
                else if (line.Length == 0)
                {
                    currentEvent = "message";
                }
            }
            OnDone();
        }
        catch (Exception ex)
        {
            OnError(ex.Message);
        }
    }

    private void Dispatch(string ev, string payload)
    {
        using var doc = JsonDocument.Parse(payload);
        var root = doc.RootElement;
        switch (ev)
        {
            case "meta":
                if (root.TryGetProperty("message_id", out var mid))
                    OnMeta(mid.GetString() ?? "");
                break;
            case "delta":
                if (root.TryGetProperty("content", out var c))
                    OnDelta(c.GetString() ?? "");
                break;
            case "card":
                if (root.TryGetProperty("data", out var d))
                {
                    var card = JsonSerializer.Deserialize<ProductCardModel>(d.GetRawText());
                    if (card != null) OnCard(card);
                }
                break;
            case "error":
                if (root.TryGetProperty("message", out var m))
                    OnError(m.GetString() ?? "unknown error");
                else
                    OnError("unknown error");
                break;
        }
    }
}
