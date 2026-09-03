import { useNavigate } from "react-router-dom"

export default function AI(){
    const navigate = useNavigate();
    const handleSignup = () => {navigate("/dashboard.ai")};
    return(
        <div>
            <h1>Currently AI is in building stage, Thank you for having patience</h1>
        </div>
    );
}