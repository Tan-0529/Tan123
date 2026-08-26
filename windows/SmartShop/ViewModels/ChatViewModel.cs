using System.Collections.ObjectModel;
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
            _reply = null;
        };
        _stream.OnError = err =>
        {
            Flush();
            if (_reply != null) _reply.Text += $"\n[错误] {err}";
            IsSending = false;
        };
    }

    public async Task SendAsync(string text)
    {
        if (string.IsNullOrWhiteSpace(text) || IsSending) return;
        Messages.Add(new ChatMessage { Role = "user", Text = text });
        _reply = new ChatMessage { Role = "assistant" };
        Messages.Add(_reply);
        IsSending = true;
        _pending = "";
        _lastFlush = 0;

        await _stream.SendAsync(new ChatInput
        {
            ConversationId = _conversationId,
            Message = text,
        });
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
