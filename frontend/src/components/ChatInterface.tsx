'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Search, ArrowUp, RefreshCw, User, Sparkles, Moon, Sun, ExternalLink } from 'lucide-react';
import { sendChatMessage } from '@/lib/api';

type Msg = {
  id:      string;
  role:    'user' | 'ai';
  text:    string;
  sources?: string[];
};

export const ChatInterface: React.FC = () => {
  const [view,    setView]    = useState<'land' | 'chat'>('land');
  const [input,   setInput]   = useState('');
  const [msgs,    setMsgs]    = useState<Msg[]>([]);
  const [loading, setLoading] = useState(false);
  const [dark,    setDark]    = useState(false);
  const chatEnd = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const saved = localStorage.getItem('groww-theme');
    if (saved === 'dark') setDark(true);
  }, []);

  useEffect(() => {
    localStorage.setItem('groww-theme', dark ? 'dark' : 'light');
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
        id: `ai-${Date.now()}`, role: 'ai',
        text: r.answer, sources: r.sources,
      }]);
    } catch (err) {
      setMsgs(p => [...p, {
        id: `err-${Date.now()}`, role: 'ai',
        text: 'Unable to connect to the server. Please try again.',
      }]);
      console.error('API error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={dark ? 'dark' : ''}>
      <style>{`
        :root {
          --bg: #f0faf6;
          --card: #ffffff;
          --primary: #00d09c;
          --pri-sub: rgba(0, 208, 156, 0.08);
          --t1: #0d2d20;
          --t2: #3d6b55;
          --t3: #8ab59f;
          --border: rgba(0, 208, 156, 0.2);
        }
        [data-theme='dark'] {
          --bg: #0a1a12;
          --card: #122418;
          --primary: #00d09c;
          --pri-sub: rgba(0, 208, 156, 0.1);
          --t1: #e8f5f0;
          --t2: #90c4ab;
          --t3: #4a7a60;
          --border: rgba(0, 208, 156, 0.18);
        }
        @keyframes msgIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        @keyframes dot   { 0%, 100% { opacity: 0.2; transform: scale(0.8); } 50% { opacity: 1; transform: scale(1.1); } }
        .chip:hover { background: var(--pri-sub) !important; border-color: var(--primary) !important; }
        .btn-icon:hover { opacity: 0.8; }
        @media (max-width: 640px) {
          .land-title { font-size: 36px !important; }
          .land-wrap  { padding: 60px 20px 40px !important; }
          .chat-wrap  { padding: 24px 16px 130px !important; }
          .bottom-bar { padding: 0 16px 16px !important; }
        }
      `}</style>

      <div style={{ minHeight: '100vh', background: 'var(--bg)', color: 'var(--t1)', display: 'flex', flexDirection: 'column', transition: 'background 0.3s, color 0.3s' }}>

        {/* NAVBAR */}
        <nav style={{ position: 'sticky', top: 0, zIndex: 100, background: 'var(--bg)', borderBottom: '1px solid var(--border)' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto', height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 24px' }}>
            <button
              onClick={() => setView('land')}
              style={{ fontWeight: 800, fontSize: 20, color: 'var(--primary)', background: 'none', border: 'none', cursor: 'pointer', letterSpacing: '-0.03em' }}
            >
              Groww MF Assistant
            </button>
            <div style={{ display: 'flex', gap: 10 }}>
              <button className="btn-icon" onClick={() => setDark(!dark)} style={{ width: 36, height: 36, borderRadius: '50%', border: '1px solid var(--border)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--t2)' }}>
                {dark ? <Sun size={16} /> : <Moon size={16} />}
              </button>
              <button className="btn-icon" style={{ width: 36, height: 36, borderRadius: '50%', border: '1px solid var(--border)', background: 'var(--card)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--t2)' }}>
                <User size={16} />
              </button>
            </div>
          </div>
        </nav>

        <main style={{ flex: 1 }}>

          {/* LANDING */}
          {view === 'land' && (
            <div className="land-wrap" style={{ maxWidth: 660, margin: '0 auto', padding: '90px 24px 60px', textAlign: 'center' }}>
              <div style={{ display: 'inline-block', background: 'var(--pri-sub)', border: '1px solid var(--border)', borderRadius: 50, padding: '6px 18px', fontSize: 13, color: 'var(--primary)', fontWeight: 600, marginBottom: 24, animation: 'msgIn 0.4s ease both' }}>
                Mutual Fund FAQ Chatbot
              </div>
              <h1 className="land-title" style={{ fontSize: 52, fontWeight: 900, color: 'var(--t1)', lineHeight: 1.08, letterSpacing: '-0.04em', marginBottom: 40, animation: 'msgIn 0.5s ease 0.05s both' }}>
                Ask anything about<br />Mutual Funds
              </h1>

              {/* Search box */}
              <div style={{ background: 'var(--card)', borderRadius: 50, boxShadow: '0 8px 30px rgba(0,0,0,0.07)', padding: '8px 8px 8px 24px', display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20, animation: 'msgIn 0.5s ease 0.1s both', border: '1px solid var(--border)' }}>
                <Search size={18} style={{ color: 'var(--t3)', flexShrink: 0 }} />
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && send(input)}
                  placeholder="What is expense ratio in mutual funds?"
                  style={{ flex: 1, border: 'none', outline: 'none', fontSize: 15, color: 'var(--t1)', background: 'transparent' }}
                />
                <button
                  onClick={() => send(input)}
                  style={{ width: 44, height: 44, borderRadius: '50%', background: input.trim() ? 'var(--primary)' : 'var(--t3)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: input.trim() ? 'pointer' : 'default', transition: 'all 0.2s', flexShrink: 0 }}
                >
                  <ArrowUp size={20} color="#fff" />
                </button>
              </div>

              {/* Suggestion chips */}
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10, justifyContent: 'center', animation: 'msgIn 0.5s ease 0.15s both' }}>
                {CHIPS.map(c => (
                  <button key={c} className="chip" onClick={() => send(c)}
                    style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 50, padding: '8px 18px', fontSize: 13, color: 'var(--t2)', fontWeight: 500, cursor: 'pointer', transition: 'all 0.15s' }}>
                    {c}
                  </button>
                ))}
              </div>

              <p style={{ marginTop: 32, fontSize: 12, color: 'var(--t3)', animation: 'msgIn 0.5s ease 0.2s both' }}>
                Not investment advice. For educational purposes only.
              </p>
            </div>
          )}

          {/* CHAT */}
          {view === 'chat' && (
            <div className="chat-wrap" style={{ maxWidth: 820, margin: '0 auto', padding: '32px 24px 120px' }}>
              {msgs.map(msg => (
                <div key={msg.id} style={{ marginBottom: 28, animation: 'msgIn 0.4s ease both' }}>

                  {msg.role === 'user' && (
                    <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                      <div style={{ background: 'var(--primary)', borderRadius: '20px 20px 4px 20px', padding: '12px 22px', fontSize: 15, color: '#fff', maxWidth: '75%', fontWeight: 500 }}>
                        {msg.text}
                      </div>
                    </div>
                  )}

                  {msg.role === 'ai' && (
                    <div style={{ display: 'flex', gap: 14, alignItems: 'flex-start' }}>
                      <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, marginTop: 4 }}>
                        <Sparkles size={16} color="#fff" />
                      </div>
                      <div style={{ background: 'var(--card)', borderRadius: '4px 20px 20px 20px', padding: '20px 24px', border: '1px solid var(--border)', boxShadow: '0 2px 16px rgba(0,0,0,0.04)', flex: 1 }}>
                        <p style={{ fontSize: 15, color: 'var(--t1)', lineHeight: 1.8, margin: 0, whiteSpace: 'pre-wrap' }}>
                          {msg.text}
                        </p>

                        {msg.sources && msg.sources.length > 0 && (
                          <div style={{ marginTop: 16, paddingTop: 14, borderTop: '1px solid var(--border)' }}>
                            <p style={{ fontSize: 12, color: 'var(--t3)', fontWeight: 600, marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Sources</p>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                              {msg.sources.map((src, i) => (
                                <a key={i} href={src} target="_blank" rel="noopener noreferrer"
                                  style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 13, color: 'var(--primary)', textDecoration: 'none', wordBreak: 'break-all' }}>
                                  <ExternalLink size={12} style={{ flexShrink: 0 }} />
                                  {src}
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        <button onClick={() => setInput(msg.text)}
                          style={{ marginTop: 14, background: 'transparent', border: '1px solid var(--border)', borderRadius: 50, padding: '6px 16px', fontSize: 13, color: 'var(--t2)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 6 }}>
                          <RefreshCw size={12} /> Ask again
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))}

              {loading && (
                <div style={{ display: 'flex', gap: 12, alignItems: 'center', paddingLeft: 48, paddingTop: 4 }}>
                  <div style={{ display: 'flex', gap: 4 }}>
                    {[0, 1, 2].map(i => (
                      <div key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: 'var(--primary)', animation: `dot 1s ${i * 0.2}s infinite` }} />
                    ))}
                  </div>
                  <span style={{ fontSize: 13, color: 'var(--t3)' }}>Searching FAQs...</span>
                </div>
              )}
              <div ref={chatEnd} />
            </div>
          )}
        </main>

        {/* BOTTOM INPUT BAR */}
        {view === 'chat' && (
          <div className="bottom-bar" style={{ position: 'fixed', bottom: 0, left: 0, right: 0, padding: '0 24px 20px', background: 'linear-gradient(to top, var(--bg) 70%, transparent)' }}>
            <div style={{ maxWidth: 820, margin: '0 auto' }}>
              <div style={{ background: 'var(--card)', borderRadius: 50, border: '1px solid var(--border)', boxShadow: '0 8px 32px rgba(0,0,0,0.1)', display: 'flex', alignItems: 'center', padding: '8px 8px 8px 24px', gap: 12 }}>
                <input
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && send(input)}
                  placeholder="Ask a follow-up question..."
                  style={{ flex: 1, border: 'none', outline: 'none', fontSize: 15, color: 'var(--t1)', background: 'transparent' }}
                />
                <button
                  onClick={() => send(input)}
                  style={{ width: 44, height: 44, borderRadius: '50%', background: input.trim() ? 'var(--primary)' : 'var(--t3)', border: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: input.trim() ? 'pointer' : 'default', transition: 'all 0.2s', flexShrink: 0 }}
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

const CHIPS = [
  'What is expense ratio?',
  'How does SIP work?',
  'What is ELSS lock-in period?',
  'Direct vs regular mutual funds',
  'What is NAV in mutual funds?',
  'How to complete KYC for Groww?',
];
