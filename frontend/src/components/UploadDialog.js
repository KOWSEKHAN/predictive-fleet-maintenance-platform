import React, { useState, useRef } from 'react';
import './UploadDialog.css';

const UploadDialog = ({ onClose, onSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileUpload(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      handleFileUpload(file);
    }
  };

  const handleFileUpload = async (file) => {
    if (!file.name.toLowerCase().endsWith('.csv')) {
      setError('Please select a valid CSV file');
      return;
    }

    setIsUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
      const response = await fetch(`${API_URL}/upload/`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        onSuccess(data.session_id, data.batch_count);
      } else {
        const errorData = await response.json();
        setError(errorData.error || 'Upload failed. Please try again.');
      }
    } catch (error) {
      setError('Network error. Please check your connection and try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="upload-overlay">
      <div className="upload-dialog">
        <div className="upload-header">
          <h2>Upload Tyre Data</h2>
          <button className="close-btn" onClick={onClose}>
            ✕
          </button>
        </div>
        
        <div className="upload-content">
          <div className="upload-instructions">
            <p>Upload a CSV file containing tyre data with the following columns:</p>
            <ul>
              <li><strong>tyre_id</strong> - Unique tyre identifier</li>
              <li><strong>psi</strong> - Tyre pressure in PSI</li>
              <li><strong>depth</strong> - Tread depth in mm</li>
              <li><strong>temp</strong> - Temperature in °C</li>
            </ul>
          </div>
          
          <div 
            className={`upload-area ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".csv"
              onChange={handleFileSelect}
              style={{ display: 'none' }}
            />
            
            <div className="upload-icon">📁</div>
            <p className="upload-text">
              {isDragging ? 'Drop your CSV file here' : 'Click to select or drag and drop a CSV file'}
            </p>
            <p className="upload-hint">Supports .csv files only</p>
          </div>
          
          {error && (
            <div className="upload-error">
              <span className="error-icon">⚠️</span>
              <span>{error}</span>
            </div>
          )}
          
          {isUploading && (
            <div className="upload-loading">
              <div className="loading-spinner"></div>
              <p>Uploading and processing data...</p>
            </div>
          )}
        </div>
        
        <div className="upload-footer">
          <button className="cancel-btn" onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
};

export default UploadDialog;
