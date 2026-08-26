using System.Collections.Specialized;
using System.Windows;
using System.Windows.Input;
using System.Windows.Threading;
using SmartShop.ViewModels;

namespace SmartShop;

public partial class MainWindow : Window
{
    private readonly ChatViewModel _vm = new();
    private readonly DispatcherTimer _scrollTimer;

    public MainWindow()
    {
        InitializeComponent();
        DataContext = _vm;

        _vm.Messages.CollectionChanged += OnMessagesChanged;

        _scrollTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(200) };
        _scrollTimer.Tick += (_, _) =>
        {
            if (_vm.IsSending) MsgScroll.ScrollToEnd();
        };
    }

    private void OnMessagesChanged(object? sender, NotifyCollectionChangedEventArgs e)
        => MsgScroll.ScrollToEnd();

    private async void SendBtn_Click(object sender, RoutedEventArgs e) => await Send();

    private async void InputBox_KeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Enter && (Keyboard.Modifiers & ModifierKeys.Shift) == 0)
        {
            e.Handled = true;
            await Send();
        }
    }

    private async Task Send()
    {
        var text = InputBox.Text.Trim();
        if (string.IsNullOrEmpty(text)) return;

        InputBox.Text = "";
        _scrollTimer.Start();
        try
        {
            await _vm.SendAsync(text);
        }
        finally
        {
            _scrollTimer.Stop();
            MsgScroll.ScrollToEnd();
        }
    }
}
