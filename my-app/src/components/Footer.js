import '../css/Footer.css';
import logo from '../img/logo.png';
import { Link } from 'react-router-dom'

function Footer() {
  return (
    <footer>
        <div className='border'></div>
        <p className="foo">2022 &#xA9 Все права защищены.</p>
    </footer>
  )
}

export default Footer;