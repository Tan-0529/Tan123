import { ChatMessage, ProductCardModel } from '../model/ChatModels';
import { ChatStream } from '../network/ChatStream';

@Observed
export class ChatViewModel {
  messages: ChatMessage[] = [];
  isSending: boolean = false;
  private stream: ChatStream = new ChatStream();
  private reply: ChatMessage | undefined = undefined;
  private pending: string = '';
  private lastFlush: number = 0;
  private conversationId: string = `c-${Date.now()}`;

  constructor() {
    this.stream.onDelta = (t: string): void => this.appendDelta(t);
    this.stream.onCard = (card: ProductCardModel): void => {
      if (this.reply) {
        this.reply.cards.push(card);
      }
    };
    this.stream.onMeta = (mid: string): void => {
      if (this.reply) {
        this.reply.messageId = mid;
      }
    };
    this.stream.onDone = (): void => this.finish();
    this.stream.onError = (msg: string): void => {
      this.flush();
      if (this.reply) {
        this.reply.text += `\n[错误] ${msg}`;
        this.reply.isStreaming = false;
      }
      this.isSending = false;
      this.reply = undefined;
    };
  }

  send(text: string): void {
    if (text.trim().length === 0 || this.isSending) {
      return;
    }
    this.messages.push(new ChatMessage(`u-${Date.now()}`, 'user', text));
    this.reply = new ChatMessage(`a-${Date.now()}`, 'assistant', '', [], true);
    this.messages.push(this.reply);
    this.isSending = true;
    this.pending = '';
    this.lastFlush = 0;
    this.stream.send({
      conversation_id: this.conversationId,
      message: text
    });
  }

  private appendDelta(t: string): void {
    this.pending += t;
    const now = Date.now();
    if (now - this.lastFlush > 50) {
      this.flush();
      this.lastFlush = now;
    }
  }

  private finish(): void {
    this.flush();
    if (this.reply) {
      this.reply.isStreaming = false;
    }
    this.isSending = false;
    this.reply = undefined;
  }

  private flush(): void {
    if (this.reply && this.pending.length > 0) {
      this.reply.text += this.pending;
      this.pending = '';
    }
  }
}
