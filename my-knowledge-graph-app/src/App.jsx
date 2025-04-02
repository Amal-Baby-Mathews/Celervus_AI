// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import TopicsPage from './pages/TopicsPage';
import UploadPage from './pages/UploadPage';
import NotFoundPage from './pages/NotFoundPage';
// Import other pages as you create them (e.g., TopicDetailPage)

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}> {/* Use Layout for all nested routes */}
        <Route index element={<HomePage />} /> {/* index route for '/' */}
        <Route path="topics" element={<TopicsPage />} />
        {/* Example detail route: <Route path="topics/:topicId" element={<TopicDetailPage />} /> */}
        <Route path="upload" element={<UploadPage />} />
        <Route path="*" element={<NotFoundPage />} /> {/* Catch-all for 404 */}
      </Route>
    </Routes>
  );
}

export default App;