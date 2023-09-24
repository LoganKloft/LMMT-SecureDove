import './App.scss'
import { Routes, Route } from 'react-router-dom'
import Login from './components/Login';
import Home from './components/Home';

function App() {

  return (
    <div className='App'>
      <Routes>
        <Route path='/' element={<Login />} />
        <Route path='home' element={<Home />} />
      </Routes>
    </div>
  );
}

export default App;
