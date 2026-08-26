export interface ProductCardModel {
  name: string;
  price: number;
  rating: number;
  imageUrl: string;
  productUrl: string;
  sku: string;
}

@Observed
export class ChatMessage {
  id: string;
  role: string;
  text: string;
  cards: ProductCardModel[];
  isStreaming: boolean;
  messageId: string;
  feedback: string;

  constructor(id: string, role: string, text: string = '', cards: ProductCardModel[] = [],
              isStreaming: boolean = false, messageId: string = '', feedback: string = '') {
    this.id = id;
    this.role = role;
    this.text = text;
    this.cards = cards;
    this.isStreaming = isStreaming;
    this.messageId = messageId;
    this.feedback = feedback;
  }
}

export interface ChatInput {
  conversation_id: string;
  message: string;
  image?: string;
}

export interface SSEEvent {
  event: string;
  content?: string;
  data?: string;
  message?: string;
  conversation_id?: string;
  message_id?: string;
}
