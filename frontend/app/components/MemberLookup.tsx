import InputBlock from './InputBlock';
import BarcodeScanner from '../BarcodeScanner';

type Props = {
  memberId: string;
  memberName: string;
  onChange: (value: string) => void;
  onLookup: () => void;
  onScan: (value: string) => Promise<void>;
};

export default function MemberLookup({ memberId, memberName, onChange, onLookup, onScan }: Props) {
  return (
    <InputBlock number="1" title="会員確認" description="会員IDは任意です。未入力の場合は非会員として続行します。">
      <div className="control-row">
        <label htmlFor="member-id">会員ID</label>
        <input
          id="member-id"
          value={memberId}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => event.key === 'Enter' && onLookup()}
          placeholder="会員IDを入力またはスキャン"
        />
        <button onClick={onLookup}>会員確認</button>
        <BarcodeScanner onScan={onScan} label="会員コードをカメラで読む" />
      </div>
      {memberName && <p className="member-chip">会員：{memberName}</p>}
    </InputBlock>
  );
}
