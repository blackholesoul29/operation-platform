async function apiFetch(method, payload = {}) {
  const url = method === 'GET'
    ? `/api/sheets?${new URLSearchParams(payload)}`
    : '/api/sheets'

  const res = await fetch(url, method === 'GET' ? {} : {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  const data = await res.json().catch(() => {
    throw new Error(`Error ${res.status}: respuesta inesperada del servidor`)
  })

  if (data.error) throw new Error(data.error)
  return data
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onerror = () => reject(new Error('Error leyendo el archivo'))
    reader.onload  = (e) => resolve(e.target.result.split(',')[1])
    reader.readAsDataURL(file)
  })
}

export const googleApi = {
  getClientes:   ()           => apiFetch('GET',  { action: 'getClientes' }),
  createCliente: (data)       => apiFetch('POST', { action: 'createCliente', data }),
  updateCliente: (id, data)   => apiFetch('POST', { action: 'updateCliente', id, data }),
  deleteCliente: (id)         => apiFetch('POST', { action: 'deleteCliente', id }),

  uploadFile: async (clientId, fieldName, file) => {
    const base64Data = await fileToBase64(file)
    return apiFetch('POST', {
      action: 'uploadFile',
      clientId,
      fieldName,
      fileName:  file.name,
      mimeType:  file.type || 'application/octet-stream',
      base64Data,
    })
  },
}
