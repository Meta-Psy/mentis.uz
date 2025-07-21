import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Landing page
import Landing from "./pages/Landing";

// Parent pages
import ParentDashboard from "./pages/Parent/Dashboard";
import ParentRecommendations from "./pages/Parent/Recomendations";
import ParentDetails from "./pages/Parent/Details";
import ParentStatistics from "./pages/Parent/Statistic";

// Student pages
import StudentDashboard from "./pages/Student/Dashboard";
import StudentPerformance from "./pages/Student/Performance";
import StudentMaterials from "./pages/Student/Materials";
import StudentTests from "./pages/Student/Tests";
import StudentTest from "./pages/Student/Test";
import TestResults from "./pages/Student/TestResults";

// Teacher pages
import TeacherDashboard from "./pages/Teacher/Dashboard";

import "./index.css";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Landing */}
          <Route path="/" element={<Landing />} />

          {/* Parent Routes */}
          <Route path="/parent" element={<ParentDashboard />} />
          <Route
            path="/parent/recommendations"
            element={<ParentRecommendations />}
          />
          <Route path="/parent/details" element={<ParentDetails />} />
          <Route path="/parent/statistics" element={<ParentStatistics />} />

          {/* Student Routes */}
          <Route path="/student" element={<StudentDashboard />} />
          <Route path="/student/performance" element={<StudentPerformance />} />
          <Route path="/student/materials" element={<StudentMaterials />} />
          <Route path="/student/tests" element={<StudentTests />} />
          <Route path="/student/test" element={<StudentTest />} />
          <Route path="/student/test_results" element={<TestResults />} />

          {/* Student Routes */}
          <Route path="/teacher" element={<TeacherDashboard />} />


          {/* 404 page */}
          <Route
            path="*"
            element={
              <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-gray-900 mb-4">404</h1>
                  <p className="text-gray-600 mb-6">Страница не найдена</p>
                  <a href="/" className="btn-primary">
                    Вернуться на главную
                  </a>
                </div>
              </div>
            }
          />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
