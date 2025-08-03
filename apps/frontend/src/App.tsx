import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Home from './pages/Home'
import Users from './pages/Users'
import Projects from './pages/Projects'
import Resume from './pages/Resume'
import Roadmap from './pages/Roadmap'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/users" element={<Users />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/roadmap" element={<Roadmap />} />
      </Routes>
    </Layout>
  )
}

export default App