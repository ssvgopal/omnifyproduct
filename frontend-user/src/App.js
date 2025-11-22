import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import UserRoutes from './routes/UserRoutes';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <UserRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;

