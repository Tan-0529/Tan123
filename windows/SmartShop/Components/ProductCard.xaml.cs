using System.Windows.Controls;
using System.Windows.Media.Imaging;
using SmartShop.Models;

namespace SmartShop.Components;

public partial class ProductCard : UserControl
{
    public ProductCard()
    {
        InitializeComponent();
        DataContextChanged += (_, _) => Bind();
    }

    private void Bind()
    {
        if (DataContext is not ProductCardModel m) return;
        NameText.Text = m.Name;
        PriceText.Text = $"¥{m.Price:F2}";
        RatingText.Text = $"★ {m.Rating:F1}";
        if (!string.IsNullOrEmpty(m.ImageUrl))
        {
            try
            {
                ProductImage.Source = new BitmapImage(new Uri(m.ImageUrl));
            }
            catch
            {
            }
        }
    }
}
