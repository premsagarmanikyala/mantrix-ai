# External Roadmap API Documentation

## Overview

The External Roadmap API provides access to learning roadmaps from multiple open sources, giving users access to community-driven and professionally curated learning paths beyond AI-generated content.

## Supported Sources

1. **GitHub Awesome Lists** - Community-curated learning roadmaps from GitHub
2. **Roadmap.sh** - Developer roadmaps for various technologies  
3. **FreeCodeCamp** - Free coding bootcamp curriculum roadmaps

## Endpoints

### GET /api/v1/external-roadmaps/sources

Get list of available external roadmap sources.

**Response:**
```json
[
  {
    "id": "github_awesome",
    "name": "GitHub Awesome Lists",
    "description": "Community-curated learning roadmaps from GitHub",
    "base_url": "https://api.github.com/repos",
    "is_active": true
  },
  {
    "id": "roadmap_sh", 
    "name": "Roadmap.sh",
    "description": "Developer roadmaps for various technologies",
    "base_url": "https://roadmap.sh/roadmaps",
    "is_active": true
  },
  {
    "id": "freecodecamp",
    "name": "FreeCodeCamp", 
    "description": "Free coding bootcamp curriculum roadmaps",
    "base_url": "https://api.freecodecamp.org",
    "is_active": true
  }
]
```

### GET /api/v1/external-roadmaps/search

Search for roadmaps across external sources.

**Parameters:**
- `query` (required): Search query (e.g., "javascript", "python", "web development")
- `sources` (optional): Comma-separated list of source IDs to search
- `limit` (optional): Maximum number of results (default: 10, max: 50)

**Example Request:**
```
GET /api/v1/external-roadmaps/search?query=javascript&sources=roadmap_sh,freecodecamp&limit=5
```

**Response:**
```json
{
  "roadmaps": [
    {
      "id": "roadmapsh_frontend",
      "title": "Frontend Developer Roadmap",
      "description": "Step-by-step guide to becoming a modern frontend developer",
      "source": "Roadmap.sh",
      "source_url": "https://roadmap.sh/frontend",
      "topics": ["html", "css", "javascript", "react", "vue"],
      "difficulty": "Beginner to Advanced",
      "estimated_duration": 500,
      "steps": [
        {
          "title": "Learn HTML",
          "description": "Semantic HTML and accessibility",
          "type": "learning",
          "estimated_time": 40
        },
        {
          "title": "Learn CSS",
          "description": "Styling, layouts, and responsive design", 
          "type": "learning",
          "estimated_time": 60
        }
      ]
    }
  ],
  "query": "javascript",
  "sources_searched": ["roadmap_sh", "freecodecamp"],
  "total_found": 1,
  "status": "success"
}
```

### POST /api/v1/external-roadmaps/search

Alternative POST method for searching roadmaps with request body.

**Request Body:**
```json
{
  "query": "python",
  "sources": ["roadmap_sh", "freecodecamp"],
  "limit": 10
}
```

**Response:** Same format as GET method.

### GET /api/v1/external-roadmaps/health

Health check for external roadmap service.

**Response:**
```json
{
  "status": "healthy",
  "service": "external-roadmaps", 
  "active_sources": ["github_awesome", "roadmap_sh", "freecodecamp"],
  "total_sources": 3,
  "test_search_working": true
}
```

## Data Models

### ExternalRoadmap

```typescript
interface ExternalRoadmap {
  id: string;                    // Unique identifier
  title: string;                 // Roadmap title
  description: string;           // Description of the roadmap
  source: string;               // Source name (e.g., "Roadmap.sh")
  source_url?: string;          // Link to original source
  topics: string[];             // List of related topics/tags
  difficulty?: string;          // Difficulty level
  estimated_duration?: number;  // Total duration in minutes
  steps: ExternalRoadmapStep[]; // Learning steps
}
```

### ExternalRoadmapStep

```typescript
interface ExternalRoadmapStep {
  title: string;        // Step title
  description: string;  // Step description
  type: string;        // Type (e.g., "learning", "practice", "reading")
  estimated_time: number; // Duration in minutes
}
```

## Usage Examples

### Frontend Integration

```javascript
// Search for JavaScript roadmaps
const searchRoadmaps = async (query) => {
  const response = await fetch(`/api/v1/external-roadmaps/search?query=${encodeURIComponent(query)}`);
  const data = await response.json();
  return data.roadmaps;
};

// Get available sources
const getSources = async () => {
  const response = await fetch('/api/v1/external-roadmaps/sources');
  return await response.json();
};
```

### Python Client

```python
import httpx

class ExternalRoadmapClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
    
    async def search_roadmaps(self, query, sources=None, limit=10):
        params = {"query": query, "limit": limit}
        if sources:
            params["sources"] = ",".join(sources)
        
        response = await self.client.get(
            f"{self.base_url}/api/v1/external-roadmaps/search",
            params=params
        )
        return response.json()
    
    async def get_sources(self):
        response = await self.client.get(
            f"{self.base_url}/api/v1/external-roadmaps/sources"
        )
        return response.json()
```

## Error Handling

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid parameters (e.g., empty query)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

Error responses include a descriptive message:

```json
{
  "detail": "Query parameter is required"
}
```

## Rate Limiting

- GitHub API integration may experience rate limiting in high-traffic scenarios
- Roadmap.sh and FreeCodeCamp sources use static data mapping and are not rate-limited
- Failed external API calls are gracefully handled with logging

## Implementation Notes

1. **GitHub Integration**: Uses GitHub API to search for awesome lists. May hit rate limits in production.

2. **Roadmap.sh Integration**: Uses curated static data mapping for popular technology roadmaps.

3. **FreeCodeCamp Integration**: Maps to FreeCodeCamp's curriculum structure with static course data.

4. **Caching**: Consider implementing caching for frequently requested roadmaps to improve performance.

5. **Authentication**: Currently no authentication required. Consider adding API keys for production use.

## Contributing

To add a new external source:

1. Add source configuration to `ExternalRoadmapService.__init__`
2. Implement search method (e.g., `_search_new_source`)
3. Add mapping in `search_roadmaps` method
4. Update documentation

The service is designed to be extensible for additional learning platforms.