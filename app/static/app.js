const instrumentSelect = document.querySelector('#instrumento');
const valueInput = document.querySelector('#valor');
const unitLabel = document.querySelector('#unidad');
const rangeLabel = document.querySelector('#rango');
const notice = document.querySelector('#notice');
const rows = document.querySelector('#envios');
let instruments = [];

async function request(url, options = {}) {
  const response = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...options });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail || `Error HTTP ${response.status}`);
  }
  return response.status === 204 ? null : response.json();
}

function selectedInstrument() {
  return instruments.find(item => item.id === Number(instrumentSelect.value));
}

function updateRange() {
  const instrument = selectedInstrument();
  unitLabel.textContent = instrument?.unidad || '—';
  if (!instrument) {
    rangeLabel.textContent = 'Elige un instrumento para ver el rango permitido.';
    valueInput.removeAttribute('min');
    valueInput.removeAttribute('max');
    return;
  }
  valueInput.min = instrument.valor_minimo;
  valueInput.max = instrument.valor_maximo;
  rangeLabel.textContent = `Rango permitido: ${instrument.valor_minimo} a ${instrument.valor_maximo} ${instrument.unidad}`;
}

function showNotice(message, isError = false) {
  notice.textContent = message;
  notice.className = `notice ${isError ? 'error' : 'ok'}`;
  notice.hidden = false;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
}

function statusBadge(name, value) {
  const cls = value === 'error' ? 'error' : value === 'simulado' ? 'simulado' : '';
  return `<span class="badge ${cls}">${escapeHtml(name)}: ${escapeHtml(value)}</span>`;
}

function renderShipments(shipments) {
  if (!shipments.length) {
    rows.innerHTML = '<tr><td colspan="6" class="empty">Aún no hay envíos. Crea el primero desde el formulario.</td></tr>';
    return;
  }
  rows.innerHTML = shipments.map(item => {
    const date = new Date(item.creado_en).toLocaleString('es');
    return `<tr>
      <td><strong>#${item.id}</strong><span class="date">${escapeHtml(date)}</span></td>
      <td><strong>${escapeHtml(item.instrumento.nombre)}</strong><span class="date">Etiqueta octal ${escapeHtml(item.instrumento.etiqueta_octal)}</span></td>
      <td>${escapeHtml(item.valor)} ${escapeHtml(item.instrumento.unidad)}</td>
      <td><span class="mono">0x${escapeHtml(item.codigo_arinc429)}</span></td>
      <td>${statusBadge('Serial', item.estado_serial)}${statusBadge('Audio', item.estado_audio)}</td>
      <td><div class="actions"><button class="action edit" data-id="${item.id}" title="Editar envío">Editar</button><button class="action delete" data-id="${item.id}" title="Eliminar envío">Eliminar</button></div></td>
    </tr>`;
  }).join('');
}

async function loadInstruments() {
  instruments = await request('/api/instrumentos');
  instrumentSelect.innerHTML = '<option value="">Seleccionar instrumento</option>' + instruments.map(item =>
    `<option value="${item.id}">${escapeHtml(item.nombre)} · ${escapeHtml(item.etiqueta_octal)} octal</option>`
  ).join('');
}

async function loadShipments() {
  try {
    renderShipments(await request('/api/envios'));
  } catch (error) {
    rows.innerHTML = `<tr><td colspan="6" class="empty">${escapeHtml(error.message)}</td></tr>`;
  }
}

instrumentSelect.addEventListener('change', updateRange);
document.querySelector('#refresh').addEventListener('click', loadShipments);
document.querySelector('#envio-form').addEventListener('submit', async event => {
  event.preventDefault();
  const instrument = selectedInstrument();
  if (!instrument) return showNotice('Selecciona un instrumento.', true);
  try {
    const result = await request('/api/envios', { method: 'POST', body: JSON.stringify({ instrumento_id: instrument.id, valor: Number(valueInput.value) }) });
    showNotice(`Envío #${result.id} creado · ARINC 429: 0x${result.codigo_arinc429} · Salidas: serial ${result.estado_serial}, audio ${result.estado_audio}.`);
    valueInput.value = '';
    await loadShipments();
  } catch (error) {
    showNotice(error.message, true);
  }
});

rows.addEventListener('click', async event => {
  const button = event.target.closest('button[data-id]');
  if (!button) return;
  const id = Number(button.dataset.id);
  try {
    if (button.classList.contains('delete')) {
      if (!confirm(`¿Eliminar el envío #${id}?`)) return;
      await request(`/api/envios/${id}`, { method: 'DELETE' });
      showNotice(`Envío #${id} eliminado.`);
      await loadShipments();
      return;
    }
    const item = await request(`/api/envios/${id}`);
    const instrumentId = prompt('ID del instrumento:', String(item.instrumento_id));
    if (instrumentId === null) return;
    const value = prompt(`Nuevo valor (${item.instrumento.unidad}):`, String(item.valor));
    if (value === null) return;
    const updated = await request(`/api/envios/${id}`, { method: 'PUT', body: JSON.stringify({ instrumento_id: Number(instrumentId), valor: Number(value) }) });
    showNotice(`Envío #${updated.id} actualizado. Las salidas físicas no se activaron nuevamente.`);
    await loadShipments();
  } catch (error) {
    showNotice(error.message, true);
  }
});

Promise.all([loadInstruments(), loadShipments()]).then(updateRange).catch(error => showNotice(error.message, true));
