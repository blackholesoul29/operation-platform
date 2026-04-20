import { APPS_SCRIPT_URL, API_SECRET } from './config'

function checkConfig() {
  if (!APPS_SCRIPT_URL) throw new Error('Apps Script URL no configurada. Edita src/lib/config.js')
}

async function get(params = {}) {
  checkConfig()
  const url = new URL(APPS_SCRIPT_URL)
  Object.entries({ ...params, secret: API_SECRET }).forEach(([k, v]) => url.searchParams.set(k, v))
  const res = await fetch(url.toString(), { redirect: 'follow' })
  const data = await res.json()
  if (data.error) throw new Error(data.error)
  return data
}

async function post(body) {
  checkConfig()
  // Content-Type text/plain evita el preflight CORS con Apps Script
  const res = await fetch(APPS_SCRIPT_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain' },
    body: JSON.stringify({ ...body, secret: API_SECRET }),
    redirect: 'follow',
  })
  const data = await res.json()
  if (data.error) throw new Error(data.error)
  return data
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('Error leyendo el archivo'))
    reader.onload = (e) => resolve(e.target.result.split(',')[1])
    reader.readAsDataURL(file)
  })
}

export const googleApi = {
  getClientes: () => get({ action: 'getClientes' }),

  createCliente: (data) => post({ action: 'createCliente', data }),

  updateCliente: (id, data) => post({ action: 'updateCliente', id, data }),

  deleteCliente: (id) => post({ action: 'deleteCliente', id }),

  uploadFile: async (clientId, fieldName, file) => {
    const base64Data = await fileToBase64(file)
    return post({
      action: 'uploadFile',
      clientId,
      fieldName,
      fileName: file.name,
      mimeType: file.type || 'application/octet-stream',
      base64Data,
    })
  },
}
