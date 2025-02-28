import { Routes, Route } from 'react-router-dom';
import HomePage from '../views/Home';
import Authors from '../views/Authors';
import Genres from '../views/Genres';
import AddBook from '../views/AddBook';
import AddAuthor from '../views/AddAuthor';

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/authors" element={<Authors />} />
      <Route path="/genres" element={<Genres />} />
      <Route path="/add-book" element={<AddBook />} />
      <Route path="/add-author" element={<AddAuthor />} />
    </Routes>
  );
}