import PropTypes from "prop-types";

const BookCard = ({ title, body }) => {
  return (
    <div className="w-72 bg-gray-100 rounded-xl shadow-xl overflow-hidden transition-transform duration-300 ease-in-out hover:-translate-y-1 hover:shadow-lg">
      <div style={{ backgroundColor: '#5EA98C' }} className="p-3">
        <h3 className="text-lg font-bold text-black text-center">{title}</h3>
      </div>
      <div className="p-4">
        <p className="text-sm text-gray-700 mb-1">
          <strong className="text-gray-900">Author:</strong> {body.author.name}
        </p>
        <p className="text-sm text-gray-700 mb-1">
          <strong className="text-gray-900">Publication Year:</strong> {body.publicationYear}
        </p>
        <p className="text-sm text-gray-700">
          <strong className="text-gray-900">Genre:</strong> {body.genre}
        </p>
      </div>
    </div>
  );
};

BookCard.propTypes = {
  title: PropTypes.string.isRequired,
  body: PropTypes.shape({
    author: PropTypes.shape({
      name: PropTypes.string.isRequired
    }).isRequired,
    publicationYear: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
    genre: PropTypes.string.isRequired
  }).isRequired
};

export default BookCard;
