import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { fetchVehicles } from '../services/api';
import './FleetOverview.css';

const FleetOverview = () => {
  const [vehicles, setVehicles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterStatus, setFilterStatus] = useState('All');
  const [sortBy, setSortBy] = useState('vehicle_number');
  const navigate = useNavigate();

  const loadData = async () => {
    try {
      const data = await fetchVehicles(1);
      // Handle paginated response: { count, next, previous, results }
      setVehicles(Array.isArray(data) ? data : (data.results || []));
    } catch (e) {
      console.error('FleetOverview failed to load vehicles list', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Reduced from 5 000 ms → 30 000 ms
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const filteredVehicles = vehicles
    .filter(v => {
      const matchesSearch = v.vehicle_number.toLowerCase().includes(search.toLowerCase()) ||
                            v.driver_name.toLowerCase().includes(search.toLowerCase());
      const matchesStatus = filterStatus === 'All' || v.status === filterStatus;
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      if (sortBy === 'vehicle_number') {
        return a.vehicle_number.localeCompare(b.vehicle_number);
      } else if (sortBy === 'status') {
        return a.status.localeCompare(b.status);
      }
      return 0;
    });

  if (loading && vehicles.length === 0) {
    return <div className="page-loading">Loading fleet inventory...</div>;
  }

  return (
    <div className="main-content">
      <Navbar title="Fleet Inventory" />
      <div className="fleet-content">
        
        <div className="controls-row glass">
          <input 
            type="text" 
            placeholder="Search vehicle or driver..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
          />
          
          <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)} className="filter-select">
            <option value="All">All Statuses</option>
            <option value="Healthy">Healthy</option>
            <option value="Warning">Warning</option>
            <option value="Critical">Critical</option>
          </select>

          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="sort-select">
            <option value="vehicle_number">Sort by Vehicle ID</option>
            <option value="status">Sort by Status</option>
          </select>
        </div>

        <div className="table-wrapper glass">
          <table className="fleet-table">
            <thead>
              <tr>
                <th>Vehicle Number</th>
                <th>Type</th>
                <th>Driver Name</th>
                <th>Assigned Route</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredVehicles.length > 0 ? (
                filteredVehicles.map(vehicle => (
                  <tr 
                    key={vehicle.id} 
                    onClick={() => navigate(`/vehicle/${vehicle.id}`)}
                    className="clickable-row"
                  >
                    <td><strong>{vehicle.vehicle_number}</strong></td>
                    <td>{vehicle.vehicle_type}</td>
                    <td>{vehicle.driver_name}</td>
                    <td>{vehicle.route}</td>
                    <td>
                      <span className={`status-badge ${vehicle.status.toLowerCase()}`}>
                        {vehicle.status}
                      </span>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" className="empty-table">No vehicles match filters. Trigger simulator above to generate vehicles.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
};

export default FleetOverview;
