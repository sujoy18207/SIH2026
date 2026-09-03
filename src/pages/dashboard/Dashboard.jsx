import { useNavigate } from "react-router-dom"
export default function Dashboard(){
    const navigate = useNavigate();
    const handleSignup = () => {navigate("/dashboard")};
        return(
        <div>
            <h1>Currently dashboard is in building stage, Thank you for having patience</h1>
        </div>
    )
}