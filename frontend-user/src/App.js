import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import UserRoutes from './routes/UserRoutes';
import Layout from './components/layout/Layout';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Layout>
          <UserRoutes />
        </Layout>
      </div>
    </BrowserRouter>
  );
}

export default App;

