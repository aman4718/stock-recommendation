export interface StockRecommendation {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  price: number;
  pe_ratio: number | null;
  market_cap: string;
  one_month_change: string;
  risk_level: string;
  valuation_category: string;
  description: string;
  fifty_two_week_high: number | null;
  fifty_two_week_low: number | null;
  eps: number | null;
  revenue_growth: string;
  profit_margin: string;
  yahoo_finance_url: string;
}

export interface ChatResponse {
  answer: string;
  recommendations: StockRecommendation[];
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function sendChatMessage(query: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to send message');
  }

  return response.json();
}
