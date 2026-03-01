import { useState, useEffect } from "react";
import { gql, useQuery, useMutation } from "@apollo/client";

const GET_ALL_AUTHORS = gql`
  query GetAllAuthors {
    getAllAuthors {
      uuid
      name
    }
  }
`;

const GET_ALL_GENRES = gql`
  query GetAllGenres {
    getAllGenres
  }
`;

const CREATE_BOOK = gql`
  mutation CreateBook(
    $title: String!,
    $publicationYear: Int!,
    $genre: String!,
    $authorUuid: String!
  ) {
    createBook(
      title: $title,
      publicationYear: $publicationYear,
      genre: $genre,
      authorUuid: $authorUuid
    ) {
      uuid
      title
    }
  }
`;

export default function AddBook() {
  const [title, setTitle] = useState("");
  const [publicationYear, setPublicationYear] = useState("");
  const [selectedGenre, setSelectedGenre] = useState("");
  const [newGenre, setNewGenre] = useState("");
  const [selectedAuthorUuid, setSelectedAuthorUuid] = useState("");
  const [reactiveGenres, setReactiveGenres] = useState([]);
  
  // const { data: authorsData, refetch: refetchAuthors } = useQuery(GET_ALL_AUTHORS);
  const { data: authorsData } = useQuery(GET_ALL_AUTHORS);
  const { data: genresData } = useQuery(GET_ALL_GENRES);
  
  const [createBook] = useMutation(CREATE_BOOK, {
    refetchQueries: [{ query: GET_ALL_GENRES }],
    awaitRefetchQueries: true,
  });
  
  // useEffect(() => {
  //   refetchAuthors();
  // }, [refetchAuthors]);

  useEffect(() => {
    if (genresData?.getAllGenres) {
      setReactiveGenres([...genresData.getAllGenres]);
    }
  }, [genresData]);

  const isValid = title.trim() && publicationYear && (selectedGenre !== "new" || newGenre.trim()) && selectedAuthorUuid;

  const submitBook = async (e) => {
    e.preventDefault();
    if (!isValid) return;

    const genre = selectedGenre === "new" ? newGenre.trim() : selectedGenre;
    try {
      await createBook({
        variables: {
          title,
          publicationYear: Number(publicationYear),
          genre,
          authorUuid: selectedAuthorUuid,
        },
      });
      alert("Book added successfully!");

      if (selectedGenre === "new" && !reactiveGenres.includes(newGenre.trim())) {
        setReactiveGenres([...reactiveGenres, newGenre.trim()]);
      }

      setTitle("");
      setPublicationYear("");
      setSelectedGenre("");
      setNewGenre("");
      setSelectedAuthorUuid("");
      // refetchAuthors();
    } catch (err) {
      alert("Error adding book");
    }
  };

  return (
    <div className="flex flex-col items-center p-6">
      <h1 className="text-2xl font-bold mb-4">📘 Add a New Book</h1>
      <span className="block w-96 h-1 bg-teal-400 mx-auto rounded-md mb-6"></span>
      <form onSubmit={submitBook} className="flex flex-col gap-4 w-80">
        
        <label className="text-lg">
          Title:
          <input 
            value={title} 
            onChange={(e) => setTitle(e.target.value)} 
            type="text" 
            required 
            className="w-full p-2 border rounded border-gray-400" 
          />
        </label>

        <label className="text-lg">
          Publication Year:
          <input 
            value={publicationYear} 
            onChange={(e) => setPublicationYear(e.target.value)} 
            type="number" 
            required 
            className="w-full p-2 border rounded border-gray-400" 
          />
        </label>

        <label className="text-lg">
          Genre:
          <select 
            value={selectedGenre} 
            onChange={(e) => setSelectedGenre(e.target.value)} 
            required 
            className="w-full p-2 border rounded border-gray-400"
          >
            <option value="">Select a genre</option>
            {reactiveGenres.map((genre) => (
              <option key={genre} value={genre}>{genre}</option>
            ))}
            <option value="new">➕ Add New Genre</option>
          </select>
        </label>

        {selectedGenre === "new" && (
          <input 
            value={newGenre} 
            onChange={(e) => setNewGenre(e.target.value)} 
            placeholder="New Genre" 
            required 
            className="w-full p-2 border rounded border-gray-400" 
          />
        )}

        {/* Author Dropdown */}
        <label className="text-lg">
          Author:
          <select 
            value={selectedAuthorUuid} 
            onChange={(e) => setSelectedAuthorUuid(e.target.value)} 
            required 
            className="w-full p-2 border rounded border-gray-400"
          >
            <option value="">Select an author</option> 
            {authorsData?.getAllAuthors.map((author) => (
              <option key={author.uuid} value={author.uuid}>{author.name}</option>
            ))}
          </select>
        </label>

        <button 
          type="submit" 
          disabled={!isValid} 
          className={`p-2 text-white rounded ${isValid ? "bg-red-500 hover:bg-red-600" : "bg-gray-400 cursor-not-allowed"}`}
        >
          Add Book
        </button>
      </form>
    </div>
  );
}
