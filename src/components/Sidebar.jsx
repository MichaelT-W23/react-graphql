import { useState } from "react";
import { Link, Outlet } from "react-router-dom";
import { parse } from "jsonc-parser";
import sidebarRawData from "./sidebarData.jsonc?raw";
import "../styles/components/Sidebar.css";

const sidebarData = parse(sidebarRawData);

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [activeItem, setActiveItem] = useState(null);

  const handleNavClick = (item) => {
    if (item.name === "Search") {
      setCollapsed(true);
      setShowSearch(true);
    } else {
      setShowSearch(false); // Close search when other items are clicked
      setCollapsed(false);
    }
    setActiveItem(item.name);
  };

  return (
    <div className="sidebar-container">
      {/* Sidebar */}
      <div className={`sidebar ${collapsed ? "collapsed" : ""}`}>
        <h2 className={collapsed ? "hidden" : ""}>BookQL</h2>
        <nav>
          <ul>
            {sidebarData.SidebarItems.map((item, index) => (
              <li key={index}>
                <Link
                  to={item.route}
                  className={`sidebar-link ${item.name === "Search" && showSearch ? "active-search" : ""}`}
                  onClick={() => handleNavClick(item)}
                >
                  <span className="material-symbols-outlined">{item.icon}</span>
                  {!collapsed && item.name}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
      </div>

      {/* Search View */}
      {showSearch && (
        <div className="search-view">
          <input type="text" placeholder="Search..." className="search-input" />
        </div>
      )}

      {/* Main Content */}
      <div className="main-content">
        <Outlet />
      </div>
    </div>
  );
};

export default Sidebar;
