import '../css/Header.css';
import logo from '../img/logo.png';
import { Link } from 'react-router-dom'

function Header() {
  return (
    <header>
      <nav className="navigate">
        <div className='logotip'>
          <img src={logo} alt='logotip' className="logo" />
          <p className='name'>DeGenerateURL</p>
        </div>
        <ul className="list">
          <li><Link className="navi" to="/">Главная</Link></li>
          <li><Link className="navi" to="/history">История</Link>  </li>
          <li><Link className="navi" to="/statistic">Статистика</Link>  </li>
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