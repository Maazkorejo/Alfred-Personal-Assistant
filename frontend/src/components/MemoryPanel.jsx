import { useEffect, useState } from 'react';

export default function MemoryPanel({ onBack }) {
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [confirmClear, setConfirmClear] = useState(false);
  const [clearing, setClearing] = useState(false);

  const fetchMemory = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://127.0.0.1:5000/api/memory');
      const data = await res.json();
      setHistory(data.history || []);
      setStats(data.stats || null);
    } catch (err) {
      setError('Could not connect to Alfred backend.');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchMemory();
  }, []);

  const handleClear = async () => {
    setClearing(true);
    try {
      await fetch('http://127.0.0.1:5000/api/memory', { method: 'DELETE' });
      setHistory([]);
      setStats({ total_messages: 0, first_message_at: null });
    } catch (err) {
      setError('Failed to clear memory.');
    }
    setClearing(false);
    setConfirmClear(false);
  };

  const formatDate = (iso) => {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div id="panel-wrap">
      <div id="panel-header">
        <button id="panel-back" onClick={onBack}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M19 12H5M12 19l-7-7 7-7"/>
          </svg>
          Back
        </button>
        <div id="panel-title">Memory</div>
        <button id="panel-refresh" onClick={fetchMemory} title="Refresh">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
        </button>
      </div>

      {stats && (
        <div id="memory-stats">
          <div className="mem-stat">
            <div className="mem-stat-val">{stats.total_messages}</div>
            <div className="mem-stat-label">Messages Stored</div>
          </div>
          <div className="mem-stat">
            <div className="mem-stat-val">{formatDate(stats.first_message_at)}</div>
            <div className="mem-stat-label">Remembering Since</div>
          </div>
        </div>
      )}

      <div id="panel-body">
        {loading && <div className="panel-state">Loading memory...</div>}
        {error && <div className="panel-state panel-error">{error}</div>}

        {!loading && !error && history.length === 0 && (
          <div className="panel-state">Alfred has no memories yet, Mr. Maaz.</div>
        )}

        {!loading && !error && history.length > 0 && (
          <div id="memory-list">
            {history.map((m, i) => (
              <div key={i} className={`memory-row ${m.role === 'user' ? 'memory-row-user' : 'memory-row-alfred'}`}>
                <div className="memory-row-label">{m.role === 'user' ? 'YOU' : 'ALFRED'}</div>
                <div className="memory-row-content">{m.content}</div>
              </div>
            ))}
          </div>
        )}
      </div>

      {history.length > 0 && (
        <div id="memory-footer">
          {!confirmClear ? (
            <button id="memory-clear-btn" onClick={() => setConfirmClear(true)}>
              Clear All Memory
            </button>
          ) : (
            <div id="memory-confirm">
              <span>Are you sure? This cannot be undone.</span>
              <button id="memory-confirm-yes" onClick={handleClear} disabled={clearing}>
                {clearing ? 'Clearing...' : 'Yes, Clear'}
              </button>
              <button id="memory-confirm-no" onClick={() => setConfirmClear(false)}>
                Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}