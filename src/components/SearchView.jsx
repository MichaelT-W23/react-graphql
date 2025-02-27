import { useEffect, useState } from 'react';
import "../styles/components/SearchView.css";
import booksData from './DELETETHIS.json';

const SearchView = () => {
  const [books, setBooks] = useState([]);

  useEffect(() => {
    setBooks(booksData.getAllBooks);
  }, []);

  return (
    <div className="search-view">
      <input type="text" placeholder="Search..." className="search-input" />
      <div className="book-list">
        {books.map((book) => (
          <div key={book.id} className="book-item">
            <h3>{book.title}</h3>
            <p>Author: {book.author.name}</p>
            <p>Publication Year: {book.publicationYear}</p>
            <p>Genre: {book.genre}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SearchView;
