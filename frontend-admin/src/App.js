import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import AdminRoutes from './routes/AdminRoutes';
import AdminLayout from './components/layout/AdminLayout';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <AdminLayout>
          <AdminRoutes />
        </AdminLayout>
      </div>
    </BrowserRouter>
  );
}

export default App;

