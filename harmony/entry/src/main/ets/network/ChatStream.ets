import http from '@ohos.net.http';
import util from '@ohos.util';
import { BusinessError } from '@ohos.base';
import { ChatInput, ProductCardModel, SSEEvent } from '../model/ChatModels';

const BASE_URL: string = 'http://127.0.0.1:8000';

export class ChatStream {
  private httpRequest: http.HttpRequest = http.createHttp();
  private buffer: string = '';
  private decoder: util.TextDecoder = util.TextDecoder.create('utf-8');

  onDelta: (text: string) => void = () => {};
  onCard: (card: ProductCardModel) => void = () => {};
  onMeta: (messageId: string) => void = () => {};
  onDone: () => void = () => {};
  onError: (msg: string) => void = () => {};

  send(input: ChatInput): void {
    const body = JSON.stringify({
      conversation_id: input.conversation_id,
      message: input.message,
      image: input.image ?? null
    });
    this.buffer = '';

    this.httpRequest.on('dataReceive', (data: ArrayBuffer) => {
      this.buffer += this.decoder.decodeToString(new Uint8Array(data));
      this.parseLines();
    });

    this.httpRequest.request(`${BASE_URL}/chat`, {
      method: http.RequestMethod.POST,
      header: { 'Content-Type': 'application/json' },
      extraData: body,
      expectDataType: http.HttpDataType.ARRAY_BUFFER,
      readTimeout: 120000,
      connectTimeout: 10000
    }).then(() => {
      this.parseLines();
      this.onDone();
    }).catch((err: BusinessError) => {
      this.onError(`${err.code}: ${err.message}`);
    });
  }

  private parseLines(): void {
    let idx = this.buffer.indexOf('\n');
    while (idx !== -1) {
      const line = this.buffer.substring(0, idx).trim();
      this.buffer = this.buffer.substring(idx + 1);
      this.parseLine(line);
      idx = this.buffer.indexOf('\n');
    }
  }

  private parseLine(line: string): void {
    if (!line.startsWith('data: ')) {
      return;
    }
    const payload = line.substring(6).trim();
    if (payload === '[DONE]') {
      return;
    }
    const ev = JSON.parse(payload) as SSEEvent;
    if (ev.event === 'delta' && ev.content) {
      this.onDelta(ev.content);
    } else if (ev.event === 'card' && ev.data) {
      const card = JSON.parse(ev.data) as ProductCardModel;
      this.onCard(card);
    } else if (ev.event === 'meta' && ev.message_id) {
      this.onMeta(ev.message_id);
    } else if (ev.event === 'error') {
      this.onError(ev.message ?? 'unknown error');
    }
  }
}
