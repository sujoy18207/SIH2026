import { useNavigate } from "react-router-dom"
import ComingSoon from "../../components/ComingSoon";
export default function HomeDashboard(){
    const navigate = useNavigate();
    const handleSignup = () => {navigate("/dashboard/home")};
        return(
        <ComingSoon/>
    )
}