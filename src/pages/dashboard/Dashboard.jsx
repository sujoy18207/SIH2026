import myImage from '../../assets/home_page_image_mplapds.png';
import "./Dashboard.css"
import { useNavigate } from 'react-router-dom';
export default function HomeDashboard(){
    const navigate = useNavigate();
    const handleDetails = () => {navigate("/dashboard/details")};
    const handlechatassis = () => {navigate("/dashboard/ai")};
        return(
            <div className="dashboard-home-wrapper">
                <div className="home-content">
                    <div className="content">
                        <div className="text-content">
                            <h2>MPLADS (Members of Parliament Local Area Development Scheme) </h2><br />
                            <p>It is a Government of India initiative that enables Members of Parliament to recommend developmental works in their constituencies. The scheme focuses on creating durable community assets such as roads, schools, healthcare facilities, drinking-water infrastructure, sanitation facilities, and other public amenities. <br />
                            <br />Our platform aims to bring greater transparency and accessibility to MPLADS-related development by presenting constituency-wise projects, allocated funds, sanctioned works, expenditure, and project progress in an easy-to-understand format. This allows citizens to better understand how public funds are being utilized and track development activities in their area.</p>
                            <div className="action-buttons">
                                <button onClick={handleDetails} className="primary-btn">Go to Projects Details</button>
                                <button onClick={handlechatassis} className="primary-btn">Use Personal Chat Assistant</button>
                            </div>
                        </div>
                        <div className="img">
                            <img src={myImage} alt="image" />
                        </div>
                    </div>
                    <div className="footer-container">
                        <hr className="divider-line" />
                        <footer className='message'>
                            <span>Reminder 🔔 : The data you will see here-after are all <i>GOVERNMENT OF INDIA</i> given data.</span>
                        </footer>
                    </div>
                </div>
            </div>
    )
}