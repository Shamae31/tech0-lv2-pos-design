import type { PurchaseResult } from '../lib/types';

type Props = { result: PurchaseResult; onClose: () => void; onHistory: () => void };

export default function PurchaseModal({ result, onClose, onHistory }: Props) {
  return (
    <div className="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="purchase-complete">
      <section className="result-card">
        <div className="complete-icon">✓</div>
        <h2 id="purchase-complete">販売を登録しました</h2>
        <p className="transaction-id">取引番号 {result.transaction_id}</p>
        <dl>
          <div><dt>税抜合計</dt><dd>¥{Number(result.subtotal).toLocaleString()}</dd></div>
          {Object.entries(result.tax_breakdown || {}).sort().map(([rate, value]) => (
            <div key={rate}><dt>{rate}%対象（税抜 ¥{Number(value.taxable_amount).toLocaleString()}）</dt><dd>¥{Number(value.tax_amount).toLocaleString()}</dd></div>
          ))}
          <div><dt>消費税合計</dt><dd>¥{Number(result.tax_total).toLocaleString()}</dd></div>
          <div className="grand-total"><dt>税込合計</dt><dd>¥{Number(result.grand_total).toLocaleString()}</dd></div>
        </dl>
        <div className="result-actions">
          <button className="return-button" autoFocus onClick={onClose}>販売画面に戻る</button>
          <button className="history-button" onClick={onHistory}>取引履歴を見る</button>
        </div>
      </section>
    </div>
  );
}
