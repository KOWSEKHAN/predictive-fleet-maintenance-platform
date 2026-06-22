import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { fetchPredictions } from '../services/api';
import './Predictions.css';

const Predictions = () => {
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const data = await fetchPredictions(1);
      // Handle paginated response: { count, next, previous, results }
      setPredictions(Array.isArray(data) ? data : (data.results || []));
    } catch (e) {
      console.error('Predictions failed to retrieve logs list', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Reduced from 5 000 ms → 60 000 ms (predictions change slowly)
    const interval = setInterval(loadData, 60000);
    return () => clearInterval(interval);
  }, []);

  const getRecommendation = (pred) => {
    if (pred.condition === 'Bad' || pred.remaining_km <= 2000) {
      return { text: 'Replace within 7 days', type: 'critical' };
    }
    if (pred.psi < 80 || pred.psi > 115) {
      return { text: 'Monitor pressure immediately', type: 'warning' };
    }
    if (pred.temp > 50) {
      return { text: 'Temperature anomaly detected', type: 'warning' };
    }
    return { text: 'Normal monitoring schedule', type: 'normal' };
  };

  if (loading && predictions.length === 0) {
    return <div className="page-loading">Calculating AI models...</div>;
  }

  return (
    <div className="main-content">
      <Navbar title="AI Predictions &amp; Recommendations" />
      <div className="predictions-content">
        
        <div className="table-wrapper glass">
          <table className="predictions-table">
            <thead>
              <tr>
                <th>Vehicle</th>
                <th>Tyre Position</th>
                <th>Predicted Condition</th>
                <th>RUL (Remaining KM)</th>
                <th>Risk Score</th>
                <th>AI Recommendation</th>
              </tr>
            </thead>
            <tbody>
              {predictions.length > 0 ? (
                predictions.map(pred => {
                  const rec = getRecommendation(pred);
                  return (
                    <tr key={pred.id}>
                      <td><strong>{pred.vehicle_number}</strong></td>
                      <td>{pred.tyre_position}</td>
                      <td>
                        <span className={`cond-badge ${pred.condition.toLowerCase()}`}>
                          {pred.condition}
                        </span>
                      </td>
                      <td>{pred.remaining_km.toLocaleString()} km</td>
                      <td>
                        <div className="risk-indicator">
                          <span className="risk-num">{pred.risk_score}%</span>
                          <div className="risk-bar-bg">
                            <div className="risk-bar-fill" style={{ width: `${pred.risk_score}%`, backgroundColor: pred.risk_score > 70 ? '#ef4444' : pred.risk_score > 40 ? '#f59e0b' : '#10b981' }}></div>
                          </div>
                        </div>
                      </td>
                      <td>
                        <span className={`rec-tag ${rec.type}`}>
                          {rec.text}
                        </span>
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="6" className="empty-table">No forecasts recorded. Ensure simulator is active.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
};

export default Predictions;
