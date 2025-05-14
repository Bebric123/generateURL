import '../css/Header.css';
import logo from '../img/logo.png';
import { Link } from 'react-router-dom'
import { useEffect, useState } from 'react';

function Header() {
  const [combinationsData, setCombinationsData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCombinations = async () => {
      try {
        const response = await fetch('http://localhost:8000/available-combinations');
        const count = await response.json();
        setCombinationsData(count);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };
    fetchCombinations();
  }, []);

  return (
    <header>
      <nav className="navigate">
        <div className='logotip'>
          <img src={logo} alt='logotip' className="logo" />
          <p className='name'>GenerateURL</p>
        </div>
        <ul className="list">
          <li><Link className="navi" to="/">Главная</Link></li>
          <li><Link className="navi" to="/history">История</Link>  </li>
          <li><Link className="navi" to="/statistic">Статистика</Link>  </li>
        </ul>
        
        <div className='btn-nav'>
          {isLoading ? (
            <div>Загрузка данных...</div>
          ) : error ? (
            <div>Ошибка: {error}</div>
          ) : combinationsData ? (
            <div className="combinations-info">
              <span>Доступно комбинаций: {combinationsData}</span>
            </div>
          ) : null}
          <button className="btn-header">Поддержка</button>
          <button className="btn-header">Контакты</button>
        </div>
      </nav>
    </header>
  );
}

export default Header;