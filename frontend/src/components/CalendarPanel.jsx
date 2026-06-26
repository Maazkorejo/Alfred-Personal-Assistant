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

function getDaysInMonth(year, month) {
  return new Date(year, month + 1, 0).getDate();
}

function getFirstDayOfMonth(year, month) {
  return new Date(year, month, 1).getDay();
}

export default function CalendarPanel() {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [today] = useState(new Date());
  const [viewYear, setViewYear] = useState(new Date().getFullYear());
  const [viewMonth, setViewMonth] = useState(new Date().getMonth());
  const [selectedDay, setSelectedDay] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({
    title: '', start_date: '', start_time: '', end_time: '', description: ''
  });

  useEffect(() => {
    fetchEvents();
  }, []);

  async function fetchEvents() {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API}/calendar`);
      const data = await res.json();
      setEvents(data.events || []);
    } catch (e) {
      setError('Failed to load events');
    } finally {
      setLoading(false);
    }
  }

  async function handleAddEvent(e) {
    e.preventDefault();
    if (!form.title || !form.start_date || !form.start_time) return;
    setSubmitting(true);
    try {
      const start_datetime = `${form.start_date} ${form.start_time}`;
      const end_datetime = form.end_time ? `${form.start_date} ${form.end_time}` : null;
      const res = await fetch(`${API}/calendar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: form.title,
          start_datetime,
          end_datetime,
          description: form.description || null,
        })
      });
      if (res.ok) {
        setForm({ title: '', start_date: '', start_time: '', end_time: '', description: '' });
        setShowForm(false);
        fetchEvents();
      }
    } catch (e) {
      setError('Failed to add event');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleDelete(id) {
    if (!window.confirm('Delete this event?')) return;
    try {
      await fetch(`${API}/calendar/${id}`, { method: 'DELETE' });
      fetchEvents();
    } catch (e) {
      setError('Failed to delete event');
    }
  }

  const monthNames = ['January','February','March','April','May','June',
                      'July','August','September','October','November','December'];

  function prevMonth() {
    if (viewMonth === 0) { setViewMonth(11); setViewYear(y => y - 1); }
    else setViewMonth(m => m - 1);
    setSelectedDay(null);
  }

  function nextMonth() {
    if (viewMonth === 11) { setViewMonth(0); setViewYear(y => y + 1); }
    else setViewMonth(m => m + 1);
    setSelectedDay(null);
  }

  const daysInMonth = getDaysInMonth(viewYear, viewMonth);
  const firstDay = getFirstDayOfMonth(viewYear, viewMonth);

  function getEventsForDay(day) {
    const dateStr = `${viewYear}-${String(viewMonth + 1).padStart(2,'0')}-${String(day).padStart(2,'0')}`;
    return events.filter(e => e.start_datetime && e.start_datetime.startsWith(dateStr));
  }

  const selectedDayEvents = selectedDay ? getEventsForDay(selectedDay) : [];

  const upcomingEvents = events.filter(e => {
    if (!e.start_datetime) return false;
    return new Date(e.start_datetime) >= new Date();
  }).slice(0, 10);

  return (
    <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto', color: 'var(--text-primary)' }}>

      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
        <h2 style={{ margin: 0, color: '#E8D5A3', fontSize: '22px', fontWeight: 500 }}>Calendar</h2>
        <button
          onClick={() => setShowForm(f => !f)}
          style={{
            background: 'rgba(232,213,163,0.15)', border: '1px solid rgba(232,213,163,0.3)',
            color: '#E8D5A3', padding: '8px 16px', borderRadius: '8px',
            cursor: 'pointer', fontSize: '14px'
          }}
        >
          {showForm ? '✕ Cancel' : '+ Add Event'}
        </button>
      </div>

      {/* Add Event Form */}
      {showForm && (
        <form onSubmit={handleAddEvent} style={{
          background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(232,213,163,0.2)',
          borderRadius: '12px', padding: '20px', marginBottom: '24px',
          display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px'
        }}>
          <input
            placeholder="Event title *"
            value={form.title}
            onChange={e => setForm(f => ({ ...f, title: e.target.value }))}
            required
            style={inputStyle}
          />
          <input
            placeholder="Description (optional)"
            value={form.description}
            onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
            style={inputStyle}
          />
          <input
            type="date"
            value={form.start_date}
            onChange={e => setForm(f => ({ ...f, start_date: e.target.value }))}
            required
            style={inputStyle}
          />
          <input
            type="time"
            value={form.start_time}
            onChange={e => setForm(f => ({ ...f, start_time: e.target.value }))}
            required
            style={inputStyle}
          />
          <input
            type="time"
            placeholder="End time (optional)"
            value={form.end_time}
            onChange={e => setForm(f => ({ ...f, end_time: e.target.value }))}
            style={inputStyle}
          />
          <button
            type="submit"
            disabled={submitting}
            style={{
              background: 'rgba(232,213,163,0.2)', border: '1px solid rgba(232,213,163,0.4)',
              color: '#E8D5A3', padding: '10px', borderRadius: '8px',
              cursor: 'pointer', fontSize: '14px', fontWeight: 500
            }}
          >
            {submitting ? 'Adding...' : 'Add Event'}
          </button>
        </form>
      )}

      {error && (
        <div style={{ color: '#ff6b6b', marginBottom: '16px', fontSize: '14px' }}>{error}</div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 320px', gap: '24px' }}>

        {/* Calendar Grid */}
        <div style={{
          background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(232,213,163,0.15)',
          borderRadius: '12px', padding: '20px'
        }}>
          {/* Month nav */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <button onClick={prevMonth} style={navBtnStyle}>‹</button>
            <span style={{ color: '#E8D5A3', fontWeight: 500, fontSize: '16px' }}>
              {monthNames[viewMonth]} {viewYear}
            </span>
            <button onClick={nextMonth} style={navBtnStyle}>›</button>
          </div>

          {/* Day headers */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px', marginBottom: '4px' }}>
            {['Su','Mo','Tu','We','Th','Fr','Sa'].map(d => (
              <div key={d} style={{ textAlign: 'center', fontSize: '11px', color: 'rgba(232,213,163,0.5)', padding: '4px 0' }}>{d}</div>
            ))}
          </div>

          {/* Day cells */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', gap: '2px' }}>
            {Array(firstDay).fill(null).map((_, i) => <div key={`empty-${i}`} />)}
            {Array(daysInMonth).fill(null).map((_, i) => {
              const day = i + 1;
              const isToday = day === today.getDate() && viewMonth === today.getMonth() && viewYear === today.getFullYear();
              const isSelected = day === selectedDay;
              const dayEvents = getEventsForDay(day);
              const hasEvents = dayEvents.length > 0;

              return (
                <div
                  key={day}
                  onClick={() => setSelectedDay(day === selectedDay ? null : day)}
                  style={{
                    textAlign: 'center', padding: '8px 4px', borderRadius: '8px',
                    cursor: 'pointer', fontSize: '13px', position: 'relative',
                    background: isSelected
                      ? 'rgba(232,213,163,0.2)'
                      : isToday
                      ? 'rgba(232,213,163,0.08)'
                      : 'transparent',
                    color: isToday ? '#E8D5A3' : 'var(--text-primary)',
                    border: isToday ? '1px solid rgba(232,213,163,0.3)' : '1px solid transparent',
                    fontWeight: isToday ? 500 : 400,
                  }}
                >
                  {day}
                  {hasEvents && (
                    <div style={{
                      width: '4px', height: '4px', borderRadius: '50%',
                      background: '#E8D5A3', margin: '2px auto 0', opacity: 0.8
                    }} />
                  )}
                </div>
              );
            })}
          </div>

          {/* Selected day events */}
          {selectedDay && (
            <div style={{ marginTop: '16px', borderTop: '1px solid rgba(232,213,163,0.1)', paddingTop: '16px' }}>
              <div style={{ fontSize: '13px', color: 'rgba(232,213,163,0.7)', marginBottom: '8px' }}>
                {monthNames[viewMonth]} {selectedDay}
              </div>
              {selectedDayEvents.length === 0 ? (
                <div style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>No events this day</div>
              ) : (
                selectedDayEvents.map(e => (
                  <div key={e.id} style={eventCardStyle}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <span style={{ fontWeight: 500, fontSize: '14px' }}>{e.title}</span>
                      <button onClick={() => handleDelete(e.id)} style={deleteBtnStyle}>✕</button>
                    </div>
                    <div style={{ fontSize: '12px', color: 'rgba(232,213,163,0.6)', marginTop: '4px' }}>
                      {formatDisplay(e.start_datetime)}
                    </div>
                    {e.description && (
                      <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '4px' }}>{e.description}</div>
                    )}
                  </div>
                ))
              )}
            </div>
          )}
        </div>

        {/* Upcoming Events Sidebar */}
        <div style={{
          background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(232,213,163,0.15)',
          borderRadius: '12px', padding: '20px'
        }}>
          <div style={{ fontSize: '13px', color: 'rgba(232,213,163,0.7)', marginBottom: '16px', fontWeight: 500 }}>
            Upcoming
          </div>
          {loading ? (
            <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>Loading...</div>
          ) : upcomingEvents.length === 0 ? (
            <div style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>No upcoming events</div>
          ) : (
            upcomingEvents.map(e => (
              <div key={e.id} style={{ ...eventCardStyle, marginBottom: '10px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <span style={{ fontWeight: 500, fontSize: '13px' }}>{e.title}</span>
                  <button onClick={() => handleDelete(e.id)} style={deleteBtnStyle}>✕</button>
                </div>
                <div style={{ fontSize: '11px', color: 'rgba(232,213,163,0.6)', marginTop: '4px' }}>
                  {formatDisplay(e.start_datetime)}
                </div>
                {e.description && (
                  <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>{e.description}</div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

const inputStyle = {
  background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(232,213,163,0.2)',
  color: 'var(--text-primary)', padding: '10px 12px', borderRadius: '8px',
  fontSize: '14px', width: '100%', boxSizing: 'border-box', outline: 'none'
};

const navBtnStyle = {
  background: 'transparent', border: '1px solid rgba(232,213,163,0.2)',
  color: '#E8D5A3', width: '32px', height: '32px', borderRadius: '8px',
  cursor: 'pointer', fontSize: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center'
};

const eventCardStyle = {
  background: 'rgba(232,213,163,0.06)', border: '1px solid rgba(232,213,163,0.15)',
  borderRadius: '8px', padding: '10px 12px', marginBottom: '8px'
};

const deleteBtnStyle = {
  background: 'transparent', border: 'none', color: 'rgba(255,100,100,0.6)',
  cursor: 'pointer', fontSize: '12px', padding: '0 0 0 8px', lineHeight: 1
};