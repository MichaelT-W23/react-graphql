import { Routes, Route } from 'react-router-dom';
import HomePage from '../views/Home';
import SecondPage from '../views/SecondPage';

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/second-page" element={<SecondPage />} />
    </Routes>
  );
}