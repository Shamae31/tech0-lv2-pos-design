'use client';
import { useEffect, useState } from 'react';
import LoginScreen from './components/LoginScreen';
import PosScreen from './components/PosScreen';
import { loginCashier } from './lib/api';

export default function Page() {
  const [token, setToken] = useState('');
  const [cashierId, setCashierId] = useState('');
  const [cashierName, setCashierName] = useState('');
  const [error, setError] = useState('');
  useEffect(() => setCashierId(localStorage.getItem('pos:lastCashierId') || ''), []);

  async function login(password: string) {
    setError('');
    try {
      const result = await loginCashier(cashierId.trim(), password);
      localStorage.setItem('pos:lastCashierId', cashierId.trim());
      setToken(result.access_token); setCashierName(result.cashier.display_name);
    } catch (err) { setError(err instanceof Error ? err.message : 'ログインに失敗しました'); }
  }

  function logout() {
    setToken('');
    setCashierName('');
    setError('');
  }

  return token
    ? <PosScreen token={token} cashierName={cashierName} onLogout={logout} />
    : <LoginScreen cashierId={cashierId} error={error} onCashierIdChange={setCashierId} onLogin={login} />;
}
