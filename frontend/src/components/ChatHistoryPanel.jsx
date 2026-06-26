import { useEffect, useState } from 'react';

export default function ChatHistoryPanel({ onBack, onSelectSession }) {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchSessions = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch('http://127.0.0.1:5000/api/sessions');
      const data = await res.json();
      setSessions(data.sessions || []);
    } catch (err) {
      setError('Could not connect to Alfred backend.');
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const formatDate = (iso) => {
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
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
        <div id="panel-title">Chat History</div>
        <button id="panel-refresh" onClick={fetchSessions} title="Refresh">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
        </button>
      </div>

      <div id="panel-body">
        {loading && <div className="panel-state">Loading chat history...</div>}
        {error && <div className="panel-state panel-error">{error}</div>}

        {!loading && !error && sessions.length === 0 && (
          <div className="panel-state">No past conversations yet, Mr. Maaz.</div>
        )}

        {!loading && !error && sessions.length > 0 && (
          <div id="email-list">
            {sessions.map((s) => (
              <div
                key={s.session_id}
                className="email-row"
                onClick={() => onSelectSession(s.session_id)}
              >
                <div className="email-row-top">
                  <span className="email-from">{formatDate(s.started_at)}</span>
                </div>
                <div className="email-subject">{s.first_message}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}