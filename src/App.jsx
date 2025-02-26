import { AppRouter } from './router';
import './App.css';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 p-6 overflow-auto">
        <p className="text-2xl">TEST WEBSITE</p>
        <AppRouter />
      </div>
    </div>
  );
}

export default App;
