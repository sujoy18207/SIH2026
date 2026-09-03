import { BrowserRouter,Routes,Route } from "react-router-dom";
import Signup from "../pages/pages.signup.jsx";
import Dashboard from "../pages/dashboard/Dashboard.jsx";
import AI from "../pages/dashboard/AI.jsx";
import LandingPage from "../pages/page.Landing.jsx";
import PageTransition from "../components/PageTransition.jsx";



export default function AppRoutes(){
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/"element={<PageTransition><LandingPage /></PageTransition>}/>
                <Route path="/signup" element={<PageTransition><Signup /></PageTransition>}/>
                <Route path="/dashboard" element={<PageTransition><Dashboard /></PageTransition>}/>
                <Route path="/dashboard/ai" element={<PageTransition><AI /></PageTransition>}/>
            </Routes>
        </BrowserRouter>
    );
}