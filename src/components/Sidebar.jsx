import { Link, Outlet } from "react-router-dom";
import { parse } from "jsonc-parser";
import sidebarRawData from "./sidebarData.jsonc?raw";
import "../styles/components/Sidebar.css";

const sidebarData = parse(sidebarRawData);

const Sidebar = () => {
  return (
    <div className="sidebar-container">
      {/* Sidebar */}
      <div className="sidebar">
        <h2>BookQL</h2>
        <nav>
          <ul>
            {sidebarData.SidebarItems.map((item, index) => (
              <li key={index}>
                <Link to={item.route} className="sidebar-link">
                  <span className="material-symbols-outlined">{item.icon}</span>
                  {item.name}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      {/* Main Content */}
      <div className="main-content">
        <Outlet />
      </div>
    </div>
  );
};

export default Sidebar;
