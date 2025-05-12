import '../css/Header.css';
import logo from '../img/logo.png';
import { Link } from 'react-router-dom'

function Header() {
  return (
    <header>
      <nav className="navigate">
        <img src={logo} alt='logotip' className="logo" />
        <p className='name'>DeGenerateURL</p>
        <ul className="list">
          <li><Link class="navi" to="/">Главная</Link></li>
          <li><Link class="navi" to="/history">История</Link>  </li>
          <li><Link class="navi" to="/statistic">Статистика</Link>  </li>
          <li><Link class="navi" to="/statistic">Кастомизация</Link>  </li>
        </ul>
        
        <div className='btn-nav'>
          <button className="btn-header">Поддержка</button>
          <button className="btn-header">Контакты</button>
        </div>
      </nav>
    </header>
  );
}

export default Header;