
export default async function handler(req, res) {
  try {
    // Handle case where req.query or path might be undefined
    const { path } = req.query || {};
    
    if (!path || !Array.isArray(path)) {
      return res.status(400).json({ error: 'Invalid path parameter' });
    }

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const pathString = path.join('/');
    const queryString = req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : '';
    const target = `${apiUrl}/${pathString}${queryString}`;

    // Prepare headers
    const headers = {
      'Content-Type': 'application/json',
    };

    // Prepare request options
    const fetchOptions = {
      method: req.method,
      headers,
    };

    // Add body for non-GET requests
    if (req.method !== 'GET' && req.body) {
      fetchOptions.body = JSON.stringify(req.body);
    }

    const response = await fetch(target, fetchOptions);
    
    // Handle response
    if (!response.ok) {
      return res.status(response.status).json({ 
        error: `API request failed: ${response.statusText}` 
      });
    }

    const data = await response.json();
    res.status(response.status).json(data);
    
  } catch (error) {
    console.error('API Proxy Error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}
