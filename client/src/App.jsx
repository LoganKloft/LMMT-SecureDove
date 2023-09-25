import { useRef } from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.scss'
import Login from './components/Login';
import Home from './components/Home';

function App() {

  const websocketRef = useRef(null);

  return (
    <div className='App'>
      <Routes>
        <Route path='/' element={<Login websocketRef={websocketRef} />} />
        <Route path='home' element={<Home websocketRef={websocketRef} />} />
      </Routes>
    </div>
  );
}

export default App;
