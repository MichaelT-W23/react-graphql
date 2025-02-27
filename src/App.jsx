import { AppRouter } from './router';
import './App.css';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <div className="flex h-screen">
      <div className="w-[245px]">
        <Sidebar />
      </div>
      
      <div >
        <AppRouter />
      </div>
    </div>
  );
}

export default App;
