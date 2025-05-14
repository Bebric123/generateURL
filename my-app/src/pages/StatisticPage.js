import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import '../css/Stati.css';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

function StatisticPage() {
  const [links, setLinks] = useState([]);
  const [selectedLink, setSelectedLink] = useState('');
  const [period, setPeriod] = useState('day');
  const [stats, setStats] = useState(null);
  const [email, setEmail] = useState('');

  useEffect(() => {
    const savedEmail = localStorage.getItem('email');
    if (savedEmail) {
      setEmail(savedEmail);
      fetchUserLinks(savedEmail);
    }
  }, []);

  useEffect(() => {
    if (selectedLink) {
      fetchLinkStats();
    }
  }, [selectedLink, period]);

  const fetchUserLinks = async (userEmail) => {
    try {
      const response = await axios.post(
        'http://localhost:8000/user/links',
        { email: userEmail }
      );
      setLinks(response.data.links);
    } catch (error) {
      console.error('Error fetching links:', error);
    }
  };

  const fetchLinkStats = async () => {
    try {
      const response = await axios.post(
        'http://localhost:8000/stats/clicks',
        {
          email: email,
          short_url: selectedLink,
          period: period
        }
      );
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error.response?.data || error.message);
    }
};

const prepareChartData = () => {
    if (!stats) return null;
    const sortedEntries = Object.entries(stats)
      .sort(([dateA], [dateB]) => new Date(dateA) - new Date(dateB));
    
    const labels = sortedEntries.map(([date]) => 
      period === 'day' 
        ? new Date(date).toLocaleDateString() 
        : new Date(date + '-01').toLocaleDateString('ru', { month: 'long', year: 'numeric' })
    );
    
    const data = sortedEntries.map(([_, count]) => count);
    
    return {
      labels,
      datasets: [
        {
          label: 'Количество переходов',
          data,
          borderColor: 'rgb(95, 75, 192)',
          backgroundColor: 'rgba(93, 75, 192, 0.5)',
          tension: 0.1
        }
      ]
    };
};

  const chartData = prepareChartData();

  return (
    <div className="statistic-container">
      <h1>Статистика переходов</h1>
      
      <div className="controls">
        <select 
          value={selectedLink}
          onChange={(e) => setSelectedLink(e.target.value)}
          className="link-selector"
        >
          <option value="">Выберите ссылку</option>
          {links.map((link, index) => (
            <option key={index} value={link.short_url}>
              {link.short_url} ({link.is_active ? 'активна' : 'неактивна'})
            </option>
          ))}
        </select>
        
        <select
          value={period}
          onChange={(e) => setPeriod(e.target.value)}
          className="period-selector"
        >
          <option value="day">По дням</option>
          <option value="month">По месяцам</option>
        </select>
      </div>
      
      {chartData && (
        <div className="chart-container">
          <Line 
            data={chartData} 
            options={{
              responsive: true,
              plugins: {
                title: {
                  display: true,
                  text: `Статистика переходов (${period === 'day' ? 'по дням' : 'по месяцам'})`
                },
              },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: {
                    stepSize: 1
                  }
                }
              }
            }}
          />
        </div>
      )}
    </div>
  );
}

export default StatisticPage;