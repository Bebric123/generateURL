import React from 'react'
import { Routes, Route } from 'react-router-dom'
import Header from './components/Header'
import Footer from './components/Footer'
import HomePage from './pages/HomePage'
import HistoryPage from './pages/HistoryPage.js'
import StatisticPage from './pages/StatisticPage.js'
import './css/index.css'

function App() {
  return (
    <div className="app-layout">
      <Header />
      <main className='centered-content'>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/statistic" element={<StatisticPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}

export default App