import { useState } from 'react'
import RouterBtn from '../components/RouterBtn'

function SecondPage() {
  const [count, setCount] = useState(0);

  const incrementCount = () => {
    setCount(count + 1);
  };

  return (
    <div className="bg-purple-800">
      <p className="text-purple-500 font-sans">SECOND PAGE</p>
      <RouterBtn path="/" buttonText="Go to Home Page" />
      <div>
        <button onClick={incrementCount}
        className="mt-2 px-4 py-2 text-white bg-gray-500 hover:bg-gray-700">
          Count {count}
        </button>
      </div>
    </div>
  );
}

export default SecondPage;
