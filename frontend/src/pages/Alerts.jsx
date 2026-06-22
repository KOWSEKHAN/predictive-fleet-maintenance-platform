import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { fetchAlerts } from '../services/api';
import './Alerts.css';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const data = await fetchAlerts(1);
      // Handle paginated response: { count, next, previous, results }
      setAlerts(Array.isArray(data) ? data : (data.results || []));
    } catch (e) {
      console.error('Alerts failed to load alerts records list', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Reduced from 5 000 ms → 15 000 ms (alerts are time-sensitive)
    const interval = setInterval(loadData, 15000);
    return () => clearInterval(interval);
  }, []);

  const getAlertDetails = (alertItem) => {
    if (alertItem.condition === 'Bad') {
      return {
        title: 'Immediate Replacement Required',
        desc: `Vehicle ${alertItem.vehicle_number} has a critical tyre (${alertItem.tyre_position}) in bad condition.`,
        severity: 'critical',
        badge: 'Critical'
      };
    }
    if (alertItem.psi < 80) {
      return {
        title: 'Low Pressure Warning',
        desc: `Tyre ${alertItem.tyre_position} on Vehicle ${alertItem.vehicle_number} is under-inflated at ${alertItem.psi} PSI.`,
        severity: 'warning',
        badge: 'Warning'
      };
    }
    if (alertItem.temp > 50) {
      return {
        title: 'High Temperature Detected',
        desc: `Tyre ${alertItem.tyre_position} on Vehicle ${alertItem.vehicle_number} is running hot at ${alertItem.temp} C.`,
        severity: 'warning',
        badge: 'Warning'
      };
    }
    return {
      title: 'Maintenance Advisory',
      desc: `Wear check recommended for ${alertItem.tyre_position} on Vehicle ${alertItem.vehicle_number}.`,
      severity: 'info',
      badge: 'Info'
    };
  };

  if (loading && alerts.length === 0) {
    return <div className="page-loading">Scanning sensors for alerts...</div>;
  }

  return (
    <div className="main-content">
      <Navbar title="Active Fleet Alerts" />
      <div className="alerts-content">
        
        <div className="alerts-list">
          {alerts.length > 0 ? (
            alerts.map(item => {
              const details = getAlertDetails(item);
              return (
                <div key={item.id} className={`alert-card glass ${details.severity}`}>
                  <div className="alert-card-header">
                    <span className="severity-badge">{details.badge}</span>
                    <span className="alert-timestamp">
                      {new Date(item.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="alert-card-body">
                    <h3>{details.title}</h3>
                    <p>{details.desc}</p>
                    <div className="alert-meta">
                      <span><strong>PSI:</strong> {item.psi}</span>
                      <span><strong>Temp:</strong> {item.temp} C</span>
                      <span><strong>Depth:</strong> {item.depth}mm</span>
                      <span><strong>Risk Score:</strong> {item.risk_score}%</span>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="no-alerts glass">
              All tyre sensors operating within nominal parameters. No active alerts.
            </div>
          )}
        </div>

      </div>
    </div>
  );
};

export default Alerts;
