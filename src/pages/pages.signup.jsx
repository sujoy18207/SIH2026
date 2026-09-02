import { useState } from "react";
import { FaGoogle } from 'react-icons/fa';
import { IoLogoApple } from 'react-icons/io5';
import { User, Mail, Lock, Eye, Construction } from 'lucide-react';
import "./pages.signup.css";
export default function Signup() {
    const [role, setRole] = useState("user");
    const [showPassword, setShowPassword] = useState(false);
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        password: "",
    });
    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    }
    const handleSubmit = (e) => {
        e.preventDefault();
        console.log("Form submitted:", {role, ...formData});
    }
    return(
        <div className="auth-card">
            <div className="logo">
                    <Construction className= "logo-icon" size={20}/>
                    <span>MPLADS</span>
            </div>
            <div className="form-panel">
                <h2 className="form-heading">Sign Up</h2>
                <p className="form-description">Create an account to get started.</p>
                <div className="role-toggle">
                    <label className="role-option">
                        <input
                            type="radio"
                            name="role"
                            checked={role === "user"}
                            onChange={() => setRole("user")}    
                        />
                        As a User
                    </label>
                    <label className="role-option">
                        <input
                            type="radio"
                            name="role"
                            checked={role === "officials"}
                            onChange={() => setRole("officials")}
                        />
                        As an official
                    </label>
                </div>
                <button className="oauth-button" type="button">
                    <FaGoogle size={12}/>
                    Sign up with Google
                </button>
                <button className="oauth-button" type="button">
                    <IoLogoApple size={13}/>
                    Sign up with Apple
                </button>
                <div className="divider">
                    OR
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Name</label>
                        <div className="input-wrapper">
                            <User className="input-icon" size={15} />
                            <input
                                className="form-input"
                                type="text"
                                name="name"
                                placeholder="Enter your name"
                                value={formData.name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Email</label>
                        <div className="input-wrapper">
                            <Mail className="input-icon" size={15} />
                            <input
                                className="form-input"
                                type="email"
                                name="email"
                                placeholder="Enter your email"
                                value={formData.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Password</label>
                        <div className="input-wrapper">
                            <Lock className="input-icon" size={15} />
                            <input
                                className="form-input"
                                type={showPassword ? "text" : "password"}
                                name="password"
                                placeholder="Enter your password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                            />
                            <span className="password-toggle-icon" onClick={() => setShowPassword(!showPassword)}>
                                <Eye className="password-toggle-icon" size={15} />
                            </span>
                        </div>
                    </div>
                    <button className="btn-primary" type="submit">
                        Sign Up
                    </button>
                </form>
                <p className="form-footer">
                    Already have an account? <a href="/login">Login</a>
                </p>
            </div>
        </div>
    )
}