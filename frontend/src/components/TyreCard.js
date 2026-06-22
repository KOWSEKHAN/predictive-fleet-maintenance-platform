import React from 'react';
import './TyreCard.css';

const TyreCard = ({ tyre }) => {
  const getStatusColor = () => {
    if (tyre.replace) return 'danger';
    if (tyre.remaining_km < 5000) return 'warning';
    return 'success';
  };

  const getStatusText = () => {
    if (tyre.replace) return 'REPLACE IMMEDIATELY';
    if (tyre.remaining_km < 5000) return 'MONITOR CLOSELY';
    return 'HEALTHY';
  };

  const getStatusIcon = () => {
    if (tyre.replace) return '🔴';
    if (tyre.remaining_km < 5000) return '🟡';
    return '🟢';
  };

  const formatValue = (value, unit) => {
    return `${value.toFixed(1)} ${unit}`;
  };

  return (
    <div className={`tyre-card ${getStatusColor()}`}>
      <div className="tyre-header">
        <div className="tyre-id">{tyre.tyre_id}</div>
        <div className="tyre-status">
          <span className="status-icon">{getStatusIcon()}</span>
          <span className="status-text">{getStatusText()}</span>
        </div>
      </div>
      
      <div className="tyre-metrics">
        <div className="metric">
          <div className="metric-label">PSI</div>
          <div className="metric-value">{formatValue(tyre.psi, 'PSI')}</div>
          <div className="metric-bar">
            <div 
              className="metric-fill psi-fill" 
              style={{ width: `${Math.min((tyre.psi / 120) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
        
        <div className="metric">
          <div className="metric-label">Depth</div>
          <div className="metric-value">{formatValue(tyre.depth, 'mm')}</div>
          <div className="metric-bar">
            <div 
              className="metric-fill depth-fill" 
              style={{ width: `${Math.min((tyre.depth / 10) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
        
        <div className="metric">
          <div className="metric-label">Temperature</div>
          <div className="metric-value">{formatValue(tyre.temp, '°C')}</div>
          <div className="metric-bar">
            <div 
              className="metric-fill temp-fill" 
              style={{ width: `${Math.min((tyre.temp / 80) * 100, 100)}%` }}
            ></div>
          </div>
        </div>
      </div>
      
      <div className="tyre-footer">
        {tyre.replace ? (
          <div className="replace-alert">
            <span className="alert-icon">⚠️</span>
            <span className="alert-text">IMMEDIATE REPLACEMENT REQUIRED</span>
          </div>
        ) : (
          <div className="remaining-info">
            <span className="remaining-label">Remaining Distance:</span>
            <span className="remaining-value">{tyre.remaining_km.toLocaleString()} km</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default TyreCard;
