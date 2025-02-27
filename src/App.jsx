import { AppRouter } from './router';
import './App.css';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <div className="flex h-screen">
      <div className="w-[245px]">
        <Sidebar />
      </div>
      
      <div className="flex-1 p-6 overflow-auto">
        <AppRouter />
      </div>
    </div>
  );
}

export default App;
