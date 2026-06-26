import { useState, useEffect } from 'react';

const API = 'http://localhost:5000/api';

function formatDisplay(dtStr) {
  if (!dtStr || dtStr === 'None') return '';
  try {
    const dt = new Date(dtStr);
    return dt.toLocaleString('en-US', {
      timeZone: 'Asia/Karachi',
      weekday: 'short', month: 'short', day: 'numeric',
      hour: 'numeric', minute: '2-digit', hour12: true
    });
  } catch {
    return dtStr;
  }
}

function isOverdue(dtStr) {
  if (!dtStr) return false;
  return new Date(dtStr) < new Date();
}

export default function RemindersPanel() {
  const [reminders, setReminders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [showCompleted, setShowCompleted] = useState(false);
  const [form, setForm] = useState({ title: '', due_date: '', due_time: '' });

  useEffect(() => {
    fetchReminders();
  }, [showCompleted]);

  async function fetchReminders() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/reminders?include_completed=${showCompleted}`);
      const data = await res.json();
      setReminders(data.reminders || []);
    } catch (e) {
      setError('Failed to load reminders');
    } finally {
      setLoading(false);
    }
  }

  async function handleAdd(e) {
    e.preventDefault();
    if (!form.title || !form.due_date || !form.due_time) return;
    setSubmitting(true);
    try {
      const due_at = `${form.due_date}T${form.due_time}:00`;
      const res = await fetch(`${API}/reminders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title: form.title, due_at })
      });
      if (res.ok) {
        setForm({ title: '', due_date: '', due_time: '' });
        setShowForm(false);
        fetchReminders();
      }
    } catch (e) {
      setError('Failed to add reminder');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleComplete(id) {
    try {
      await fetch(`${API}/reminders/${id}/complete`, { method: 'PATCH' });
      fetchReminders();
    } catch (e) {
      setError('Failed to complete reminder');
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this reminder?')) return;
    try {
      await fetch(`${API}/reminders/${id}`, { method: 'DELETE' });
      fetchReminders();
    } catch (e) {
      setError('Failed to delete reminder');
    }
  }

  const pending = reminders.filter(r => !r.completed);
  const completed = reminders.filter(r => r.completed);

  return (
    <div style={{ padding: '24px', maxWidth: '700px', margin: '0 auto', color: 'var(--text-primary)' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, color: '#E8D5A3', fontSize: '22px', fontWeight: 500 }}>Reminders</h2>
        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setShowCompleted(s => !s)}
            style={{
              background: 'transparent', border: '1px solid rgba(232,213,163,0.2)',
              color: 'rgba(232,213,163,0.6)', padding: '8px 14px', borderRadius: '8px',
              cursor: 'pointer', fontSize: '13px'
            }}
          >
            {showCompleted ? 'Hide Done' : 'Show Done'}
          </button>
          <button
            onClick={() => setShowForm(f => !f)}
            style={{
              background: 'rgba(232,213,163,0.15)', border: '1px solid rgba(232,213,163,0.3)',
              color: '#E8D5A3', padding: '8px 16px', borderRadius: '8px',
              cursor: 'pointer', fontSize: '14px'
            }}
          >
            {showForm ? '✕ Cancel' : '+ Add Reminder'}
          </button>
        </div>
      </div>

      {/* Add Form */}
      {showForm && (
        <form onSubmit={handleAdd} style={{
          background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(232,213,163,0.2)',
          borderRadius: '12px', padding: '20px', marginBottom: '24px',
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px'
        }}>
          <input
            placeholder="Reminder title *"
            value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            required
            style={{ ...inputStyle, gridColumn: '1 / -1' }}
          />
          <input
            type="date"
            value={form.due_date}
            onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))}
            required
            style={inputStyle}
          />
          <input
            type="time"
            value={form.due_time}
            onChange={e => setForm(f => ({ ...f, due_time: e.target.value }))}
            required
            style={inputStyle}
          />
          <button
            type="submit"
            disabled={submitting}
            style={{
              gridColumn: '1 / -1', background: 'rgba(232,213,163,0.2)',
              border: '1px solid rgba(232,213,163,0.4)', color: '#E8D5A3',
              padding: '10px', borderRadius: '8px', cursor: 'pointer',
              fontSize: '14px', fontWeight: 500
            }}
          >
            {submitting ? 'Adding...' : 'Set Reminder'}
          </button>
        </form>
      )}

      {error && (
        <div style={{ color: '#ff6b6b', marginBottom: '16px', fontSize: '14px' }}>{error}</div>
      )}

      {loading ? (
        <div style={{ color: 'var(--text-secondary)', fontSize: '14px' }}>Loading...</div>
      ) : (
        <>
          {/* Pending */}
          {pending.length === 0 ? (
            <div style={{
              textAlign: 'center', padding: '48px 24px',
              color: 'var(--text-secondary)', fontSize: '14px',
              background: 'rgba(255,255,255,0.02)', borderRadius: '12px',
              border: '1px solid rgba(232,213,163,0.1)'
            }}>
              No pending reminders — ask Alfred to set one
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {pending.map(r => {
                const overdue = isOverdue(r.due_at);
                return (
                  <div key={r.id} style={{
                    background: overdue ? 'rgba(255,100,100,0.06)' : 'rgba(255,255,255,0.03)',
                    border: `1px solid ${overdue ? 'rgba(255,100,100,0.25)' : 'rgba(232,213,163,0.15)'}`,
                    borderRadius: '12px', padding: '16px 18px',
                    display: 'flex', alignItems: 'center', gap: '14px'
                  }}>
                    {/* Complete checkbox */}
                    <button
                      onClick={() => handleComplete(r.id)}
                      title="Mark complete"
                      style={{
                        width: '20px', height: '20px', borderRadius: '50%', flexShrink: 0,
                        border: `2px solid ${overdue ? 'rgba(255,100,100,0.5)' : 'rgba(232,213,163,0.4)'}`,
                        background: 'transparent', cursor: 'pointer'
                      }}
                    />

                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 500, fontSize: '14px', marginBottom: '4px' }}>
                        {r.title}
                      </div>
                      <div style={{
                        fontSize: '12px',
                        color: overdue ? 'rgba(255,120,120,0.8)' : 'rgba(232,213,163,0.6)'
                      }}>
                        {overdue ? '⚠ Overdue · ' : '🔔 '}{formatDisplay(r.due_at)}
                      </div>
                    </div>

                    <div style={{ display: 'flex', gap: '6px' }}>
                      <button
                        onClick={() => handleComplete(r.id)}
                        style={{
                          background: 'rgba(100,200,100,0.1)', border: '1px solid rgba(100,200,100,0.2)',
                          color: 'rgba(100,220,100,0.8)', padding: '5px 10px',
                          borderRadius: '6px', cursor: 'pointer', fontSize: '12px'
                        }}
                      >
                        Done
                      </button>
                      <button
                        onClick={() => handleDelete(r.id)}
                        style={{
                          background: 'transparent', border: '1px solid rgba(255,100,100,0.2)',
                          color: 'rgba(255,100,100,0.6)', padding: '5px 10px',
                          borderRadius: '6px', cursor: 'pointer', fontSize: '12px'
                        }}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {/* Completed */}
          {showCompleted && completed.length > 0 && (
            <div style={{ marginTop: '24px' }}>
              <div style={{ fontSize: '12px', color: 'rgba(232,213,163,0.4)', marginBottom: '10px' }}>
                COMPLETED
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {completed.map(r => (
                  <div key={r.id} style={{
                    background: 'rgba(255,255,255,0.02)', border: '1px solid rgba(255,255,255,0.06)',
                    borderRadius: '10px', padding: '12px 16px',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    opacity: 0.5
                  }}>
                    <div>
                      <div style={{ fontSize: '13px', textDecoration: 'line-through' }}>{r.title}</div>
                      <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>
                        {formatDisplay(r.due_at)}
                      </div>
                    </div>
                    <button
                      onClick={() => handleDelete(r.id)}
                      style={{
                        background: 'transparent', border: 'none',
                        color: 'rgba(255,100,100,0.5)', cursor: 'pointer', fontSize: '13px'
                      }}
                    >
                      ✕
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

const inputStyle = {
  background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(232,213,163,0.2)',
  color: 'var(--text-primary)', padding: '10px 12px', borderRadius: '8px',
  fontSize: '14px', width: '100%', boxSizing: 'border-box', outline: 'none'
};