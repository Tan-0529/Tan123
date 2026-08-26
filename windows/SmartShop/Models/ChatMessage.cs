using System.Collections.ObjectModel;
using System.Text.Json.Serialization;
using System.Windows.Media;
using SmartShop.ViewModels;

namespace SmartShop.Models;

public class ChatMessage : ViewModelBase
{
    public string Role { get; set; } = "";

    private string _text = "";
    public string Text
    {
        get => _text;
        set { _text = value; OnPropertyChanged(); }
    }

    public ImageSource? Image { get; set; }

    public string? MessageId { get; set; }

    private string? _feedback;
    public string? Feedback
    {
        get => _feedback;
        set { _feedback = value; OnPropertyChanged(); }
    }

    private bool _isStreaming;
    public bool IsStreaming
    {
        get => _isStreaming;
        set { _isStreaming = value; OnPropertyChanged(); }
    }

    public ObservableCollection<ProductCardModel> Cards { get; } = new();
}

public class ProductCardModel
{
    [JsonPropertyName("name")] public string Name { get; set; } = "";
    [JsonPropertyName("price")] public double Price { get; set; }
    [JsonPropertyName("rating")] public double Rating { get; set; }
    [JsonPropertyName("image_url")] public string ImageUrl { get; set; } = "";
    [JsonPropertyName("product_url")] public string ProductUrl { get; set; } = "";
    [JsonPropertyName("sku")] public string Sku { get; set; } = "";
}

public class ChatInput
{
    [JsonPropertyName("conversation_id")] public string ConversationId { get; set; } = "";
    [JsonPropertyName("message")] public string Message { get; set; } = "";
    [JsonPropertyName("image")] public string? Image { get; set; }
}
