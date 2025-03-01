import { useEffect, useState, useRef } from "react";
import { gql, useQuery } from "@apollo/client";
import PropTypes from "prop-types";
import styles from "../styles/components/SearchView.module.css";

const GET_ALL_BOOKS = gql`
  query {
    getAllBooks {
      id
      title
      publicationYear
      genre
      author {
        name
      }
    }
  }
`;

const SearchView = ({ onClose }) => {
  const { loading, error, data, refetch } = useQuery(GET_ALL_BOOKS, {
    fetchPolicy: "network-only",
  });

  const [books, setBooks] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [isFocused, setIsFocused] = useState(false);
  const searchInputRef = useRef(null);
  const searchContainerRef = useRef(null);

  useEffect(() => {
    if (refetch) {
      refetch();
    }
  }, [refetch]);

  useEffect(() => {
    if (data) {
      setBooks(data.getAllBooks);
    }
  }, [data]);

  const filteredBooks = books.filter(
    (book) =>
      book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      book.author.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const clearSearch = () => {
    setSearchTerm("");
    setIsFocused(false);
    searchInputRef.current?.blur();
    onClose();
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        onClose(); 
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [onClose]);

  if (loading) return <p>Loading books...</p>;
  if (error) return <p>Error loading books: {error.message}</p>;

  return (
    <div ref={searchContainerRef} className={styles['search-view']}>
      <div className={styles['search-section']}>
        <div className={styles['search-header']}>
          <p>Search</p>
          <span 
            className={`material-symbols-outlined ${styles['search-close-icon']}`}
            onClick={onClose}
          >
            close
          </span>
        </div>

        <div className={styles['search-input-container']}>
          {!isFocused && (
            <span className={`material-symbols-outlined ${styles['search-icon']}`}>search</span>
          )}
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search by title or author..."
            className={styles['search-input']}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onFocus={() => setIsFocused(true)}
            onBlur={() => searchTerm === "" && setIsFocused(false)}
          />
          {isFocused && (
            <span
              className={`material-symbols-outlined ${styles['cancel-icon']}`}
              onClick={clearSearch}
            >
              cancel
            </span>
          )}
        </div>
      </div>

      <div className={styles['book-list']}>
        {filteredBooks.length > 0 ? (
          filteredBooks.map((book) => (
            <div key={book.id} className={styles['book-item']}>
              <h3>{book.title}</h3>
              <p>Author: {book.author.name}</p>
              <p>Publication Year: {book.publicationYear}</p>
              <p>Genre: {book.genre}</p>
            </div>
          ))
        ) : (
          <p className={styles['no-results']}>No books found for &quot;{searchTerm}&quot;</p>
        )}
      </div>
    </div>
  );
};

SearchView.propTypes = {
  onClose: PropTypes.func.isRequired
};

export default SearchView;
