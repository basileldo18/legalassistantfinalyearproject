import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css'
import Login from "./component/login/login"; 
import MainPage from "./component/mainpage/main";
import Chatbot from "./component/chatbot/chatbot"
function App() {
  return (
     <Router>
     <div className="App">
       <Routes>
         <Route path="/" element={<Login />} /> {/* Login Page */}
         <Route path="/main" element={<MainPage />} /> 
         <Route path="/chatbot" element={<Chatbot />} /> 
       </Routes>
     </div>
   </Router>
  );
}

export default App;

