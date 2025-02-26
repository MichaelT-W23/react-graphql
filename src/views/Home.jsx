import RouterBtn from '../components/RouterBtn'
import '../styles/views/Home.css'

function HomePage() {
  return (
    <div>
      <p className="title">HOME PAGE</p>
      <RouterBtn path="/second-page" buttonText="Go to 2nd page" />
    </div>
  );
}

export default HomePage;