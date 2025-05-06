import React, { useState, useEffect } from 'react';
import axios from 'axios';

function HistoryPage() {
  const [userLinks, setUserLinks] = useState([]);
  const [email, setEmail] = useState('');

  useEffect(() => {
    const savedEmail = localStorage.getItem('email');
    if (savedEmail) {
      setEmail(savedEmail);
      fetchUserLinks(savedEmail);
    }
  }, []);

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

  return (
    <div className="history-container">
      <h1>История ваших ссылок</h1>
      
      <div className="links-list">
        {userLinks.length > 0 ? (
          userLinks.map((link, index) => (
            <div key={index} className="link-item">
              <p>Оригинал: {link.long_url}</p>
              <p>
                Сокращенная:{' '}
                <a href={link.short_url} target="_blank" rel="noopener noreferrer">
                  {link.short_url}
                </a>
              </p>
              <small>Создано: {new Date(link.created_at).toLocaleString()}</small>
            </div>
          ))
        ) : (
          <p>У вас пока нет сохраненных ссылок</p>
        )}
      </div>
    </div>
  );
}

export default HistoryPage;