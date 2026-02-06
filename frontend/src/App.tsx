import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Dashboard } from '@/components/Dashboard';
import { InterventionList } from '@/components/InterventionList';
import { InterventionDetail } from '@/components/InterventionDetail';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-6 py-4">
            <div className="flex justify-between items-center">
              <Link to="/" className="text-xl font-bold text-blue-600 hover:text-blue-700">
                长寿医学临床干预模型
              </Link>
              <div className="flex gap-6">
                <Link
                  to="/"
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  仪表盘
                </Link>
                <Link
                  to="/interventions"
                  className="text-gray-600 hover:text-blue-600 transition-colors"
                >
                  干预措施
                </Link>
              </div>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/interventions" element={<InterventionList />} />
          <Route path="/interventions/:id" element={<InterventionDetail interventionId={1} />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
