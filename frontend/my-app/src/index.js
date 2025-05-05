import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import Header from "./Header";

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <div className="app-layout">
      <Header />
      <main className="centered-content">
        <App />
      </main>
    </div>
  </React.StrictMode>
);