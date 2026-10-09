import { useState } from 'react';

export default function App() {
  const [token, setToken] = useState(null);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [statusText, setStatusText] = useState('Idle');

  const handleLogin = async (e) => {
    e.preventDefault();
    setStatusText('Authenticating...');
    try {
      const res = await fetch('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      if (!res.ok) throw new Error('Authentication Failed');
      const data = await res.json();
      setToken(data.access_token);
      setStatusText('Authenticated Successfully');
    } catch {
      setStatusText('Authentication Error');
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="w-full max-w-md bg-slate-800 rounded-xl p-8 border border-slate-700 shadow-2xl">
        <h1 className="text-2xl font-bold mb-4 text-center text-cyan-400">
          Production Operations Hub
        </h1>
        <p data-testid="status-indicator" className="text-sm text-center mb-6 text-slate-400">
          Status: {statusText}
        </p>

        {!token ? (
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs uppercase text-slate-400 mb-1">Email</label>
              <input
                data-testid="email-input"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
            <div>
              <label className="block text-xs uppercase text-slate-400 mb-1">Password</label>
              <input
                data-testid="password-input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded text-white"
              />
            </div>
            <button
              data-testid="login-submit"
              type="submit"
              className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 rounded font-semibold text-white transition"
            >
              Sign In
            </button>
          </form>
        ) : (
          <div className="space-y-4">
            <div data-testid="dashboard-view" className="p-4 bg-slate-900 rounded border border-slate-700">
              <h2 className="text-md font-semibold text-emerald-400">Secure Dashboard</h2>
              <p className="text-xs text-slate-400 mt-1">Logged in as: {email}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}