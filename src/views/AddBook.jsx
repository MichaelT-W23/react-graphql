import { useEffect } from "react";
import { useQuery, gql } from "@apollo/client";
import AuthorCard from "../components/AuthorCard";

const GET_ALL_AUTHORS = gql`
  query {
    getAllAuthors {
      id
      name
      age
      nationality
      books {
        id
        title
        publicationYear
        genre
      }
    }
  }
`;

const AuthorsPage = () => {
  const { data, loading, error, refetch } = useQuery(GET_ALL_AUTHORS);

  useEffect(() => {
    refetch();
  }, [refetch]);

  return (
    <div className="flex flex-col items-center">
      <h1 className="pt-4 text-2xl font-bold mb-5 text-gray-800 text-center tracking-wide relative">
        ✍🏻 Explore Our Authors
        <span className="block w-96 h-1 bg-red-400 mt-2 mx-auto rounded-md"></span>
      </h1>
      
      {loading && <p className="text-lg text-gray-500">Loading authors...</p>}
      {error && <p className="text-lg text-red-500">Error loading authors: {error.message}</p>}
      
      {data?.getAllAuthors?.length > 0 && (
        <ul className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-5 justify-center max-w-6xl w-full pb-24">
          {data.getAllAuthors.map((author) => (
            <li key={author.id} className="flex justify-center">
              <AuthorCard name={author.name} details={author} />
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default AuthorsPage;