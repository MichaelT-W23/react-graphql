import { useState } from "react";
import { Link, Outlet } from "react-router-dom";
import { parse } from "jsonc-parser";
import sidebarRawData from "./sidebarData.jsonc?raw";
import SearchView from "./SearchView";
import "../styles/components/Sidebar.css";

const sidebarData = parse(sidebarRawData);

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [showSearch, setShowSearch] = useState(false);

  const handleNavClick = (item) => {
    if (item.name === "Search") {
      setCollapsed(true);
      setShowSearch(true);
    } else {
      setShowSearch(false); // Close search when other items are clicked
      setCollapsed(false);
    }
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
        <SearchView></SearchView>
      )}

      {/* Main Content */}
      <div className="main-content">
        <Outlet />
      </div>
    </div>
  );
};

export default Sidebar;
