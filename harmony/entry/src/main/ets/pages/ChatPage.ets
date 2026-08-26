import { photoAccessHelper } from '@kit.MediaLibraryKit';
import { fileIo } from '@kit.CoreFileKit';
import { util } from '@kit.ArkTS';
import { ChatMessage, ProductCardModel } from '../model/ChatModels';
import { ChatViewModel } from '../viewmodel/ChatViewModel';
import { ProductCard } from '../components/ProductCard';

@Entry
@Component
struct ChatPage {
  @State vm: ChatViewModel = new ChatViewModel();
  @State inputText: string = '';
  private scroller: Scroller = new Scroller();
  private pendingImage: string = '';

  build() {
    Column() {
      Row() {
        Text('SmartShop AI')
          .fontSize(18)
          .fontWeight(FontWeight.Bold)
      }
      .width('100%')
      .padding(14)

      Divider()
        .strokeWidth(1)
        .color('#EEEEEE')

      List({ space: 12, scroller: this.scroller }) {
        ForEach(this.vm.messages, (msg: ChatMessage) => {
          ListItem() {
            MessageCell({ msg: msg, onFeedback: (r: string) => this.vm.feedback(msg, r) })
          }
          .transition(TransitionEffect.OPACITY.combine(TransitionEffect.translate({ y: 20 })))
        }, (msg: ChatMessage) => msg.id)
      }
      .layoutWeight(1)
      .width('100%')
      .padding({ left: 14, right: 14 })

      Divider()
        .strokeWidth(1)
        .color('#EEEEEE')

      Row({ space: 8 }) {
        Button('图片')
          .width(56)
          .height(44)
          .backgroundColor(this.pendingImage.length > 0 ? '#67C23A' : '#F5F5F5')
          .fontColor(this.pendingImage.length > 0 ? Color.White : '#333333')
          .onClick(() => {
            this.pickImage();
          })
        TextInput({ placeholder: '输入商品问题...', text: this.inputText })
          .layoutWeight(1)
          .height(44)
          .backgroundColor('#F5F5F5')
          .borderRadius(22)
          .onChange((v: string) => {
            this.inputText = v;
          })
        Button('发送')
          .width(76)
          .height(44)
          .backgroundColor('#4A90D9')
          .onClick(() => {
            this.send();
          })
      }
      .width('100%')
      .padding(12)
    }
    .width('100%')
    .height('100%')
  }

  private send(): void {
    if (this.inputText.trim().length === 0) {
      return;
    }
    const text = this.inputText;
    this.inputText = '';
    const image = this.pendingImage.length > 0 ? this.pendingImage : undefined;
    this.pendingImage = '';
    this.vm.send(text, image);
    this.scroller.scrollEdge(Edge.Bottom);
  }

  private async pickImage(): Promise<void> {
    const picker = new photoAccessHelper.PhotoViewPicker();
    const result = await picker.select({
      MIMEType: photoAccessHelper.PhotoViewMIMETypes.IMAGE_TYPE,
      maxSelectNumber: 1
    });
    if (result.photoUris.length === 0) {
      return;
    }
    const uri = result.photoUris[0];
    const file = fileIo.openSync(uri, fileIo.OpenMode.READ_ONLY);
    const stat = fileIo.statSync(file.fd);
    const buffer = new ArrayBuffer(stat.size);
    fileIo.readSync(file.fd, buffer);
    fileIo.closeSync(file);
    this.pendingImage = util.Base64Helper.encodeSync(new Uint8Array(buffer));
  }
}

@Component
struct MessageCell {
  @ObjectLink msg: ChatMessage;
  onFeedback: (rating: string) => void = () => {};

  build() {
    Column() {
      if (this.msg.role === 'user') {
        Text(this.msg.text)
          .fontSize(14)
          .fontColor('#333333')
          .backgroundColor('#D6EAF8')
          .borderRadius(10)
          .padding(10)
          .constraintSize({ maxWidth: '80%' })
      } else {
        Column({ space: 8 }) {
          Text(this.msg.text)
            .fontSize(14)
            .lineHeight(22)
          ForEach(this.msg.cards, (card: ProductCardModel) => {
            ProductCard({ card: card })
          }, (card: ProductCardModel) => card.sku)
          Row({ space: 10 }) {
            Text(this.msg.feedback === 'like' ? '👍 已赞' : '👍')
              .fontSize(13)
              .fontColor(this.msg.feedback === 'like' ? '#4A90D9' : '#999999')
              .onClick(() => {
                this.onFeedback('like');
              })
            Text(this.msg.feedback === 'dislike' ? '👎 已踩' : '👎')
              .fontSize(13)
              .fontColor(this.msg.feedback === 'dislike' ? '#E64545' : '#999999')
              .onClick(() => {
                this.onFeedback('dislike');
              })
          }
          .margin({ top: 4 })
        }
        .alignItems(HorizontalAlign.Start)
        .constraintSize({ maxWidth: '92%' })
      }
    }
    .width('100%')
    .alignItems(this.msg.role === 'user' ? HorizontalAlign.End : HorizontalAlign.Start)
  }
}
