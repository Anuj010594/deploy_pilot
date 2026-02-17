import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ScanForm from './components/ScanForm';
import Results from './components/Results';
import Footer from './components/Footer';
import { healthCheck } from './services/api';
import './styles/App.css';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking');

  useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      await healthCheck();
      setBackendStatus('healthy');
    } catch (err) {
      setBackendStatus('error');
    }
  };

  const handleScanComplete = (data) => {
    setResults(data);
    setLoading(false);
    setError(null);
  };

  const handleScanError = (err) => {
    setError(err.message);
    setLoading(false);
    setResults(null);
  };

  const handleScanStart = () => {
    setLoading(true);
    setError(null);
    setResults(null);
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="app">
      <Header backendStatus={backendStatus} />
      
      <main className="main-content">
        <div className="container">
          <div className="hero-section">
            <h1 className="hero-title">
              Intelligent Project Detection
            </h1>
            <p className="hero-subtitle">
              Automatically detect programming languages, frameworks, and build tools from your repositories
            </p>
          </div>

          <div className="content-wrapper">
            <ScanForm 
              onScanStart={handleScanStart}
              onScanComplete={handleScanComplete}
              onScanError={handleScanError}
              loading={loading}
            />

            {error && (
              <div className="error-container">
                <div className="error-icon">⚠️</div>
                <div className="error-content">
                  <h3>Scan Failed</h3>
                  <p>{error}</p>
                </div>
              </div>
            )}

            {results && (
              <Results 
                data={results} 
                onReset={handleReset}
              />
            )}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

export default App;
