// ============================================================
// PLATAFORMA OPERACIONES — Apps Script Backend
// Spreadsheet: https://docs.google.com/spreadsheets/d/1gQjo1VUKBYv3SIxAHj-tRx9RdcRe0ItzrbduiF6o2G0
// Carpeta raíz Drive: https://drive.google.com/drive/folders/1Gc-SuTyo5rAKGXUU-X1qxHoMtI7MFOmk
// ============================================================

const SPREADSHEET_ID   = '1gQjo1VUKBYv3SIxAHj-tRx9RdcRe0ItzrbduiF6o2G0';
const PARENT_FOLDER_ID = '1Gc-SuTyo5rAKGXUU-X1qxHoMtI7MFOmk';
const SHEET_NAME       = 'Clientes';

// Cambia esta clave por una cadena segura y ponla también en config.js
const API_SECRET = 'unergy-ops-2025';

// Orden de columnas — NO cambiar sin actualizar el índice COLS
const COLS = {
  id:                    0,
  nombre_comercial:      1,
  razon_social_url:      2,
  nit_url:               3,
  rut_url:               4,
  camara_comercio_url:   5,
  nda_url:               6,
  servicios:             7,
  oferta_url:            8,
  cert_bancaria_url:     9,
  estado:                10,
  created_at:            11,
  updated_at:            12,
  folder_id:             13,
  folder_url:            14,
  // Contrato del servicio
  contrato_url:          15,
  fecha_inicio:          16,
  fecha_fin:             17,
  renovacion_automatica: 18,
  periodo_renovacion:    19,
};

const HEADERS = Object.keys(COLS);
const NUM_COLS = HEADERS.length;

// ─── Helpers ────────────────────────────────────────────────

function getSheet() {
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = ss.insertSheet(SHEET_NAME);
    sheet.getRange(1, 1, 1, NUM_COLS).setValues([HEADERS]);
    sheet.setFrozenRows(1);
    sheet.getRange(1, 1, 1, NUM_COLS).setFontWeight('bold');
  }
  return sheet;
}

function rowToObj(row) {
  const obj = {};
  HEADERS.forEach((h, i) => { obj[h] = row[i] !== undefined ? String(row[i]) : ''; });
  obj.servicios = obj.servicios ? obj.servicios.split(',').filter(Boolean) : [];
  return obj;
}

function respond(data) {
  return ContentService
    .createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

// ─── Endpoints ──────────────────────────────────────────────

function checkAuth(secret) {
  if (secret !== API_SECRET) throw new Error('No autorizado');
}

function doGet(e) {
  try {
    checkAuth(e.parameter && e.parameter.secret);
    const action = e.parameter.action || 'getClientes';
    if (action === 'getClientes') return respond(getAllClientes());
    if (action === 'getCliente')  return respond(getCliente(e.parameter.id));
    return respond({ error: 'Acción desconocida' });
  } catch(err) {
    return respond({ error: err.message });
  }
}

function doPost(e) {
  try {
    const body = JSON.parse(e.postData.contents);
    checkAuth(body.secret);
    switch (body.action) {
      case 'createCliente': return respond(createCliente(body.data));
      case 'updateCliente': return respond(updateCliente(body.id, body.data));
      case 'deleteCliente': return respond(deleteCliente(body.id));
      case 'uploadFile':    return respond(uploadFile(body));
      default:              return respond({ error: 'Acción desconocida: ' + body.action });
    }
  } catch(err) {
    return respond({ error: err.message });
  }
}

// ─── Operaciones ────────────────────────────────────────────

function getAllClientes() {
  const sheet = getSheet();
  const data  = sheet.getDataRange().getValues();
  if (data.length <= 1) return [];
  return data.slice(1).map(rowToObj);
}

function getCliente(id) {
  const found = getAllClientes().find(c => c.id === id);
  return found || { error: 'No encontrado' };
}

function createCliente(data) {
  const sheet  = getSheet();
  const id     = Utilities.getUuid();
  const now    = new Date().toISOString();

  // Crear carpeta en Drive
  const parent = DriveApp.getFolderById(PARENT_FOLDER_ID);
  const folder = parent.createFolder(data.nombre_comercial || 'Sin nombre - ' + id);
  folder.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

  const row = new Array(NUM_COLS).fill('');
  row[COLS.id]               = id;
  row[COLS.nombre_comercial] = data.nombre_comercial || '';
  row[COLS.servicios]        = Array.isArray(data.servicios) ? data.servicios.join(',') : '';
  row[COLS.estado]           = data.estado || 'Originación';
  row[COLS.created_at]       = now;
  row[COLS.updated_at]       = now;
  row[COLS.folder_id]        = folder.getId();
  row[COLS.folder_url]       = folder.getUrl();

  sheet.appendRow(row);

  return {
    id,
    nombre_comercial: data.nombre_comercial,
    estado:           row[COLS.estado],
    folder_id:        folder.getId(),
    folder_url:       folder.getUrl(),
    created_at:       now,
  };
}

function updateCliente(id, data) {
  const sheet   = getSheet();
  const allData = sheet.getDataRange().getValues();

  for (let i = 1; i < allData.length; i++) {
    if (allData[i][COLS.id] !== id) continue;
    const rowNum = i + 1;
    Object.keys(data).forEach(key => {
      if (COLS[key] === undefined) return;
      let val = data[key];
      if (Array.isArray(val)) val = val.join(',');
      sheet.getRange(rowNum, COLS[key] + 1).setValue(val || '');
    });
    sheet.getRange(rowNum, COLS.updated_at + 1).setValue(new Date().toISOString());
    return { success: true };
  }
  return { error: 'Cliente no encontrado' };
}

function deleteCliente(id) {
  const sheet   = getSheet();
  const allData = sheet.getDataRange().getValues();

  for (let i = 1; i < allData.length; i++) {
    if (allData[i][COLS.id] !== id) continue;
    const folderId = allData[i][COLS.folder_id];
    if (folderId) {
      try { DriveApp.getFolderById(folderId).setTrashed(true); } catch(e) {}
    }
    sheet.deleteRow(i + 1);
    return { success: true };
  }
  return { error: 'Cliente no encontrado' };
}

function uploadFile(body) {
  const { clientId, fieldName, fileName, mimeType, base64Data } = body;

  const sheet   = getSheet();
  const allData = sheet.getDataRange().getValues();

  let folderId = null, rowNum = null;
  for (let i = 1; i < allData.length; i++) {
    if (allData[i][COLS.id] !== clientId) continue;
    folderId = allData[i][COLS.folder_id];
    rowNum   = i + 1;
    break;
  }

  if (!folderId) return { error: 'Cliente o carpeta no encontrada' };

  const folder = DriveApp.getFolderById(folderId);

  // Eliminar versión anterior del mismo campo
  const existing = folder.getFilesByName('[' + fieldName + ']');
  while (existing.hasNext()) existing.next().setTrashed(true);

  const bytes = Utilities.base64Decode(base64Data);
  const blob  = Utilities.newBlob(bytes, mimeType || 'application/octet-stream', '[' + fieldName + '] ' + fileName);
  const file  = folder.createFile(blob);
  file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

  const fileUrl  = file.getUrl();
  const colKey   = fieldName + '_url';

  if (COLS[colKey] !== undefined) {
    sheet.getRange(rowNum, COLS[colKey] + 1).setValue(fileUrl);
    sheet.getRange(rowNum, COLS.updated_at + 1).setValue(new Date().toISOString());
  }

  return { fileUrl, fileId: file.getId(), fileName: file.getName() };
}
