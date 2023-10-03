import { useState, useRef } from 'react';
import { Routes, Route } from 'react-router-dom';
import { SnackbarProvider } from 'notistack';
import { SnackbarUtilsConfigurator } from './components/Snackbar';
import './App.scss'
import Login from './components/Login';
import Home from './components/Home';

function App() {

  const websocketRef = useRef(null);

  const [username, setUsername] = useState("");

  return (
    <div className='App'>
      <Routes>
        <Route path='/' element={<Login username={username} setUsername={setUsername} websocketRef={websocketRef} />} />
        <Route path='home' element={<Home username={username} websocketRef={websocketRef} />} />
      </Routes>
      <SnackbarProvider
        maxStack={3}
      >
        <SnackbarUtilsConfigurator />
      </SnackbarProvider>
    </div>
  );
}

export default App;
