import React, { useEffect, useState, useCallback } from 'react';
import Navbar from '../components/Navbar';
import { fetchSummary, fetchDashboardChartData } from '../services/api';
import {
  PieChart, Pie, Cell,
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
} from 'recharts';
import './Dashboard.css';

// Condition colours — memoised outside component to avoid re-allocation
const CONDITION_COLORS = { Good: '#10b981', Average: '#f59e0b', Bad: '#ef4444' };

const Dashboard = () => {
  const [summary,  setSummary]  = useState(null);
  const [chartData, setChartData] = useState({ pie_data: [], bar_data: [] });
  const [loading,  setLoading]  = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [summaryData, charts] = await Promise.all([
        fetchSummary(),
        fetchDashboardChartData(),   // aggregated — no longer fetches 300 predictions
      ]);
      setSummary(summaryData);
      setChartData(charts);
    } catch (e) {
      console.error('Dashboard failed to retrieve live logs', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    // Reduced from 5 000 ms → 30 000 ms (6× less server load)
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, [loadData]);

  // Transform server pie_data into Recharts format
  const pieData = chartData.pie_data
    .filter(d => d.count > 0)
    .map(d => ({
      name:  d.condition,
      value: d.count,
      color: CONDITION_COLORS[d.condition] || '#94a3b8',
    }));

  const barData = chartData.bar_data; // already { name, km } from server

  if (loading && !summary) {
    return <div className="page-loading">Loading Dashboard analytics...</div>;
  }

  return (
    <div className="main-content">
      <Navbar title="Dashboard Overview" />
      <div className="dashboard-content">

        <div className="kpi-grid">
          <div className="kpi-card glass highlight">
            <span className="kpi-icon">❤️</span>
            <div className="kpi-info">
              <h3>Fleet Health Score</h3>
              <p className="kpi-val">{summary?.fleet_health_score}%</p>
            </div>
          </div>

          <div className="kpi-card glass">
            <span className="kpi-icon">🚛</span>
            <div className="kpi-info">
              <h3>Total Vehicles</h3>
              <p className="kpi-val">{summary?.total_vehicles}</p>
            </div>
          </div>

          <div className="kpi-card glass text-success">
            <span className="kpi-icon">🟢</span>
            <div className="kpi-info">
              <h3>Healthy</h3>
              <p className="kpi-val">{summary?.healthy_vehicles}</p>
            </div>
          </div>

          <div className="kpi-card glass text-warning">
            <span className="kpi-icon">🟡</span>
            <div className="kpi-info">
              <h3>Warning</h3>
              <p className="kpi-val">{summary?.warning_vehicles}</p>
            </div>
          </div>

          <div className="kpi-card glass text-danger">
            <span className="kpi-icon">🔴</span>
            <div className="kpi-info">
              <h3>Critical</h3>
              <p className="kpi-val">{summary?.critical_vehicles}</p>
            </div>
          </div>
        </div>

        <div className="charts-grid">
          <div className="chart-card glass">
            <h3>Condition Distribution</h3>
            <div className="chart-wrapper">
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%" cy="50%"
                      innerRadius={60} outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="chart-empty">No telemetry data. Start simulator to gather logs.</div>
              )}
            </div>
          </div>

          <div className="chart-card glass">
            <h3>Lowest Remaining Life (KM)</h3>
            <div className="chart-wrapper">
              {barData.length > 0 ? (
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={barData}>
                    <XAxis dataKey="name" stroke="rgba(255,255,255,0.6)" fontSize={11} />
                    <YAxis stroke="rgba(255,255,255,0.6)" fontSize={11} />
                    <Tooltip />
                    <Bar dataKey="km" fill="#a855f7" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="chart-empty">No lifecycle data. Start simulator to gather logs.</div>
              )}
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
