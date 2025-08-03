import { serve } from '@hono/node-server'
import { serveStatic } from '@hono/node-server/serve-static'
import app from './routes'

// Serve static files from client/dist
app.use('/*', serveStatic({ root: './client/dist' }))

const port = 3000
console.log(`🚀 Mantrix Learning Platform starting on http://localhost:${port}`)

serve({
  fetch: app.fetch,
  port,
})

console.log(`✅ Frontend server running on http://localhost:${port}`)
console.log(`🔗 Backend API available at http://localhost:8000`)
console.log(`📚 Full learning platform ready!`)