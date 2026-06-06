import {

    Routes,

    Route,

    Navigate

} from "react-router-dom";

import ChatPage from "./pages/ChatPage";

import DashboardPage from "./pages/DashboardPage";

import "./App.css";

function App() {

    return (

        <Routes>

            <Route

                path="/"

                element={

                    <Navigate

                        to="/chat"

                        replace

                    />

                }

            />

            <Route

                path="/chat"

                element={

                    <ChatPage />

                }

            />

            <Route

                path="/dashboard"

                element={

                    <DashboardPage />

                }

            />

        </Routes>

    );

}

export default App;