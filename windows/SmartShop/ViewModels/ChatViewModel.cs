using System.Collections.ObjectModel;
using System.IO;
using System.Windows.Media.Imaging;
using SmartShop.Models;
using SmartShop.Network;

namespace SmartShop.ViewModels;

public class ChatViewModel : ViewModelBase
{
    private readonly ChatStream _stream = new();
    private readonly string _conversationId = Guid.NewGuid().ToString();
    private ChatMessage? _reply;
    private string _pending = "";
    private long _lastFlush;

    public ObservableCollection<ChatMessage> Messages { get; } = new();

    private bool _isSending;
    public bool IsSending
    {
        get => _isSending;
        set { _isSending = value; OnPropertyChanged(); }
    }

    public ChatViewModel()
    {
        _stream.OnDelta = AppendDelta;
        _stream.OnCard = card => _reply?.Cards.Add(card);
        _stream.OnDone = () =>
        {
            Flush();
            IsSending = false;
            if (_reply != null) _reply.IsStreaming = false;
            _reply = null;
        };
        _stream.OnError = err =>
        {
            Flush();
            if (_reply != null)
            {
                _reply.Text += $"\n[错误] {err}";
                _reply.IsStreaming = false;
            }
            IsSending = false;
        };
    }

    public async Task SendAsync(string text, string? imageBase64 = null)
    {
        if (string.IsNullOrWhiteSpace(text) || IsSending) return;
        Messages.Add(new ChatMessage
        {
            Role = "user",
            Text = text,
            Image = imageBase64 is null ? null : DecodeBase64(imageBase64),
        });
        _reply = new ChatMessage { Role = "assistant", IsStreaming = true };
        Messages.Add(_reply);
        IsSending = true;
        _pending = "";
        _lastFlush = 0;

        await _stream.SendAsync(new ChatInput
        {
            ConversationId = _conversationId,
            Message = text,
            Image = imageBase64,
        });
    }

    private static System.Windows.Media.ImageSource? DecodeBase64(string base64)
    {
        try
        {
            var bytes = Convert.FromBase64String(base64);
            using var ms = new MemoryStream(bytes);
            var img = new BitmapImage();
            img.BeginInit();
            img.CacheOption = BitmapCacheOption.OnLoad;
            img.StreamSource = ms;
            img.EndInit();
            img.Freeze();
            return img;
        }
        catch
        {
            return null;
        }
    }

    private void AppendDelta(string token)
    {
        _pending += token;
        var now = Environment.TickCount64;
        if (now - _lastFlush > 50)
        {
            Flush();
            _lastFlush = now;
        }
    }

    private void Flush()
    {
        if (_reply != null && _pending.Length > 0)
        {
            _reply.Text += _pending;
            _pending = "";
        }
    }
}
