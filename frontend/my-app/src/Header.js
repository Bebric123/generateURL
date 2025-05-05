import './Header.css';
import logo from './img/logo.png';

function Header() {
  return (
    <header>
      <nav className="navigate">
        <img src={logo} alt='logotip' className="logo" />
        <p className='name'>DeGenerateURL</p>
        <ul className="list">
          <li>Главная</li>
          <li>Статистика</li>
          <li>История</li>
          <li>URL</li>
          <li>Кастомизация</li>
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