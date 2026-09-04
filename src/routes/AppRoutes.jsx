import { BrowserRouter,Routes,Route } from "react-router-dom";
import Signup from "../pages/pages.signup.jsx";
import HomeDashboard from "../pages/dashboard/Dashboard.jsx";
import AI from "../pages/dashboard/AI.jsx";
import LandingPage from "../pages/page.Landing.jsx";
import PageTransition from "../components/PageTransition.jsx";
import DashboardLayout from "../components/dashboard/DashboardLayout.jsx";
import NotFound from "../components/NotFound.jsx";
import ComingSoon from "../components/ComingSoon.jsx";



export default function AppRoutes(){
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/"element={<PageTransition><LandingPage /></PageTransition>}/>
                <Route path="/signup" element={<PageTransition><Signup /></PageTransition>}/>
                <Route path="/dashboard" element={<DashboardLayout />}>
                    <Route index element={<PageTransition><HomeDashboard /></PageTransition>}/>
                    <Route path="/dashboard/ai" element={<PageTransition><AI /></PageTransition>}/>
                    <Route path="*" element={<ComingSoon />} />
                </Route>
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}