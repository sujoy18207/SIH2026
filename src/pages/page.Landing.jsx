import "./Landing.css"
import { useNavigate } from "react-router-dom"
export default function LandingPage(){
    const navigate = useNavigate();
    const handleSignup = () => {navigate("/signup")};
    const handleAi =() => {navigate("/dashboard/ai")};
    return(
        <div className="landing-page">
            <button onClick={handleSignup}>
                Sign Up
            </button>
            <button onClick={handleAi}>
                Ai
            </button>
        </div>
    );
}