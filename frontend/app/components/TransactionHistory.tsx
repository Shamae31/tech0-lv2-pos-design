'use client';

import { useEffect, useState } from 'react';
import { fetchTransactions } from '../lib/api';
import { yen } from '../lib/money';
import type { Transaction } from '../lib/types';

export default function TransactionHistory({ token }: { token: string }) {
  const [rows, setRows] = useState<Transaction[]>([]);
  const [error, setError] = useState('');
  const [page, setPage] = useState(0);

  useEffect(() => {
    fetchTransactions(token, page)
      .then(setRows)
      .catch((err) => setError(err instanceof Error ? err.message : '取引履歴を取得できません'));
  }, [token, page]);

  return (
    <section className="history-panel">
      <div className="history-heading">
        <div><h2>取引履歴</h2><p>確定済みの取引は閲覧専用です。</p></div>
        <button onClick={() => fetchTransactions(token, page).then(setRows).catch(() => setError('更新できませんでした'))}>更新</button>
      </div>
      {error && <p className="alert">{error}</p>}
      {rows.length === 0 ? <p className="empty-cart">確定済みの取引はありません</p> : (
        <div className="history-list">
          {rows.map((tx) => (
            <details key={tx.transaction_id}>
              <summary>
                <span><strong>{tx.transaction_id}</strong><small>{new Date(tx.purchased_at).toLocaleString('ja-JP')}／{tx.cashier_name}</small></span>
                <span>{tx.member_id ? `会員 ${tx.member_id}` : '非会員'}</span>
                <b>{yen(Number(tx.grand_total))}</b>
              </summary>
              <div className="history-details">
                {tx.details.map((detail, index) => (
                  <div className="history-line" key={index}>
                    <span>
                      <strong>{detail.product_name} × {detail.quantity}</strong>
                      <small>税抜単価 {yen(Number(detail.sold_unit_price))}／税率 {Number(detail.applied_tax_rate)}%</small>
                      {Number(detail.discount_amount) > 0 && <small>値引き −{yen(Number(detail.discount_amount))}</small>}
                    </span>
                    <small>税抜 {yen(Number(detail.line_total))}／消費税 {yen(Number(detail.tax_amount))}</small>
                    <strong>税込 {yen(Number(detail.line_total) + Number(detail.tax_amount))}</strong>
                  </div>
                ))}
                <dl className="history-totals">
                  <div><dt>値引き後の税抜小計</dt><dd>{yen(Number(tx.subtotal))}</dd></div>
                  <div><dt>消費税</dt><dd>{yen(Number(tx.tax_total))}</dd></div>
                  <div className="history-grand-total"><dt>税込合計</dt><dd>{yen(Number(tx.grand_total))}</dd></div>
                </dl>
              </div>
            </details>
          ))}
        </div>
      )}
      <div className="history-pagination">
        <button disabled={page === 0} onClick={() => setPage(page - 1)}>前のページ</button>
        <span>{page + 1}ページ</span>
        <button disabled={rows.length < 50} onClick={() => setPage(page + 1)}>次のページ</button>
      </div>
    </section>
  );
}
