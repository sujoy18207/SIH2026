import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import './DashboardLayout.css';

export default function DashboardLayout() {
  return (
    <div className="dashboard-wrapper">
      <header className="navbar-container">
        <nav className="floating-navbar">
          <div className="nav-logo">
            <span className="logo-icon">🪐</span>
          </div>
          <div className="nav-links">
            <NavLink 
              to="/dashboard/home" 
              end 
              className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}
            >
              Home
            </NavLink>

            <NavLink 
              to="/dashboard/details" 
              className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}
            >
              Details
            </NavLink>

            <NavLink 
              to="/dashboard/leaderboard" 
              className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}
            >
              Leaderboard
            </NavLink>

            <NavLink 
              to="/dashboard/ai" 
              className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}
            >
              AI
            </NavLink>
          </div>

          {/* Pill Button on Far Right */}
          <div className="nav-action">
            <button className="email-pill-btn">BWU 404</button>
          </div>
        </nav>
      </header>
        <Outlet />
    </div>
  );
}