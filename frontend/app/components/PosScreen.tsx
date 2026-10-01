'use client';

import { useEffect, useRef, useState } from 'react';
import { createPurchase, fetchMember, fetchProduct, quotePurchase } from '../lib/api';
import type { Product, PurchaseQuote, PurchaseResult } from '../lib/types';
import MemberLookup from './MemberLookup';
import ProductEntry from './ProductEntry';
import PurchaseList from './PurchaseList';
import PurchaseModal from './PurchaseModal';
import TransactionHistory from './TransactionHistory';

type Props = { token: string; cashierName: string; onLogout: () => void };

export default function PosScreen({ token, cashierName, onLogout }: Props) {
  const [memberId, setMemberId] = useState('');
  const [memberName, setMemberName] = useState('');
  const [confirmedMemberId, setConfirmedMemberId] = useState('');
  const [code, setCode] = useState('');
  const [items, setItems] = useState<Product[]>([]);
  const [message, setMessage] = useState('');
  const [result, setResult] = useState<PurchaseResult | null>(null);
  const [view, setView] = useState<'sales' | 'history'>('sales');
  const [quote, setQuote] = useState<{ key: string; value: PurchaseQuote } | null>(null);
  const [sending, setSending] = useState(false);
  const [refreshQuote, setRefreshQuote] = useState(0);
  const requestRef = useRef<{ key: string; id: string } | null>(null);
  const sendingRef = useRef(false);
  const memberIdRef = useRef(memberId);
  memberIdRef.current = memberId;
  const quoteKey = JSON.stringify({ member: confirmedMemberId, items: items.map(({ product_code, quantity }) => ({ product_code, quantity })) });
  const readyQuote = quote?.key === quoteKey ? quote.value : null;

  useEffect(() => {
    if (!items.length || (memberId.trim() && !confirmedMemberId)) return;
    let active = true;
    quotePurchase(token, confirmedMemberId || null, items).then((value) => {
      if (active) { setQuote({ key: quoteKey, value }); setMessage(''); }
    }).catch((error) => {
      if (active) { setQuote(null); setMessage(error instanceof Error ? error.message : '金額を取得できません'); }
    });
    return () => { active = false; };
  }, [token, quoteKey, refreshQuote, memberId, confirmedMemberId, items]);

  async function findMember() {
    const lookupId = memberId.trim();
    if (!lookupId) {
      setMemberName('');
      setConfirmedMemberId('');
      setMessage('非会員として続行します');
      return;
    }
    try {
      const member = await fetchMember(token, lookupId);
      if (memberIdRef.current.trim() !== lookupId) return;
      setMemberName(member.name);
      setConfirmedMemberId(member.member_id);
      setMessage(`会員: ${member.name}`);
    } catch (error) {
      if (memberIdRef.current.trim() !== lookupId) return;
      setMemberName('');
      setConfirmedMemberId('');
      setMessage(error instanceof Error ? error.message : '会員確認に失敗しました');
    }
  }

  async function addProduct(productCode = code) {
    if (!productCode.trim()) {
      setMessage('商品コードを入力してください');
      return;
    }
    try {
      const product = await fetchProduct(token, productCode.trim());
      setItems((current) => {
        const index = current.findIndex((item) => item.product_code === product.product_code);
        if (index < 0) return [...current, { ...product, quantity: 1 }];
        return current.map((item, itemIndex) => itemIndex === index ? { ...item, quantity: Math.min(99, item.quantity + 1) } : item);
      });
      setCode('');
      setMessage('商品を追加しました');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : '商品検索に失敗しました');
    }
  }

  async function purchase() {
    if (sendingRef.current || result || !readyQuote || (memberId.trim() && !confirmedMemberId)) return;
    sendingRef.current = true;
    setSending(true);
    if (requestRef.current?.key !== quoteKey) requestRef.current = { key: quoteKey, id: crypto.randomUUID() };
    try {
      setResult(await createPurchase(token, confirmedMemberId || null, items, requestRef.current.id, readyQuote.grand_total));
      setMessage('');
    } catch (error) {
      setMessage(error instanceof Error ? error.message : '購入確定に失敗しました');
      if (error instanceof Error && error.message.includes('金額が更新')) {
        requestRef.current = null;
        setRefreshQuote((value) => value + 1);
      }
    } finally {
      sendingRef.current = false;
      setSending(false);
    }
  }

  function closeResult() {
    setResult(null);
    setItems([]);
    setMemberId('');
    setMemberName('');
    setConfirmedMemberId('');
    setQuote(null);
    requestRef.current = null;
    setCode('');
    setMessage('');
  }

  function openHistoryFromResult() {
    closeResult();
    setView('history');
  }

  function changeQuantity(index: number, quantity: number) {
    const safeQuantity = Math.max(1, Math.min(99, quantity));
    setItems((current) => current.map((item, itemIndex) => itemIndex === index ? { ...item, quantity: safeQuantity } : item));
  }

  return (
    <>
      <main className="pos-shell">
        <header className="pos-header">
          <div className="app-title"><span>販売管理</span><h1>{view === 'sales' ? '販売登録' : '取引履歴'}</h1></div>
          <nav aria-label="業務メニュー">
            <button className={`nav-item ${view === 'sales' ? 'active' : ''}`} onClick={() => setView('sales')}>販売登録</button>
            <button className={`nav-item ${view === 'history' ? 'active' : ''}`} onClick={() => setView('history')}>取引履歴</button>
          </nav>
        </header>
        <div className="operator-bar">
          <div><span>ログイン中の担当者</span><strong>{cashierName}</strong></div>
          <button className="logout-button" onClick={onLogout}>ログアウト</button>
        </div>
        {view === 'sales' && message && <p className="status-message">{message}</p>}
        {view === 'sales' ? (
          <>
            <section className="input-panel">
              <MemberLookup
                memberId={memberId}
                memberName={memberName}
                onChange={(value) => {
                  setMemberId(value);
                  memberIdRef.current = value;
                  setMemberName('');
                  setConfirmedMemberId('');
                }}
                onLookup={findMember}
                onScan={async (value) => {
                  setMemberId(value);
                  memberIdRef.current = value;
                  setMemberName('');
                  setConfirmedMemberId('');
                  const member = await fetchMember(token, value);
                  if (memberIdRef.current !== value) return;
                  setMemberName(member.name);
                  setConfirmedMemberId(member.member_id);
                  setMessage(`会員: ${member.name}`);
                }}
              />
              <ProductEntry code={code} onChange={setCode} onAdd={() => { void addProduct(); }} onScan={async (value) => { await addProduct(value); }} />
            </section>
            <PurchaseList items={items} quote={readyQuote} sending={sending} onQuantityChange={changeQuantity} onDelete={(index) => setItems((current) => current.filter((_, itemIndex) => itemIndex !== index))} onPurchase={purchase} />
          </>
        ) : <TransactionHistory token={token} />}
      </main>
      {result && <PurchaseModal result={result} onClose={closeResult} onHistory={openHistoryFromResult} />}
    </>
  );
}
