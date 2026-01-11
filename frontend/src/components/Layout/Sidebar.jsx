/**
 * Sidebar Component (Optional - Simple version)
 */

import React from 'react';
import { FaChartLine, FaBell, FaCog, FaThermometerHalf } from 'react-icons/fa';
import './Layout.scss';

const Sidebar = ({ activeSection = 'dashboard', onSectionChange }) => {
  const menuItems = [
    { id: 'dashboard', icon: FaThermometerHalf, label:'Dashboard' },
    { id: 'charts', icon: FaChartLine, label: 'Analytics' },
    { id: 'alerts', icon: FaBell, label: 'Alerts' },
    { id: 'settings', icon: FaCog, label: 'Settings' },
  ];

  return (
    <aside className="sidebar">
      <nav className="sidebar__nav">
        {menuItems.map(item => (
          <button
            key={item.id}
            className={`sidebar__item ${activeSection === item.id ? 'sidebar__item--active' : ''}`}
            onClick={() => onSectionChange && onSectionChange(item.id)}
          >
            <item.icon className="sidebar__icon" />
            <span className="sidebar__label">{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
};

export default Sidebar;