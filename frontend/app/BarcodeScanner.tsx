'use client';

import { useEffect, useId, useRef, useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

type Props = { onScan: (value: string) => Promise<void>; label?: string };

export default function BarcodeScanner({ onScan, label = '商品コードをカメラで読む' }: Props) {
  const region = `reader-${useId().replace(/:/g, '')}`;
  const scanner = useRef<Html5Qrcode | null>(null);
  const busy = useRef(false);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => () => {
    const active = scanner.current;
    scanner.current = null;
    if (active) void active.stop().catch(() => {}).then(() => active.clear());
  }, []);

  async function start() {
    if (scanner.current) return;
    const instance = new Html5Qrcode(region);
    scanner.current = instance;
    setError('');
    try {
      await instance.start({ facingMode: 'environment' }, { fps: 5, qrbox: { width: 260, height: 160 } }, (value) => {
        if (busy.current) return;
        busy.current = true;
        void onScan(value).catch(() => setError('読取後の確認に失敗しました')).finally(() => {
          window.setTimeout(() => { busy.current = false; }, 800);
        });
      }, () => {});
      setRunning(true);
    } catch {
      scanner.current = null;
      setError('カメラを起動できません。権限とHTTPS接続を確認してください。');
      instance.clear();
    }
  }

  async function stop() {
    const active = scanner.current;
    scanner.current = null;
    if (!active) return;
    await active.stop().catch(() => {});
    active.clear();
    setRunning(false);
  }

  return <div className="scanner-control">
    <div id={region} />
    <button className={`camera-button ${running ? 'active' : ''}`} onClick={running ? stop : start}>{running ? 'カメラ停止' : label}</button>
    {error && <small role="alert">{error}</small>}
  </div>;
}
