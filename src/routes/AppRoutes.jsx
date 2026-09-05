import { useState, useEffect } from "react";
import { BrowserRouter,Routes,Route } from "react-router-dom";
import Signup from "../pages/pages.signup.jsx";
import HomeDashboard from "../pages/dashboard/Dashboard.jsx";
import LandingPage from "../pages/page.Landing.jsx";
import PageTransition from "../components/PageTransition.jsx";
import DashboardLayout from "../components/dashboard/DashboardLayout.jsx";
import NotFound from "../components/NotFound.jsx";
import ComingSoon from "../components/ComingSoon.jsx";
import LoadingScreen from "../components/LoadingScreen.jsx";



export default function AppRoutes(){
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const timer = setTimeout(() => {
        setIsLoading(false);
        }, 600);

        return () => clearTimeout(timer);
    }, []);

    if (isLoading) {
        return <LoadingScreen />;
    }
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/"element={<PageTransition><LandingPage /></PageTransition>}/>
                <Route path="/signup" element={<PageTransition><Signup /></PageTransition>}/>
                <Route path="/dashboard" element={<DashboardLayout />}>
                    <Route index element={<HomeDashboard />} />
                    <Route path="*" element={<ComingSoon />} />
                </Route>
                <Route path="*" element={<NotFound />} />
            </Routes>
        </BrowserRouter>
    );
}