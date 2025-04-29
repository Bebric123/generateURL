import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [longUrl, setLongUrl] = useState('');
  const [shortUrl, setShortUrl] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(
        'http://localhost:8000/shorten',
        { long_url: longUrl }, 
        {
          headers: {
            'Content-Type': 'application/json',  
          },
        }
      );
      setShortUrl(response.data.short_url);
    } catch (error) {
      console.error('Ошибка при запросе:', error.response?.data);
    }
  };

  return (
    <div class="form">
      <h1>Генерация короткой ссылки</h1>
      <div class="generate">
        <form onSubmit={handleSubmit}>
          <input type="text" value={longUrl} onChange={(e) => setLongUrl(e.target.value)} placeholder="Enter long URL"/>
          <button type="submit">Скоротать</button>
        </form>
        {shortUrl && (
          <div>
             <a href={shortUrl} target="_blank" rel="noopener noreferrer">
               {shortUrl}
             </a>
           </div>
        )}
      </div>
    </div>
  );
}

export default App;