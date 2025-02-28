import { useState, useEffect } from "react";
import { gql, useQuery, useLazyQuery } from "@apollo/client";
import BookCard from "../components/BookCard";

const GET_ALL_GENRES = gql`
  query {
    getAllGenres
  }
`;

const GET_BOOKS_BY_GENRE = gql`
  query GetBooksByGenre($genre: String!) {
    getBooksByGenre(genre: $genre) {
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

export default function Genres() {
  const { data: genreData, refetch: refetchGenres } = useQuery(GET_ALL_GENRES);
  const { data: allBooksData, loading, error, refetch: refetchAllBooks } = useQuery(GET_ALL_BOOKS);

  const [selectedGenre, setSelectedGenre] = useState("All");

  const [fetchBooksByGenre, { data: genreBooksData, loading: genreLoading, error: genreError }] =
    useLazyQuery(GET_BOOKS_BY_GENRE);

  useEffect(() => {
    refetchGenres();
    refetchAllBooks();
  }, [refetchGenres, refetchAllBooks]);

  useEffect(() => {
    if (selectedGenre === "All") {
      refetchAllBooks();
    } else {
      fetchBooksByGenre({ variables: { genre: selectedGenre } });
    }
  }, [selectedGenre, refetchAllBooks, fetchBooksByGenre]);

  const genres = genreData?.getAllGenres || [];
  const books = selectedGenre === "All" ? allBooksData?.getAllBooks || [] : genreBooksData?.getBooksByGenre || [];

  return (
    <div className="flex flex-col items-center w-full max-w-3xl mx-auto py-8 px-4">
      <h1 className="text-3xl font-bold text-center mb-2 relative">
        🧙🏻‍♂️ Genres - {selectedGenre}
      </h1>
      <span className="block w-96 h-1 bg-red-400 mx-auto rounded-md mb-6"></span>
      <div className="w-full max-w-xs mb-6">
        <label htmlFor="genre-select" className="block text-lg font-semibold mb-2">
          Select Genre:
        </label>
        <select
          id="genre-select"
          className="w-full p-2 border border-gray-300 rounded-md"
          value={selectedGenre}
          onChange={(e) => setSelectedGenre(e.target.value)}
        >
          <option value="All">All</option>
          {genres.map((genre) => (
            <option key={genre} value={genre}>
              {genre}
            </option>
          ))}
        </select>
      </div>
      {(loading || genreLoading) && <p className="text-gray-600">Loading books...</p>}
      {(error || genreError) && <p className="text-red-500">Error loading books.</p>}
      {books.length > 0 ? (
        <ul className="w-full flex flex-col items-center space-y-4 px-4">
          {books.map((book) => (
            <li key={book.id} className="w-full max-w-md flex justify-center">
              <BookCard title={book.title} body={book} />
            </li>
          ))}
        </ul>
      ) : (
        !loading && !genreLoading && <p className="text-gray-700">No books available.</p>
      )}
    </div>
  );
}
