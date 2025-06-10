
export default async function handler(req, res) {
  const { path } = req.query;
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const target = apiUrl + '/' + path.join('/');
  const resp = await fetch(target + (req.url.includes('?') ? req.url.slice(req.url.indexOf('?')) : ''), {
    method: req.method,
    headers: { 'Content-Type': 'application/json' },
    body: req.method === 'GET' ? undefined : JSON.stringify(req.body)
  });
  const data = await resp.json();
  res.status(resp.status).json(data);
}
