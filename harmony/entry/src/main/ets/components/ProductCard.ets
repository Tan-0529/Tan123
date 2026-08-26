import { ProductCardModel } from '../model/ChatModels';

@Component
export struct ProductCard {
  card: ProductCardModel = { name: '', price: 0, rating: 0, imageUrl: '', productUrl: '', sku: '' };

  build() {
    Column({ space: 6 }) {
      Image(this.card.imageUrl)
        .width('100%')
        .height(140)
        .objectFit(ImageFit.Cover)
        .borderRadius({ topLeft: 8, topRight: 8 })

      Text(this.card.name)
        .fontSize(15)
        .fontWeight(FontWeight.Medium)
        .maxLines(2)
        .textOverflow({ overflow: TextOverflow.Ellipsis })
        .padding({ left: 10, right: 10 })

      Row() {
        Text(`¥${this.card.price.toFixed(2)}`)
          .fontSize(18)
          .fontColor('#E64545')
          .fontWeight(FontWeight.Bold)
        Blank()
        Text(`★ ${this.card.rating.toFixed(1)}`)
          .fontSize(13)
          .fontColor('#FF8C00')
      }
      .width('100%')
      .padding({ left: 10, right: 10, bottom: 10 })
    }
    .width(280)
    .backgroundColor(Color.White)
    .borderRadius(12)
    .margin({ top: 4, bottom: 4 })
    .shadow({ radius: 8, color: '#1A000000', offsetY: 2 })
  }
}
