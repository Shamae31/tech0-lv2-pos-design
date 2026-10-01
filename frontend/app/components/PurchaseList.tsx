import { useState } from 'react';
import { yen } from '../lib/money';
import type { Product, PurchaseQuote } from '../lib/types';

type Props = {
  items: Product[];
  quote: PurchaseQuote | null;
  sending: boolean;
  onQuantityChange: (index: number, quantity: number) => void;
  onDelete: (index: number) => void;
  onPurchase: () => void;
};

export default function PurchaseList({ items, quote, sending, onQuantityChange, onDelete, onPurchase }: Props) {
  const [selectedCode, setSelectedCode] = useState<string | null>(null);
  return (
    <section className="cart-panel">
      <h2>購入リスト</h2>
      {items.length === 0 ? (
        <p className="empty-cart">商品を登録するとここに表示されます</p>
      ) : (
        <ul>
          {items.map((item, index) => (
            <li key={item.product_code} className={selectedCode === item.product_code ? 'selected-item' : ''} onClick={() => setSelectedCode(item.product_code)}>
              <ProductImage product={item} />
              <span>
                <strong>{item.product_name}</strong>
                <small>税抜単価 {yen(item.current_unit_price)}（税率{item.tax_rate}%）</small>
                {quote?.details.find((detail) => detail.product_code === item.product_code) && <small>
                  小計 {yen(Number(quote.details.find((detail) => detail.product_code === item.product_code)!.line_total))}
                  {Number(quote.details.find((detail) => detail.product_code === item.product_code)!.discount_amount) > 0 && `／値引き ${yen(Number(quote.details.find((detail) => detail.product_code === item.product_code)!.discount_amount))}`}
                </small>}
              </span>
              <label>
                数量
                <input
                  type="number"
                  min="1"
                  max="99"
                  value={item.quantity}
                  onChange={(event) => onQuantityChange(index, Number(event.target.value) || 1)}
                />
              </label>
              <button className="delete-button" onClick={() => onDelete(index)}>削除</button>
            </li>
          ))}
        </ul>
      )}
      {selectedCode && items.some((item) => item.product_code === selectedCode) && <p className="selected-summary">選択中：{items.find((item) => item.product_code === selectedCode)?.product_name}／税抜単価 {yen(items.find((item) => item.product_code === selectedCode)?.current_unit_price || 0)}／数量 {items.find((item) => item.product_code === selectedCode)?.quantity}</p>}
      <div className="checkout-row">
        <div>
          <span>税抜合計 {quote ? yen(Number(quote.subtotal)) : '計算中'}　消費税 {quote ? yen(Number(quote.tax_total)) : '計算中'}</span>
          <strong>お支払い（税込） {quote ? yen(Number(quote.grand_total)) : '計算中'}</strong>
        </div>
        <button className="purchase-button" disabled={!items.length || !quote || sending} onClick={onPurchase}>{sending ? '処理中…' : '購入確定'}</button>
      </div>
    </section>
  );
}

function ProductImage({ product }: { product: Product }) {
  return (
    <div className="product-photo">
      {product.image_url ? <img src={product.image_url} alt="" /> : <span>{product.product_name.slice(0, 1)}</span>}
    </div>
  );
}
