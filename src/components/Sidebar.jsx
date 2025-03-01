import { useState } from "react";
import { Link, Outlet } from "react-router-dom";
import { parse } from "jsonc-parser";
import sidebarRawData from "./sidebarData.jsonc?raw";
import SearchView from "./SearchView";
import styles from "../styles/components/Sidebar.module.css";

const sidebarData = parse(sidebarRawData);

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [showSearch, setShowSearch] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  const handleNavClick = (item) => {
    setSelectedItem(item.name);

    if (item.name === "Search") {
      setCollapsed(true);
      setShowSearch(true);
    } else {
      setShowSearch(false);
      setCollapsed(false);
    }
  };

  const handleCloseSearch = () => {
    setShowSearch(false);
    setCollapsed(false);
    setSelectedItem(null);
  };

  return (
    <div className={styles["sidebar-container"]}>
      <div className={`${styles.sidebar} ${collapsed ? styles.collapsed : ""}`}>
        <h2 className={collapsed ? styles.hidden : ""}>BookQL</h2>
        <nav>
          <ul>
            {sidebarData.SidebarItems.map((item, index) => (
              <li key={index}>
                <Link
                  to={item.route || "#"}
                  className={`${styles["sidebar-link"]} 
                              ${item.name === selectedItem ? styles["active-item"] : ""} 
                              ${item.name === "Search" && showSearch ? styles["active-search"] : ""}`}
                  onClick={(event) => handleNavClick(item, event)}
                >
                  <span className={`material-symbols-outlined ${item.name === selectedItem ? styles["active-icon"] : ""}`}>
                    {item.icon}
                  </span>
                  {!collapsed && item.name}
                </Link>
              </li>
            ))}
          </ul>
        </nav>
        <div className={`${styles["search-container"]} ${showSearch ? styles["search-open"] : styles["search-closed"]}`}>
          {showSearch && <SearchView onClose={handleCloseSearch} />}
        </div>
      </div>
      
      <div className={styles["main-content"]}>
        <Outlet />
      </div>
    </div>
  );
};

export default Sidebar;
