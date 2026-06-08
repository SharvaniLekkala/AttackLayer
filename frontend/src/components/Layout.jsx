import { Link, useLocation } from "react-router-dom";

function Layout({ children }) {

    const location = useLocation();

    return (
        <div className="app-layout">
            <nav className="app-nav">
                <div className="app-nav-brand">ATTACKLAYER</div>
                <div className="app-nav-links">
                    <Link
                        to="/chat"
                        className={location.pathname === "/chat" ? "nav-link active" : "nav-link"}
                    >
                        Chat
                    </Link>
                    <Link
                        to="/dashboard"
                        className={location.pathname === "/dashboard" ? "nav-link active" : "nav-link"}
                    >
                        Dashboard
                    </Link>
                </div>
            </nav>
            {children}
        </div>
    );
}

export default Layout;
