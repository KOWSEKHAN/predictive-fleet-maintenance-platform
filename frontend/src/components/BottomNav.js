import React from 'react';
import './BottomNav.css';

const BottomNav = () => {
  const navItems = [
    { icon: '🏠', label: 'Home'},
    { icon: '🗺️', label: 'Map' },
    { icon: '🔧', label: 'Tire Health', active: true  },
    { icon: '🎵', label: 'Music' },
    { icon: '⚙️', label: 'Settings' }
  ];

  return (
    <div className="bottom-nav">
      {navItems.map((item, index) => (
        <div 
          key={index} 
          className={`nav-item ${item.active ? 'active' : ''}`}
        >
          <div className="nav-icon">{item.icon}</div>
          <div className="nav-label">{item.label}</div>
        </div>
      ))}
    </div>
  );
};

export default BottomNav;
