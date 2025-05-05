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
    <div className="container">
      <div className="form">
        <form onSubmit={handleSubmit}>
          <input type="text" value={longUrl} onChange={(e) => setLongUrl(e.target.value)} placeholder="Введите вашу ссылочку"/>
          <input type="text" value={shortUrl} onChange={(e) => setLongUrl(e.target.value)} placeholder="Ваша короткая ссылочка"/>
          <button className="btn_gen" type="submit">Скоротать</button>
        </form>
      </div>
    </div>
  );
}

export default App;