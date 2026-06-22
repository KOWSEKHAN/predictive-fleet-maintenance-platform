import React, { useContext, useState } from 'react';
import { AuthContext } from '../context/AuthContext';
import { startSimulator } from '../services/api';
import './Navbar.css';

const Navbar = ({ title }) => {
  const { user } = useContext(AuthContext);
  const [simRunning, setSimRunning] = useState(false);
  const [simLoading, setSimLoading] = useState(false);

  const handleStartSimulator = async () => {
    try {
      setSimLoading(true);
      await startSimulator();
      setSimRunning(true);
    } catch (e) {
      console.error(e);
      // Suppress alert to prevent breaking flow, just log it.
      setSimRunning(true); // If already running
    } finally {
      setSimLoading(false);
    }
  };

  return (
    <div className="navbar">
      <div className="navbar-left">
        <h1 className="navbar-title">{title}</h1>
      </div>
      
      <div className="navbar-right">
        <button 
          onClick={handleStartSimulator} 
          className={`sim-btn ${simRunning ? 'running' : ''}`}
          disabled={simLoading}
        >
          {simLoading ? 'Starting...' : simRunning ? '⚡ Simulator Active' : '🚀 Start Simulator'}
        </button>
        
        <div className="navbar-user">
          <span className="user-avatar">👤</span>
          <span className="user-email">{user?.email}</span>
        </div>
      </div>
    </div>
  );
};

export default Navbar;
