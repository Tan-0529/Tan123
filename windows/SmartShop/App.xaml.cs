using System.Windows;

namespace SmartShop;

public partial class App : Application
{
    public static bool IsDark { get; private set; }

    public static void ToggleTheme()
    {
        IsDark = !IsDark;
        var dict = new ResourceDictionary
        {
            Source = new Uri(IsDark ? "Themes/DarkTheme.xaml" : "Themes/LightTheme.xaml",
                             UriKind.Relative)
        };
        var merged = Application.Current.Resources.MergedDictionaries;
        merged.Clear();
        merged.Add(dict);
    }
}
