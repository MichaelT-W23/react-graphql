import PropTypes from "prop-types";

const BookCard = ({ book }) => {
  return (
    <div className="w-72 bg-gray-100 rounded-xl shadow-xl overflow-hidden transition-transform duration-300 ease-in-out hover:-translate-y-1 hover:shadow-lg">
      <div style={{ backgroundColor: '#5EA98C' }} className="p-3">
        <h3 className="text-lg font-bold text-black text-center">
          {book.title}
        </h3>
      </div>
      <div className="p-4">
        <p className="text-sm text-gray-700 mb-1">
          <strong>Author:</strong> {book.author?.name}
        </p>
        <p className="text-sm text-gray-700 mb-1">
          <strong>Publication Year:</strong> {book.publicationYear}
        </p>
        <p className="text-sm text-gray-700">
          <strong>Genre:</strong> {book.genre}
        </p>
      </div>
    </div>
  );
};

BookCard.propTypes = {
  book: PropTypes.shape({
    uuid: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
    publicationYear: PropTypes.oneOfType([
      PropTypes.string,
      PropTypes.number
    ]).isRequired,
    genre: PropTypes.string.isRequired,
    author: PropTypes.shape({
      uuid: PropTypes.string,
      name: PropTypes.string
    })
  }).isRequired
};

export default BookCard;