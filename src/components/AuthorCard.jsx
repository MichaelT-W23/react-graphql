import { useState } from "react";
import PropTypes from "prop-types";

const AuthorCard = ({ name, details }) => {
  const [showBooks, setShowBooks] = useState(false);

  return (
    <div className="w-72 bg-gray-100 rounded-xl shadow-lg p-4 transition-transform transform hover:shadow-2xl">
      <div className="text-center">
        <h3 className="text-xl font-bold text-gray-800 mb-2">{name}</h3>
        <p className="text-gray-600"><strong>Age:</strong> {details.age}</p>
        <p className="text-gray-600"><strong>Nationality:</strong> {details.nationality}</p>
      </div>
      
      <button
        className="mt-4 w-full bg-teal-600 text-white py-2 rounded-lg text-sm font-semibold hover:bg-teal-700 transition"
        onClick={() => setShowBooks(!showBooks)}
      >
        {showBooks ? "Hide Books" : "See Books"}
      </button>
      
      {showBooks && (
        <div className="mt-4">
          {details.books && details.books.length ? (
            <ul className="list-none space-y-2">
              {details.books.map((book) => (
                <li key={book.id} className="text-sm text-gray-700">
                  <strong>• {book.title}</strong> ({book.publicationYear}) - {book.genre}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-gray-500 mt-2">No books were found for this author.</p>
          )}
        </div>
      )}
    </div>
  );
};

AuthorCard.propTypes = {
  name: PropTypes.string.isRequired,
  details: PropTypes.shape({
    age: PropTypes.number,
    nationality: PropTypes.string,
    books: PropTypes.arrayOf(
      PropTypes.shape({
        id: PropTypes.number.isRequired,
        title: PropTypes.string.isRequired,
        publicationYear: PropTypes.number.isRequired,
        genre: PropTypes.string.isRequired
      })
    )
  }).isRequired
};

export default AuthorCard;