export const config = {
  api: { bodyParser: { sizeLimit: '10mb' } },
  maxDuration: 30,
}

export default async function handler(req, res) {
  const SCRIPT_URL = process.env.APPS_SCRIPT_URL
  const SECRET     = process.env.API_SECRET

  res.setHeader('Access-Control-Allow-Origin', '*')
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type')
  if (req.method === 'OPTIONS') return res.status(200).end()

  if (!SCRIPT_URL) {
    return res.status(500).json({
      error: 'APPS_SCRIPT_URL no configurado en Vercel. Agrégala en Settings → Environment Variables.',
    })
  }

  try {
    let scriptRes

    if (req.method === 'GET') {
      const params = new URLSearchParams({ ...req.query, secret: SECRET })
      scriptRes = await fetch(`${SCRIPT_URL}?${params}`, { redirect: 'follow' })
    } else if (req.method === 'POST') {
      const body = req.body || {}
      scriptRes = await fetch(SCRIPT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'text/plain' },
        body: JSON.stringify({ ...body, secret: SECRET }),
        redirect: 'follow',
      })
    } else {
      return res.status(405).json({ error: 'Método no permitido' })
    }

    if (!scriptRes.ok) {
      const text = await scriptRes.text().catch(() => '')
      // Si el script redirige a login de Google → acceso restringido
      if (text.includes('accounts.google') || text.includes('SignIn')) {
        return res.status(403).json({
          error: 'El Apps Script requiere autenticación. Redespliégalo con acceso "Cualquier usuario".',
        })
      }
      return res.status(scriptRes.status).json({ error: `Apps Script HTTP ${scriptRes.status}` })
    }

    const data = await scriptRes.json()
    return res.json(data)
  } catch (e) {
    return res.status(500).json({ error: e.message || 'Error de conexión con Apps Script' })
  }
}
