export default function handler(request, response) {
  const country =
    request.headers['x-vercel-ip-country'] ||
    request.headers['cf-ipcountry'] ||
    'GLOBAL'

  response.setHeader('Cache-Control', 'public, max-age=0, s-maxage=3600')
  response.status(200).json({
    country: String(country).trim().toUpperCase() || 'GLOBAL',
  })
}
