import { useNavigate } from "react-router-dom"
import ComingSoon from "../../components/ComingSoon";

export default function AI(){
    const navigate = useNavigate();
    const handleSignup = () => {navigate("/dashboard/ai")};
    return(
        <ComingSoon/>
    );
}