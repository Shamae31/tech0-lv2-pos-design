import BarcodeScanner from '../BarcodeScanner';
import InputBlock from './InputBlock';

type Props = {
  code: string;
  onChange: (value: string) => void;
  onAdd: () => void;
  onScan: (value: string) => Promise<void>;
};

export default function ProductEntry({ code, onChange, onAdd, onScan }: Props) {
  return (
    <InputBlock number="2" title="商品登録" description="バーコードを読み取るか、読み取れない場合は商品コードを手入力します。">
      <div className="control-row product-row">
        <label htmlFor="product-code">商品コード</label>
        <input
          id="product-code"
          value={code}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => event.key === 'Enter' && onAdd()}
          placeholder="商品コードを手入力"
        />
        <button onClick={onAdd}>検索・追加</button>
        <BarcodeScanner onScan={onScan} />
      </div>
      <p className="input-help">価格は商品マスタに登録された税抜単価を使用します。任意金額は入力できません。</p>
    </InputBlock>
  );
}
