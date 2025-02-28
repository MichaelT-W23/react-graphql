import { Routes, Route } from 'react-router-dom';
import HomePage from '../views/Home';
import Authors from '../views/Authors';

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/authors" element={<Authors />} />
    </Routes>
  );
}