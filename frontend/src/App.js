import React, { useContext } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, AuthContext } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import FleetOverview from './pages/FleetOverview';
import VehicleDetails from './pages/VehicleDetails';
import Predictions from './pages/Predictions';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';
import './App.css';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useContext(AuthContext);

  if (loading) {
    return <div className="page-loading">Restoring user session...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="page-container">
        {children}
      </div>
    </div>
  );
};

function AppContent() {
  return (
    <Routes>
      {/* Auth Routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected Routes */}
      <Route 
        path="/dashboard" 
        element={
          <ProtectedRoute>
            <Dashboard />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/fleet" 
        element={
          <ProtectedRoute>
            <FleetOverview />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/vehicle/:id" 
        element={
          <ProtectedRoute>
            <VehicleDetails />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/predictions" 
        element={
          <ProtectedRoute>
            <Predictions />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/alerts" 
        element={
          <ProtectedRoute>
            <Alerts />
          </ProtectedRoute>
        } 
      />
      <Route 
        path="/reports" 
        element={
          <ProtectedRoute>
            <Reports />
          </ProtectedRoute>
        } 
      />

      {/* Fallback Redirects */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <AppContent />
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
