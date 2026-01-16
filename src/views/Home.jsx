import { useQuery, gql } from "@apollo/client";
import { useEffect } from "react";
import BookCard from "../components/BookCard";
import styles from '../styles/views/Home.module.css';

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
  const { loading, error, data, refetch } = useQuery(GET_ALL_BOOKS);

  useEffect(() => {
    refetch();
  }, [refetch]);

  if (loading) return <p className={styles['loading-text']}>Loading books...</p>;
  if (error) return <p className={styles.errorText}>Error loading books: {error.message}</p>;

  return (
    <div className={styles.container}>
      <h1 className={styles['page-title']}>📚 Explore Our Books2</h1>
      <ul className={styles['book-list']}>
        {data?.getAllBooks.map((book) => (
          <li key={book.id} className={styles['book-list-item']}>
            <BookCard title={book.title} body={book} />
          </li>
        ))}
      </ul>
    </div>
  );
};

export default BooksList;
