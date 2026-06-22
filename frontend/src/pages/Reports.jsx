import React, { useEffect, useState } from 'react';
import Navbar from '../components/Navbar';
import { fetchReportsSummary, fetchPredictions } from '../services/api';
import './Reports.css';

const Reports = () => {
  const [summary, setSummary] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const summaryData = await fetchReportsSummary();
      setSummary(summaryData);

      const predData = await fetchPredictions(1);
      // Handle paginated response: { count, next, previous, results }
      setPredictions(Array.isArray(predData) ? predData : (predData.results || []));
    } catch (e) {
      console.error('Reports failed to compile summaries statistics', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Reports are not time-critical; no polling needed
  }, []);

  const handleExportCSV = () => {
    if (predictions.length === 0) {
      alert("No prediction data to export. Make sure the simulator is active.");
      return;
    }
    
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Vehicle Number,Tyre Position,Condition,Remaining KM (RUL),Risk Score\n";
    
    predictions.forEach(pred => {
      const row = `${pred.vehicle_number},${pred.tyre_position},${pred.condition},${pred.remaining_km},${pred.risk_score}`;
      csvContent += row + "\n";
    });
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `predictive_fleet_report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading && !summary) {
    return <div className="page-loading">Compiling reports metrics...</div>;
  }

  return (
    <div className="main-content">
      <Navbar title="Fleet Analytics &amp; Reports" />
      <div className="reports-content">
        
        <div className="export-row glass">
          <h3>Download Complete Fleet Telemetry</h3>
          <button onClick={handleExportCSV} className="export-btn">
            Export to CSV
          </button>
        </div>

        <div className="reports-grid">
          
          <div className="report-card glass">
            <h2>Weekly Operations Summary</h2>
            <div className="report-stats">
              <div className="stat-line">
                <span className="stat-label">Active Monitored Vehicles</span>
                <span className="stat-val">{summary?.weekly_summary.vehicles_monitored}</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">Alerts Generated</span>
                <span className="stat-val warning">{summary?.weekly_summary.alerts_generated}</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">Critical Issues Resolved</span>
                <span className="stat-val success">{summary?.weekly_summary.critical_resolved}</span>
              </div>
            </div>
          </div>

          <div className="report-card glass">
            <h2>Monthly Fleet Trends</h2>
            <div className="report-stats">
              <div className="stat-line">
                <span className="stat-label">Projected Odometer (Avg)</span>
                <span className="stat-val">34,500 km</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">Monthly Alert Volume</span>
                <span className="stat-val warning">{summary?.monthly_summary.alerts_generated}</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">Preventative Swaps Completed</span>
                <span className="stat-val success">{summary?.monthly_summary.critical_resolved}</span>
              </div>
            </div>
          </div>

          <div className="report-card glass">
            <h2>Telemetry Average Baselines</h2>
            <div className="report-stats">
              <div className="stat-line">
                <span className="stat-label">Average Tyre Pressure</span>
                <span className="stat-val">{summary?.fleet_statistics.average_psi} PSI</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">Average Operating Temp</span>
                <span className="stat-val">{summary?.fleet_statistics.average_temperature} C</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">Average Tread Wear Depth</span>
                <span className="stat-val">{summary?.fleet_statistics.average_tread_depth} mm</span>
              </div>
            </div>
          </div>

          <div className="report-card glass">
            <h2>AI Model Reliability</h2>
            <div className="report-stats">
              <div className="stat-line">
                <span className="stat-label">ML Prediction Model</span>
                <span className="stat-val">RandomForest v1.2</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">F1 Classification Accuracy</span>
                <span className="stat-val success">{summary?.prediction_accuracy.accuracy_rate}%</span>
              </div>
              <div className="stat-line">
                <span className="stat-label">Prediction RUL Confidence</span>
                <span className="stat-val">96.8%</span>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default Reports;
