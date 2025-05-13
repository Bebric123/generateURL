import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../css/App.css';

function HomePage() {
    const [longUrl, setLongUrl] = useState('');
    const [shortUrl, setShortUrl] = useState('');
    const [email, setEmail] = useState('');
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [userLinks, setUserLinks] = useState([]);
    const [error, setError] = useState(''); 
  
    useEffect(() => {
      const savedEmail = localStorage.getItem('email');
      if (savedEmail) {
        setEmail(savedEmail);
        setIsLoggedIn(true);
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
  
    const handleLogin = (e) => {
      e.preventDefault();
      if (!email) {
        setError('Пожалуйста, введите email');
        return;
      }
      localStorage.setItem('email', email);
      setIsLoggedIn(true);
      fetchUserLinks(email);
      setError('');
    };
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      
      if (!isLoggedIn) {
        setError('Сначала войдите в систему');
        return;
      }
      
      if (!longUrl.trim()) {
        setError('Пожалуйста, введите ссылку для сокращения');
        return;
      }
      
      if (!longUrl.startsWith('http://') && !longUrl.startsWith('https://')) {
        setError('Ссылка должна начинаться с http:// или https://');
        return;
      }
      
      try {
        setError(''); 
        const response = await axios.post(
          'http://localhost:8000/shorten',
          { 
            long_url: longUrl,
            email: email
          }
        );
        setShortUrl(response.data.short_url);
        fetchUserLinks(email);
      } catch (error) {
        console.error('Error:', error.response?.data);
        setError('Ошибка при создании короткой ссылки');
      }
    };
  
    return (
      <div className="container">
        {!isLoggedIn ? (
          <div className="form">
            <form onSubmit={handleLogin}>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Ваш email"
                required
              />
              <button className="btn_gen" type="submit">Войти</button>
              {error && <div className="error-message">{error}</div>}
            </form>
          </div>
        ) : (
          <div className="container">
            <div className="form">
              <form onSubmit={handleSubmit}>
                <input 
                  type="text" 
                  value={longUrl} 
                  onChange={(e) => setLongUrl(e.target.value)} 
                  placeholder="Введите URL (начинается с http://)"
                />
                <input 
                  type="text" 
                  value={shortUrl} 
                  readOnly
                  placeholder="Здесь появится короткая ссылка"
                />
                <button className="btn_gen" type="submit">Скоротать</button>
                {error && <div className="error-message">{error}</div>}
              </form>
            </div>
          </div>
        )}
      </div>
    );
}

export default HomePage;