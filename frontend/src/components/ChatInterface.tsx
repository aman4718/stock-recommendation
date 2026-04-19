'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
  Search, ArrowRight, ArrowUp, SlidersHorizontal, RefreshCw,
  Clock, User, Sparkles, MessageSquare, Briefcase, TrendingUp,
  Moon, Sun, Send
} from 'lucide-react';
import { sendChatMessage, StockRecommendation } from '@/lib/api';
import { StockCard } from './StockCard';

type Msg = {
  id:     string;
  role:   'user' | 'ai';
  text:   string;
  stocks?: StockRecommendation[];
};

export const ChatInterface: React.FC = () => {
  const [view,    setView]    = useState<'land' | 'chat'>('land');
  const [input,   setInput]   = useState('');
  const [msgs,    setMsgs]    = useState<Msg[]>([]);
  const [loading, setLoading] = useState(false);
  const [dark,    setDark]    = useState(false);
  const [sg,      setSg]      = useState(0);
  const chatEnd = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Persistence for dark mode
  useEffect(() => {
    const saved = localStorage.getItem('al-theme');
    if (saved === 'dark') setDark(true);
  }, []);

  useEffect(() => {
    localStorage.setItem('al-theme', dark ? 'dark' : 'light');
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  }, [dark]);

  useEffect(() => {
    chatEnd.current?.scrollIntoView({ behavior: 'smooth' });
  }, [msgs, loading]);

  const send = async (query: string) => {
    const q = query.trim();
    if (!q || loading) return;
    setMsgs(p => [...p, { id: `${Date.now()}`, role: 'user', text: q }]);
    setView('chat');
    setInput('');
    setLoading(true);
    try {
      const r = await sendChatMessage(q);
      setMsgs(p => [...p, {
        id: `ai-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`, role: 'ai',
        text: r.answer, stocks: r.recommendations,
      }]);
    } catch (err) {
      setMsgs(p => [...p, {
        id: `err-${Date.now()}`, role: 'ai',
        text: 'I\'m having trouble connecting to the analytics engine right now. Please check your internet connection or try again in a moment.',
      }]);
      console.error("API Connection Error:", err);
    } finally {
      setLoading(false);
    }
  };

  const refine = (text: string) => {
    setInput(text);
    inputRef.current?.focus();
    // Optional: scroll to bottom
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
  };

  const chips = SUGG[sg % SUGG.length];

  return (
    <div className={dark ? 'dark' : ''}>
      <style>{`
        :root {
          --al-bg: #eeeef6;
          --al-card: #ffffff;
          --al-primary: #3d35c8;
          --al-pri-sub: rgba(61, 53, 200, 0.06);
          --al-t1: #1a1640;
          --al-t2: #5b5880;
          --al-t3: #9896bc;
          --al-border: rgba(61, 53, 200, 0.1);
        }
        [data-theme='dark'] {
          --al-bg: #0f1016;
          --al-card: #1c1d26;
          --al-primary: #6c63ff;
          --al-pri-sub: rgba(108, 99, 255, 0.12);
          --al-t1: #f3f4f9;
          --al-t2: #b4b8cc;
          --al-t3: #6c6f93;
          --al-border: rgba(108, 99, 255, 0.15);
        }

        .al-desktop { display: flex; }
        .al-mobile  { display: none; }
        .al-chips   { flex-direction: row; flex-wrap: wrap; justify-content: center; }

        @media (max-width: 640px) {
          .al-desktop    { display: none   !important; }
          .al-mobile     { display: flex   !important; }
          .al-title      { font-size: 38px !important; line-height: 1.12 !important; }
          .al-chips      { flex-direction: column !important; align-items: flex-start !important; gap: 8px !important; }
          .al-searchbox  { padding: 8px 8px 8px 18px !important; }
          .al-land       { padding: 48px 20px 40px !important; }
          .al-chat       { padding: 24px 16px 140px !important; }
          .al-followup   { bottom: 0 !important; padding: 0 16px 16px !important; }
        }

        .al-btn:hover { background: var(--al-pri-sub) !important; opacity: 0.95; }
        .al-action-btn:hover { background: var(--al-pri-sub) !important; }
        @keyframes msgIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes dot { 0%, 100% { opacity: 0.2; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.1); } }
      `}</style>

      <div style={{ minHeight: '100vh', background: 'var(--al-bg)', color: 'var(--al-t1)', display: 'flex', flexDirection: 'column', transition: 'background 0.3s, color 0.3s' }}>

        {/* ════════════ NAVBAR ════════════ */}
        <nav style={{ position: 'sticky', top: 0, zIndex: 100, background: 'var(--al-bg)', borderBottom: '1px solid var(--al-border)', opacity: 0.98 }}>
          <div style={{ maxWidth: 1120, margin: '0 auto', height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px' }}>
            <button
              onClick={() => setView('land')}
              style={{ fontWeight: 800, fontSize: 18, color: 'var(--al-primary)', background: 'none', border: 'none', cursor: 'pointer', padding: 0, letterSpacing: '-0.03em' }}
            >
              Aether Ledger
            </button>

            <div style={{ display: 'flex', gap: 10 }}>
              <button 
                onClick={() => setDark(!dark)}
                style={{ width: 36, height: 36, borderRadius: '50%', border: '1px solid var(--al-border)', background: 'var(--al-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--al-t2)' }}
              >
                {dark ? <Sun size={16} /> : <Moon size={16} />}
              </button>
              <button style={{ width: 36, height: 36, borderRadius: '50%', border: '1px solid var(--al-border)', background: 'var(--al-card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--al-t2)' }}>
                <User size={16} />
              </button>
            </div>
          </div>
        </nav>

        {/* ════════════ MAIN SCROLL AREA ════════════ */}
        <main style={{ flex: 1 }}>

          {/* ─── LANDING VIEW ─── */}
          {view === 'land' && (
            <div className="al-land" style={{ maxWidth: 680, margin: '0 auto', padding: '100px 24px 60px', textAlign: 'center' }}>
              <h1 className="al-title" style={{ fontSize: 56, fontWeight: 900, color: 'var(--al-t1)', lineHeight: 1.05, letterSpacing: '-0.04em', marginBottom: 44, animation: 'msgIn 0.5s ease both' }}>
                Ask anything about<br />Markets &amp; Stocks
              </h1>

              {/* Search pill */}
              <div 
                className="al-searchbox" 
                style={{ background: 'var(--al-card)', borderRadius: 50, boxShadow: '0 8px 30px rgba(0,0,0,0.08)', padding: '8px 8px 8px 24px', display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, animation: 'msgIn 0.5s ease 0.1s both', border: '1px solid var(--al-border)' }}
              >
                <Search size={18} style={{ color: 'var(--al-t3)', flexShrink: 0 }} />
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && send(input)}
                  placeholder="High growth AI stocks in India..."
                  style={{ flex: 1, border: 'none', outline: 'none', fontSize: 16, color: 'var(--al-t1)', background: 'transparent' }}
                />
                <button
                  onClick={() => send(input)}
                  style={{ width: 44, height: 44, borderRadius: '50%', background: input.trim() ? 'var(--al-primary)' : 'var(--al-t3)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: input.trim() ? 'pointer' : 'default', transition: 'all 0.2s', flexShrink: 0 }}
                >
                  <ArrowUp size={20} color="#fff" />
                </button>
              </div>

              {/* Suggestion chips */}
              <div className="al-chips" style={{ display: 'flex', gap: 10, animation: 'msgIn 0.5s ease 0.2s both' }}>
                {chips.map(c => (
                  <button
                    key={c}
                    onClick={() => send(c.replace(/^#/, ''))}
                    className="al-btn"
                    style={{ background: 'var(--al-card)', border: '1px solid var(--al-border)', borderRadius: 50, padding: '8px 20px', fontSize: 14, color: 'var(--al-t2)', fontWeight: 500, cursor: 'pointer', transition: 'all 0.15s' }}
                  >
                    {c}
                  </button>
                ))}
                <button 
                  onClick={() => setSg(s => s + 1)}
                  style={{ background: 'transparent', border: 'none', color: 'var(--al-primary)', fontSize: 14, fontWeight: 600, cursor: 'pointer', padding: '8px' }}
                >
                  More ideas +
                </button>
              </div>
            </div>
          )}

          {/* ─── CHAT / RESULTS VIEW ─── */}
          {view === 'chat' && (
            <div className="al-chat" style={{ maxWidth: 860, margin: '0 auto', padding: '32px 24px 120px' }}>
              {msgs.map((msg, idx) => (
                <div key={msg.id} style={{ marginBottom: 32, animation: 'msgIn 0.4s ease both' }}>

                  {/* User message */}
                  {msg.role === 'user' && (
                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 24 }}>
                      <div style={{ background: 'var(--al-pri-sub)', borderRadius: 24, padding: '14px 28px', fontSize: 16, color: 'var(--al-t1)', maxWidth: '80%', textAlign: 'center', fontWeight: 500 }}>
                        {msg.text}
                      </div>
                    </div>
                  )}

                  {/* AI response */}
                  {msg.role === 'ai' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
                      <div style={{ background: 'var(--al-card)', borderRadius: 28, padding: '28px', border: '1px solid var(--al-border)', boxShadow: '0 4px 20px rgba(0,0,0,0.04)' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18 }}>
                          <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'var(--al-primary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Sparkles size={16} color="#fff" />
                          </div>
                          <span style={{ fontWeight: 700, fontSize: 15, color: 'var(--al-primary)' }}>Aether Analyst</span>
                        </div>

                        <p style={{ fontSize: 16, color: 'var(--al-t2)', lineHeight: 1.75, marginBottom: 20 }}>
                          {msg.text}
                        </p>

                        <div style={{ display: 'flex', gap: 10 }}>
                          <button
                            onClick={() => refine(msg.text)}
                            className="al-action-btn"
                            style={{ background: 'transparent', border: '1px solid var(--al-border)', borderRadius: 50, padding: '7px 18px', fontSize: 14, color: 'var(--al-t2)', fontWeight: 500, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}
                          >
                            <RefreshCw size={14} /> Refine Prompt
                          </button>
                        </div>
                      </div>

                      {msg.stocks && msg.stocks.length > 0 && (
                        <div style={{ display: 'flex', gap: 16, overflowX: 'auto', paddingBottom: 10 }}>
                          {msg.stocks.map((s, i) => (
                            <div key={`${msg.id}-${i}`} style={{ flexShrink: 0, animation: `msgIn 0.4s ease ${i * 0.1}s both` }}>
                              <StockCard stock={s} />
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div style={{ display: 'flex', gap: 12, alignItems: 'center', padding: '20px' }}>
                   <div style={{ display: 'flex', gap: 4 }}>
                    {[0,1,2].map(i => (
                      <div key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--al-primary)', animation: `dot 1s ${i * 0.2}s infinite` }} />
                    ))}
                  </div>
                  <span style={{ fontSize: 14, color: 'var(--al-t3)', fontWeight: 500 }}>Analyzing data...</span>
                </div>
              )}
              <div ref={chatEnd} />
            </div>
          )}
        </main>

        {/* ════════════ INPUT BAR ════════════ */}
        {view === 'chat' && (
          <div className="al-followup" style={{ position: 'fixed', bottom: 0, left: 0, right: 0, padding: '0 24px 24px', background: 'linear-gradient(to top, var(--al-bg) 70%, transparent)' }}>
            <div style={{ maxWidth: 860, margin: '0 auto' }}>
              <div style={{ background: 'var(--al-card)', borderRadius: 50, border: '1px solid var(--al-border)', boxShadow: '0 10px 40px rgba(0,0,0,0.12)', display: 'flex', alignItems: 'center', padding: '8px 8px 8px 24px', gap: 12 }}>
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && send(input)}
                  placeholder="Type a follow-up..."
                  style={{ flex: 1, border: 'none', outline: 'none', fontSize: 15, color: 'var(--al-t1)', background: 'transparent' }}
                />
                <button
                  onClick={() => send(input)}
                  style={{ width: 44, height: 44, borderRadius: '50%', background: input.trim() ? 'var(--al-primary)' : 'var(--al-t3)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: input.trim() ? 'pointer' : 'default', transition: 'all 0.2s', flexShrink: 0 }}
                >
                  <ArrowUp size={20} color="#fff" />
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};

const SUGG = [
  ['#High growth Tech', '#Undervalued banks', '#Dividends for 2025'],
  ['#Blue chip picks', '#EV sector growth', '#AI infrastructure'],
  ['#Pharma recovery', '#Small cap gems', '#Green energy'],
];
