import React from 'react';
import { Outlet, NavLink } from 'react-router-dom';
import './DashboardLayout.css';

export default function DashboardLayout() {
  return (
    <div className="dashboard-wrapper">
      {/* Floating Pill Navbar */}
      <header className="navbar-container">
        <nav className="floating-navbar">
          {/* Brand Logo Circle */}
          <div className="nav-logo">
            <span className="logo-icon">🪐</span>
          </div>

          {/* Navigation Links */}
          <div className="nav-links">
            <NavLink 
              to="/dashboard" 
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

      {/* Dynamic Page Content */}
      <main className="dashboard-content">
        <Outlet />
      </main>
    </div>
  );
}