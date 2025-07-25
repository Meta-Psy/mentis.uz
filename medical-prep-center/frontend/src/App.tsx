import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

// Landing page
import Landing from "./pages/Landing";

// Parent pages
import ParentDashboard from "./pages/Parent/Dashboard/Dashboard";
// import ParentRecommendations from "./pages/Parent/Recommendations/ParentRecommendations";
import ParentDetails from "./pages/Parent/Statistics/ParentDetails";
import ParentStatistics from "./pages/Parent/Statistics/ParentStatistics";

// Student pages
import StudentDashboard from "./pages/Student/Dashboard/StudentDashboard";
import StudentMaterials from "./pages/Student/Materials/StudentMaterials";
import StudentTests from "./pages/Student/Tests/AllTestsPage";
import StudentTest from "./pages/Student/Tests/ActiveTestPage";
import TestResults from "./pages/Student/Tests/TestResults";

// Teacher pages
import TeacherDashboard from "./pages/Teacher/Dashboard/TeacherDashboard";

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
          {/* <Route
            path="/parent/recommendations"
            element={<ParentRecommendations />}
          /> */}
          <Route path="/parent/details" element={<ParentDetails />} />
          <Route path="/parent/statistics" element={<ParentStatistics />} />

          {/* Student Routes */}
          <Route path="/student" element={<StudentDashboard />} />
          <Route path="/student/materials" element={<StudentMaterials />} />
          <Route path="/student/tests" element={<StudentTests />} />
          <Route path="/student/test" element={<StudentTest />} />
          <Route path="/student/test_results" element={<TestResults />} />

          {/* Student Routes */}
          <Route path="/teacher" element={<TeacherDashboard teacherId={1}/>} />


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
