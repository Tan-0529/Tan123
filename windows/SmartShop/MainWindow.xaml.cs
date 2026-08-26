using System.Collections.Specialized;
using System.IO;
using System.Windows;
using System.Windows.Input;
using System.Windows.Threading;
using Microsoft.Win32;
using SmartShop.Models;
using SmartShop.ViewModels;

namespace SmartShop;

public partial class MainWindow : Window
{
    private readonly ChatViewModel _vm = new();
    private readonly DispatcherTimer _scrollTimer;
    private string? _selectedImageBase64;
    private bool _followBottom = true;

    public MainWindow()
    {
        InitializeComponent();
        DataContext = _vm;

        _vm.Messages.CollectionChanged += OnMessagesChanged;

        _scrollTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(200) };
        _scrollTimer.Tick += (_, _) =>
        {
            if (_vm.IsSending && _followBottom) MsgScroll.ScrollToEnd();
        };

        MsgScroll.ScrollChanged += (_, e) =>
        {
            if (_followBottom && e.VerticalChange < 0)
                _followBottom = false;
        };
    }

    private void OnMessagesChanged(object? sender, NotifyCollectionChangedEventArgs e)
    {
        if (_followBottom) MsgScroll.ScrollToEnd();
    }

    private void ThemeBtn_Click(object sender, RoutedEventArgs e)
    {
        App.ToggleTheme();
    }

    private async void SendBtn_Click(object sender, RoutedEventArgs e) => await Send();

    private void ImageBtn_Click(object sender, RoutedEventArgs e)
    {
        var dlg = new OpenFileDialog
        {
            Filter = "图片文件|*.jpg;*.jpeg;*.png;*.webp|所有文件|*.*"
        };
        if (dlg.ShowDialog() == true)
        {
            _selectedImageBase64 = Convert.ToBase64String(File.ReadAllBytes(dlg.FileName));
            ImageBtn.Content = "图片✓";
        }
    }

    private async void LikeBtn_Click(object sender, RoutedEventArgs e)
    {
        if ((sender as FrameworkElement)?.Tag is ChatMessage msg)
        {
            await _vm.FeedbackAsync(msg, "like");
            MessageBox.Show("感谢您的反馈！", "SmartShop AI",
                            MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }

    private async void DislikeBtn_Click(object sender, RoutedEventArgs e)
    {
        if ((sender as FrameworkElement)?.Tag is ChatMessage msg)
        {
            await _vm.FeedbackAsync(msg, "dislike");
            MessageBox.Show("感谢您的反馈！", "SmartShop AI",
                            MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }

    private void InputBox_PreviewMouseWheel(object sender, MouseWheelEventArgs e)
    {
        if (e.Delta > 0) MsgScroll.LineUp();
        else MsgScroll.LineDown();
        e.Handled = true;
    }

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
        var image = _selectedImageBase64;
        _selectedImageBase64 = null;
        ImageBtn.Content = "图片";
        _followBottom = true;
        MsgScroll.ScrollToEnd();
        _scrollTimer.Start();
        try
        {
            await _vm.SendAsync(text, image);
        }
        finally
        {
            _scrollTimer.Stop();
            if (_followBottom) MsgScroll.ScrollToEnd();
        }
    }
}
