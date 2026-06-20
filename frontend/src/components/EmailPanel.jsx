import { useEffect, useState } from 'react';

export default function EmailPanel({ onBack }) {
  const [emails, setEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mode, setMode] = useState('unread');
  const [selected, setSelected] = useState(null);

  const fetchEmails = async (m = mode) => {
    setLoading(true);
    setError(null);
    setSelected(null);
    try {
      const res = await fetch(`http://127.0.0.1:5000/api/emails?mode=${m}&limit=15`);
      const data = await res.json();
      if (data.error) {
        setError(data.error);
        setEmails([]);
      } else {
        setEmails(data.emails || []);
      }
    } catch (err) {
      setError('Could not connect to Alfred backend.');
      setEmails([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  const handleModeChange = (m) => {
    setMode(m);
    fetchEmails(m);
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
        <div id="panel-title">Email</div>
        <button id="panel-refresh" onClick={() => fetchEmails()} title="Refresh">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
        </button>
      </div>

      <div id="panel-tabs">
        <button className={`panel-tab${mode === 'unread' ? ' active' : ''}`} onClick={() => handleModeChange('unread')}>Unread</button>
        <button className={`panel-tab${mode === 'recent' ? ' active' : ''}`} onClick={() => handleModeChange('recent')}>Recent</button>
      </div>

      <div id="panel-body">
        {loading && <div className="panel-state">Loading emails...</div>}
        {error && <div className="panel-state panel-error">{error}</div>}
        {!loading && !error && emails.length === 0 && (
          <div className="panel-state">No emails found.</div>
        )}

        {!loading && !error && emails.length > 0 && !selected && (
          <div id="email-list">
            {emails.map((e, i) => (
              <div key={i} className="email-row" onClick={() => setSelected(e)}>
                <div className="email-row-top">
                  <span className="email-from">{e.from?.split('<')[0].trim() || e.from}</span>
                  <span className="email-date">{e.date?.split(',')[1]?.split(':')[0]?.trim() || ''}</span>
                </div>
                <div className="email-subject">{e.subject || '(No Subject)'}</div>
                <div className="email-snippet">{e.snippet}</div>
              </div>
            ))}
          </div>
        )}

        {selected && (
          <div id="email-detail">
            <button id="email-detail-back" onClick={() => setSelected(null)}>&larr; Back to list</button>
            <div className="email-detail-subject">{selected.subject}</div>
            <div className="email-detail-meta">
              <span>From: {selected.from}</span>
              <span>{selected.date}</span>
            </div>
            <div className="email-detail-body">{selected.snippet}</div>
          </div>
        )}
      </div>
    </div>
  );
}