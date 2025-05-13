import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/History.css';

function HistoryPage() {
  const [userLinks, setUserLinks] = useState([]);
  const [sortedLinks, setSortedLinks] = useState([]);
  const [email, setEmail] = useState('');
  const [sortOrder, setSortOrder] = useState('desc');
  const [activeOnly, setActiveOnly] = useState(false);
  const [copiedLink, setCopiedLink] = useState(null);

  useEffect(() => {
    const savedEmail = localStorage.getItem('email');
    if (savedEmail) {
      setEmail(savedEmail);
      fetchUserLinks(savedEmail);
    }
  }, []);

  useEffect(() => {
    let filteredLinks = [...userLinks];
    
    if (activeOnly) {
      filteredLinks = filteredLinks.filter(link => link.is_active !== false);
    }
    
    const sorted = filteredLinks.sort((a, b) => {
      const dateA = new Date(a.created_at);
      const dateB = new Date(b.created_at);
      return sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
    });
    
    setSortedLinks(sorted);
  }, [userLinks, sortOrder, activeOnly]);

  const fetchUserLinks = async (userEmail) => {
    try {
      const response = await axios.post(
        'http://localhost:8000/user/links',
        { email: userEmail }
      );
      setUserLinks(response.data.links);
    } catch (error) {
      console.error('Error fetching links:', error);
    }
  };

  const toggleSortOrder = () => {
    setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc');
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setCopiedLink(text);
    setTimeout(() => setCopiedLink(null), 2000);
  };

  const refreshLinks = () => {
    fetchUserLinks(email);
  };

  return (
    <div className="history-container">
      <h1>История ваших ссылок</h1>
      
      <div className="table-container">
        <table className="links-table">
          <thead>
            <tr>
              <th>№</th>
              <th>Оригинальная ссылка</th>
              <th>Сокращенная ссылка</th>
              <th onClick={toggleSortOrder} className="sortable-header">
                Дата создания {sortOrder === 'asc' ? '↑' : '↓'}
              </th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            {sortedLinks.length > 0 ? (
              sortedLinks.map((link, index) => (
                <tr key={index} className={!link.is_active ? 'inactive-link' : ''}>
                  <td>{index + 1}</td>
                  <td className="long-url-cell">
                    <a href={link.long_url} target="_blank" rel="noopener noreferrer">
                      {link.long_url}
                    </a>
                  </td>
                  <td>
                    <a href={link.short_url} target="_blank" rel="noopener noreferrer">
                      {link.short_url}
                    </a>
                  </td>
                  <td>{new Date(link.created_at).toLocaleString()}</td>
                  <td>
                    <span className={`status-badge ${link.is_active ? 'active' : 'inactive'}`}>
                      {link.is_active ? 'Активна' : 'Неактивна'}
                    </span>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="6" className="no-links-message">
                  {activeOnly ? 'Нет активных ссылок' : 'У вас пока нет сохраненных ссылок'}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default HistoryPage;