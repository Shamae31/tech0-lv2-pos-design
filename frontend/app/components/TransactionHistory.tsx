'use client';
import { useEffect, useState } from 'react';
import { fetchTransactions } from '../lib/api';
import type { Transaction } from '../lib/types';

export default function TransactionHistory({token}:{token:string}){
  const [rows,setRows]=useState<Transaction[]>([]); const [error,setError]=useState(''); const [page,setPage]=useState(0);
  useEffect(()=>{fetchTransactions(token,page).then(setRows).catch(err=>setError(err instanceof Error?err.message:'取引履歴を取得できません'))},[token,page]);
  return <section className="history-panel"><div className="history-heading"><div><h2>取引履歴</h2><p>確定済みの取引は閲覧専用です。</p></div><button onClick={()=>fetchTransactions(token,page).then(setRows).catch(()=>setError('更新できませんでした'))}>更新</button></div>{error&&<p className="alert">{error}</p>}{rows.length===0?<p className="empty-cart">確定済みの取引はありません</p>:<div className="history-list">{rows.map(tx=><details key={tx.transaction_id}><summary><span><strong>{tx.transaction_id}</strong><small>{new Date(tx.purchased_at).toLocaleString('ja-JP')}／{tx.cashier_name}</small></span><span>{tx.member_id?`会員 ${tx.member_id}`:'非会員'}</span><b>税込 ¥{Number(tx.grand_total).toLocaleString()}</b></summary><div className="history-details">{tx.details.map((d,i)=><div key={i}><span>{d.product_name} × {d.quantity}</span><small>税抜単価 ¥{Number(d.sold_unit_price).toLocaleString()}／税率 {Number(d.applied_tax_rate)}%</small><strong>¥{Number(d.line_total+d.tax_amount).toLocaleString()}</strong></div>)}</div></details>)}</div>}<div className="history-pagination"><button disabled={page===0} onClick={()=>setPage(page-1)}>前のページ</button><span>{page+1}ページ</span><button disabled={rows.length<50} onClick={()=>setPage(page+1)}>次のページ</button></div></section>;
}
