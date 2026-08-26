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

            string? line;
            while ((line = await reader.ReadLineAsync(ct)) is not null)
            {
                if (!line.StartsWith("data: ")) continue;
                var payload = line[6..];
                if (payload == "[DONE]") break;
                Dispatch(payload);
            }
            OnDone();
        }
        catch (Exception ex)
        {
            OnError(ex.Message);
        }
    }

    private void Dispatch(string payload)
    {
        using var doc = JsonDocument.Parse(payload);
        var root = doc.RootElement;
        var ev = root.GetProperty("event").GetString();
        switch (ev)
        {
            case "delta":
                OnDelta(root.GetProperty("content").GetString() ?? "");
                break;
            case "card":
                var card = JsonSerializer.Deserialize<ProductCardModel>(
                    root.GetProperty("data").GetRawText());
                if (card != null) OnCard(card);
                break;
            case "error":
                OnError(root.GetProperty("message").GetString() ?? "unknown error");
                break;
        }
    }
}
