import { useQuery, gql } from "@apollo/client";
import BookCard from "../components/BookCard";

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

export default function BooksList() {
  const { data, loading, error } = useQuery(GET_ALL_BOOKS);
  const books = data?.getAllBooks || [];

  return (
    <div className="flex flex-col items-center px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-800 text-center relative">
        📚 Explore Our Books
        <span className="block w-80 h-1 bg-red-500 mt-2 mx-auto rounded"></span>
      </h1>
      
      {loading && <p className="text-gray-500 text-lg">Loading books...</p>}
      {error && <p className="text-red-500 text-lg">Error loading books: {error.message}</p>}
      
      {books.length > 0 && (
        <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mt-6 w-full max-w-5xl">
          {books.map((book) => (
            <li key={book.id} className="flex justify-center">
              <BookCard title={book.title} body={book} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
