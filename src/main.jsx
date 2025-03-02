import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ApolloProvider } from '@apollo/client';
import apolloClient from '../src/lib/apolloClient.js';
import App from './App.jsx';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ApolloProvider client={apolloClient}>
      <BrowserRouter basename="/react-graphql">
        <App />
      </BrowserRouter>
    </ApolloProvider>
  </React.StrictMode>
);
