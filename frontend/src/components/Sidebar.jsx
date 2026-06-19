export default function Sidebar({ alfredState, stateConfig, activeNav, setActiveNav }) {
  const cfg = stateConfig[alfredState];

  const navItems = [
    {
      label: 'New Chat',
      icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M12 5v14M5 12h14"/></svg>
    },
    {
      label: 'Chat History',
      icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
    },
    {
      label: 'Voice',
      icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0014 0M12 19v3M8 22h8"/></svg>
    },
  ];

  const toolItems = [
    {
      label: 'Email',
      icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
    },
    {
      label: 'Calendar',
      icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
    },
    {
      label: 'Memory',
      icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>
    },
    {
      label: 'Reminders',
      icon: <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 01-3.46 0"/></svg>
    },
  ];

  return (
    <aside id="sidebar">
      <div className="sidebar-brand">
        <div className="name">Alfred</div>
        <div className="sub">AI Assistant</div>
      </div>

      <div
        className="state-pill"
        style={{ borderColor: cfg.pillColor, background: cfg.bg }}
      >
        <span
          className={`state-dot${alfredState !== 'idle' ? ' pulse' : ''}`}
          style={{ background: cfg.dot }}
        />
        <span className="state-label-text" style={{ color: cfg.pillColor }}>
          {cfg.label}
        </span>
      </div>

      <div className="nav-section">Chat</div>

      <div id="nav-list">
        {navItems.map(item => (
          <button
            key={item.label}
            className={`nav-btn${activeNav === item.label ? ' active' : ''}`}
            onClick={() => setActiveNav(item.label)}
          >
            {item.icon}
            {item.label}
          </button>
        ))}

        <div className="nav-divider" />
        <div className="nav-section" style={{ padding: '0 10px 6px' }}>Tools</div>

        {toolItems.map(item => (
          <button
            key={item.label}
            className={`nav-btn${activeNav === item.label ? ' active' : ''}`}
            onClick={() => setActiveNav(item.label)}
          >
            {item.icon}
            {item.label}
          </button>
        ))}
      </div>

      <div className="nav-divider" />

      <div className="nav-bottom">
        <button className="nav-btn" onClick={() => setActiveNav('Settings')}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 00.33 1.82l.06.06a2 2 0 010 2.83 2 2 0 01-2.83 0l-.06-.06a1.65 1.65 0 00-1.82-.33 1.65 1.65 0 00-1 1.51V21a2 2 0 01-2 2 2 2 0 01-2-2v-.09A1.65 1.65 0 009 19.4a1.65 1.65 0 00-1.82.33l-.06.06a2 2 0 01-2.83 0 2 2 0 010-2.83l.06-.06A1.65 1.65 0 004.68 15a1.65 1.65 0 00-1.51-1H3a2 2 0 01-2-2 2 2 0 012-2h.09A1.65 1.65 0 004.6 9a1.65 1.65 0 00-.33-1.82l-.06-.06a2 2 0 010-2.83 2 2 0 012.83 0l.06.06A1.65 1.65 0 009 4.68a1.65 1.65 0 001-1.51V3a2 2 0 012-2 2 2 0 012 2v.09a1.65 1.65 0 001 1.51 1.65 1.65 0 001.82-.33l.06-.06a2 2 0 012.83 0 2 2 0 010 2.83l-.06.06A1.65 1.65 0 0019.4 9a1.65 1.65 0 001.51 1H21a2 2 0 012 2 2 2 0 01-2 2h-.09a1.65 1.65 0 00-1.51 1z"/></svg>
          Settings
        </button>
        <button className="nav-btn" onClick={() => setActiveNav('Profile')}>
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
          Profile
        </button>
      </div>
    </aside>
  );
}