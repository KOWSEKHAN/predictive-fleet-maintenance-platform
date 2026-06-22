import React from 'react';
import TyreCard from './TyreCard';
import './Dashboard.css';

const Dashboard = ({ tyres, isLoading, sessionId, onReset }) => {
  if (!sessionId) {
    return (
      <div className="dashboard-empty">
        <div className="empty-state">
          <div className="empty-icon">🚛</div>
          <h2>Welcome to Predictive Fleet Dashboard</h2>
          <p>Upload a CSV file to start monitoring your fleet's tyre health</p>
          <div className="empty-features">
            <div className="feature">
              <span className="feature-icon">📊</span>
              <span>Real-time tyre monitoring</span>
            </div>
            <div className="feature">
              <span className="feature-icon">🔮</span>
              <span>AI-powered predictions</span>
            </div>
            <div className="feature">
              <span className="feature-icon">⏰</span>
              <span>Auto-cycling batches</span>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading tyre data...</p>
        </div>
      </div>
    );
  }

  if (tyres.length === 0) {
    return (
      <div className="dashboard-empty">
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h2>No tyre data available</h2>
          <p>Upload a new CSV file or check your data format</p>
          <button className="reset-btn" onClick={onReset}>
            Reset Session
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Fleet Tyre Status</h2>
        <div className="dashboard-stats">
          <div className="stat">
            <span className="stat-label">Total Tyres:</span>
            <span className="stat-value">{tyres.length}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Need Replacement:</span>
            <span className="stat-value warning">
              {tyres.filter(t => t.replace).length}
            </span>
          </div>
        </div>
      </div>
      
      <div className="tyre-grid">
        {tyres.map((tyre, index) => (
          <TyreCard key={tyre.tyre_id || index} tyre={tyre} />
        ))}
      </div>
      
      <div className="dashboard-footer">
        <button className="reset-btn" onClick={onReset}>
          Reset Session
        </button>
      </div>
    </div>
  );
};

export default Dashboard;
