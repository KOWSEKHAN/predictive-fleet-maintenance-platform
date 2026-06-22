import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import TyreCard from '../components/TyreCard';
import { fetchVehicleDetails, fetchVehiclePredictions } from '../services/api';
import './VehicleDetails.css';

const VehicleDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [vehicle, setVehicle] = useState(null);
  const [tyres, setTyres] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    try {
      const vehicleData = await fetchVehicleDetails(id);
      setVehicle(vehicleData);
      
      const tyreData = await fetchVehiclePredictions(id);
      setTyres(tyreData);
    } catch (e) {
      console.error("VehicleDetails failed to load tyres metadata", e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Reduced from 5 000 ms → 30 000 ms
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  if (loading && !vehicle) {
    return <div className="page-loading">Loading vehicle telemetry...</div>;
  }

  if (!vehicle) {
    return (
      <div className="main-content">
        <Navbar title="Vehicle Not Found" />
        <div className="error-content">
          <p>The requested vehicle could not be found or you do not have permission to view it.</p>
          <button onClick={() => navigate('/fleet')} className="back-btn">Back to Fleet</button>
        </div>
      </div>
    );
  }

  return (
    <div className="main-content">
      <Navbar title={`Vehicle Profile: ${vehicle.vehicle_number}`} />
      <div className="details-content">
        
        <button onClick={() => navigate('/fleet')} className="back-btn">
          &larr; Back to Fleet
        </button>

        <div className="vehicle-header glass">
          <div className="meta-item">
            <span className="meta-label">Vehicle Type</span>
            <span className="meta-value">{vehicle.vehicle_type}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Driver Assigned</span>
            <span className="meta-value">{vehicle.driver_name}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Route</span>
            <span className="meta-value">{vehicle.route}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Status</span>
            <span className={`status-badge ${vehicle.status.toLowerCase()}`}>
              {vehicle.status}
            </span>
          </div>
        </div>

        <div className="tyres-section">
          <h2>Tyre Status &amp; AI Forecasts</h2>
          <div className="tyres-grid">
            {tyres.length > 0 ? (
              tyres.map(tyre => (
                <TyreCard key={tyre.id} tyre={tyre} />
              ))
            ) : (
              <div className="no-tyres glass">
                No telemetry recorded for this vehicle. Ensure the simulator is active.
              </div>
            )}
          </div>
        </div>

      </div>
    </div>
  );
};

export default VehicleDetails;
