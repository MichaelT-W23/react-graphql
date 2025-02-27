import { useEffect, useState } from 'react';
import "../styles/components/SearchView.css";
import booksData from './DELETETHIS.json';

const SearchView = () => {
  const [books, setBooks] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    setBooks(booksData.getAllBooks);
  }, []);

  const filteredBooks = books.filter((book) => 
    book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    book.author.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="search-view">
      <div className="search-section">
        <div className="search-header">
          <p>Search</p>
        </div>

        {/* Search Input Wrapper */}
        <div className="search-input-container">
          <span className="material-symbols-outlined search-icon">search</span>
          <input 
            type="text" 
            placeholder="Search by title or author..." 
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      <div className="book-list">
        {filteredBooks.map((book) => (
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
