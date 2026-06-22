import React, { useContext, useState, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/dashboard',   icon: '📊', label: 'Dashboard'     },
  { to: '/fleet',       icon: '🚛', label: 'Fleet Overview' },
  { to: '/predictions', icon: '🔮', label: 'AI Predictions' },
  { to: '/alerts',      icon: '🚨', label: 'Alerts'         },
  { to: '/reports',     icon: '📋', label: 'Reports'        },
];

const Sidebar = () => {
  const { logoutUser, user } = useContext(AuthContext);
  const navigate  = useNavigate();
  const location  = useLocation();
  const [open, setOpen] = useState(false);

  // Close sidebar on route change (mobile)
  useEffect(() => { setOpen(false); }, [location.pathname]);

  // Prevent body scroll when mobile sidebar is open
  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : '';
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  const handleLogout = () => {
    logoutUser();
    navigate('/login');
  };

  return (
    <>
      {/* ── Mobile hamburger button ───────────────────────── */}
      <button
        className={`hamburger-btn ${open ? 'open' : ''}`}
        onClick={() => setOpen(o => !o)}
        aria-label={open ? 'Close navigation menu' : 'Open navigation menu'}
        aria-expanded={open}
      >
        <span /><span /><span />
      </button>

      {/* ── Backdrop overlay (mobile only) ────────────────── */}
      {open && (
        <div
          className="sidebar-overlay visible"
          onClick={() => setOpen(false)}
          aria-hidden="true"
        />
      )}

      {/* ── Sidebar panel ─────────────────────────────────── */}
      <aside className={`sidebar ${open ? 'sidebar--open' : ''}`} aria-label="Main navigation">
        <div className="sidebar-brand">
          <span className="brand-logo" aria-hidden="true">🚛</span>
          <span className="brand-name">FleetCare AI</span>
        </div>

        <div className="sidebar-company">
          <span className="company-title">Company</span>
          <span className="company-name">{user?.company?.company_name || 'My Fleet'}</span>
        </div>

        <nav className="sidebar-nav" role="navigation">
          {NAV_ITEMS.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span className="nav-icon" aria-hidden="true">{icon}</span>
              <span className="nav-text">{label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button onClick={handleLogout} className="logout-btn">
            <span className="nav-icon" aria-hidden="true">🚪</span>
            <span className="nav-text">Logout</span>
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
