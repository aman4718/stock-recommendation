import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { StockRecommendation } from '@/lib/api';

const C = {
  primary:  '#3d35c8',
  priLight: '#ebe9ff',
  t1:       '#1a1640',
  t2:       '#5b5880',
  t3:       '#9896bc',
  success:  '#16a34a',
  danger:   '#dc2626',
} as const;

function getAction(stock: StockRecommendation): 'BUY' | 'HOLD' | 'SELL' {
  const risk = (stock.risk_level ?? '').toLowerCase();
  if (risk === 'low')  return 'BUY';
  if (risk === 'high') return 'SELL';
  return 'HOLD';
}

function getConfidence(risk: string | null | undefined): number {
  return ({ low: 88, medium: 72, high: 58 } as Record<string, number>)[(risk ?? '').toLowerCase()] ?? 70;
}

const ACTION: Record<'BUY'|'HOLD'|'SELL', { bg: string; color: string; border: string }> = {
  BUY:  { bg: '#ebe9ff', color: '#3d35c8', border: 'rgba(61,53,200,0.22)' },
  HOLD: { bg: '#f3f4f6', color: '#374151', border: '#e5e7eb' },
  SELL: { bg: '#fef2f2', color: '#dc2626', border: '#fecaca' },
};

interface Props {
  stock: StockRecommendation;
}

export const StockCard: React.FC<Props> = ({ stock }) => {
  const changeStr = String(stock.one_month_change ?? '');
  const up        = changeStr.includes('+') || (!changeStr.includes('-') && changeStr !== 'N/A' && changeStr !== '—');
  const action    = getAction(stock);
  const conf      = getConfidence(stock.risk_level);
  const { bg, color, border } = ACTION[action];

  const tags: string[] = [];
  if (stock.sector && stock.sector !== 'N/A') tags.push('#' + stock.sector);
  const riskLabel = stock.risk_level || 'Unknown';
  if (riskLabel !== 'Unknown') tags.push('#' + (riskLabel.charAt(0).toUpperCase() + riskLabel.slice(1)));

  return (
    <div
      onClick={() => window.open(stock.yahoo_finance_url, '_blank')}
      title="Click to view full details on Yahoo Finance"
      style={{
        background: 'var(--al-card)',
        borderRadius: 22,
        padding: '22px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.06)',
        border: '1px solid var(--al-border)',
        minWidth: 280,
        width: 300,
        transition: 'all 0.2s ease-in-out',
        cursor: 'pointer',
      }}
      onMouseEnter={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.1)';
        e.currentTarget.style.borderColor = 'var(--al-primary)';
      }}
      onMouseLeave={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,0,0,0.06)';
        e.currentTarget.style.borderColor = 'var(--al-border)';
      }}
    >
      {/* ── Name + Price ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
        <div style={{ flex: 1, minWidth: 0, paddingRight: 12 }}>
          <div style={{ fontWeight: 800, fontSize: 18, color: 'var(--al-t1)', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
            {stock.name}
          </div>
          <div style={{ fontSize: 13, color: 'var(--al-t3)', marginTop: 4, fontWeight: 600 }}>
            {stock.ticker} • {stock.industry}
          </div>
        </div>
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontWeight: 700, fontSize: 17, color: 'var(--al-t1)', fontVariantNumeric: 'tabular-nums' }}>
            ${typeof stock.price === 'number' ? stock.price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : '0.00'}
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 3, justifyContent: 'flex-end', marginTop: 4, color: up ? '#10b981' : '#ef4444', fontSize: 13, fontWeight: 700 }}>
            {up ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
            {changeStr || '—'}
          </div>
        </div>
      </div>

      {/* ── Sector Tags ── */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, marginBottom: 18 }}>
        {tags.map((t, i) => (
          <span
            key={`${t}-${i}`}
            style={{ background: 'var(--al-pri-sub)', color: 'var(--al-primary)', fontSize: 11, fontWeight: 700, padding: '4px 12px', borderRadius: 50, letterSpacing: '0.02em', textTransform: 'uppercase' }}
          >
            {t}
          </span>
        ))}
        {stock.valuation_category && stock.valuation_category !== 'Unknown' && (
          <span style={{ background: '#fef3c7', color: '#92400e', fontSize: 11, fontWeight: 700, padding: '4px 12px', borderRadius: 50, letterSpacing: '0.02em', textTransform: 'uppercase' }}>
            #{stock.valuation_category.replace(' / ', '-')}
          </span>
        )}
      </div>

      {/* ── Action Badge + Confidence ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18 }}>
        <span style={{ background: bg, color, border: `1px solid ${border}`, padding: '4px 16px', borderRadius: 50, fontSize: 12, fontWeight: 800, letterSpacing: '0.06em' }}>
          {action}
        </span>
        <span style={{ fontSize: 13, color: 'var(--al-t2)', fontWeight: 600 }}>
          {conf}% Conf.
        </span>
      </div>

      {/* ── Separator + Extra Info ── */}
      <div style={{ borderTop: '1px solid var(--al-border)', paddingTop: 14, display: 'flex', flexWrap: 'wrap', gap: '8px 16px', fontSize: 12, color: 'var(--al-t3)' }}>
        <div style={{ flex: '1 1 40%' }}>
          Cap: <span style={{ color: 'var(--al-t1)', fontWeight: 700 }}>{stock.market_cap || '—'}</span>
        </div>
        <div style={{ flex: '1 1 40%', textAlign: 'right' }}>
          P/E: <span style={{ color: 'var(--al-t1)', fontWeight: 700 }}>{stock.pe_ratio ? Number(stock.pe_ratio).toFixed(1) + 'x' : '—'}</span>
        </div>
        <div style={{ flex: '1 1 100%', fontSize: 11, fontStyle: 'italic', marginTop: 4, color: 'var(--al-primary)', fontWeight: 600 }}>
          Click card for full analysis →
        </div>
      </div>
    </div>
  );
};

