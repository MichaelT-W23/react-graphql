import { useEffect, useState, useRef } from "react";
import "../styles/components/SearchView.css";
import booksData from "./DELETETHIS.json";

const SearchView = () => {
  const [books, setBooks] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const searchInputRef = useRef(null);

  useEffect(() => {
    setBooks(booksData.getAllBooks);
  }, []);

  const filteredBooks = books.filter(
    (book) =>
      book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      book.author.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const clearSearch = () => {
    setSearchTerm("");
    setIsFocused(false);
    searchInputRef.current?.blur();
  };

  return (
    <div className="search-view">
      <div className="search-section">
        <div className="search-header">
          <p>Search</p>
        </div>

        <div className="search-input-container">
          {!isFocused && (
            <span className="material-symbols-outlined search-icon">search</span>
          )}
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search by title or author..."
            className="search-input"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => searchTerm === "" && setIsFocused(false)}
          />
          {isFocused && (
            <span
              className="material-symbols-outlined cancel-icon"
              onClick={clearSearch}
            >
              cancel
            </span>
          )}
        </div>
      </div>

      <div className="book-list">
        {filteredBooks.length > 0 ? (
          filteredBooks.map((book) => (
            <div key={book.id} className="book-item">
              <h3>{book.title}</h3>
              <p>Author: {book.author.name}</p>
              <p>Publication Year: {book.publicationYear}</p>
              <p>Genre: {book.genre}</p>
            </div>
          ))
        ) : (
          <p className="no-results">No books found for &quot;{searchTerm}&quot;</p>
        )}
      </div>
    </div>
  );
};

export default SearchView;
