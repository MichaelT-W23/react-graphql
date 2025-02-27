import { useQuery, gql } from "@apollo/client";
import BookCard from "../components/BookCard";
import '../styles/views/Home.css';

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

const BooksList = () => {
  const { loading, error, data } = useQuery(GET_ALL_BOOKS);

  if (loading) return <p className="loading-text">Loading books...</p>;
  if (error) return <p className="error-text">Error loading books: {error.message}</p>;

  return (
    <div className="container">
      <h1 className="page-title">📚 Explore Our Books</h1>
      <ul className="book-list">
        {data.getAllBooks.map((book) => (
          <li key={book.id} className="book-list-item">
            <BookCard title={book.title} body={book} />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BooksList;