import "./Landing.css"
import { useNavigate } from "react-router-dom"
export default function LandingPage(){
    const navigate = useNavigate();
    const handleSignup = () => {navigate("/signup")};
    const handleDashboard =() => {navigate("/dashboard/home")};
    return(
        <div className="landing-page">
            <div className="cta-container">
                <button className="btn-primary-sign-up" onClick={handleSignup}>
                    Sign Up ➡
                </button>

                <button className="btn-secondary-ai-launcher" onClick={handleDashboard}>
                    Dashboard
                </button>
            </div>
        </div>
    );
}