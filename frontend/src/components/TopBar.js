import React, { useState, useEffect } from 'react';
import './TopBar.css';

const TopBar = ({ onUploadClick, sessionId, currentBatch, batchCount }) => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      setCurrentTime(now);
      setCurrentDate(now);
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <div className="topbar">
      <div className="topbar-left">
        <div className="datetime">
          <div className="time">{formatTime(currentTime)}</div>
          <div className="date">{formatDate(currentDate)}</div>
        </div>
        <div className="location">
          <span className="location-icon">📍</span>
          <span>Fleet HQ, Main Depot</span>
        </div>
      </div>
      
      <div className="topbar-center">
        <h1 className="title">Predictive Fleet Dashboard</h1>
        {sessionId && (
          <div className="session-info">
            <span>Batch {currentBatch + 1} of {batchCount}</span>
          </div>
        )}
      </div>
      
      <div className="topbar-right">
        <button className="upload-btn" onClick={onUploadClick}>
          <span className="upload-icon">📁</span>
          Upload CSV
        </button>
        <div className="notification-icon">
          <span>🔔</span>
        </div>
      </div>
    </div>
  );
};

export default TopBar;
