# app.py
import os
import json
from flask import Flask, request, send_from_directory, jsonify, render_template_string, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
FLAGS_DIR = os.path.join(BASE_DIR, "static", "flags")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(FLAGS_DIR, exist_ok=True)

CITIES_FILE = os.path.join(DATA_DIR, "cities.json")        # master list (upload or edit)
REMOVED_FILE = os.path.join(DATA_DIR, "removed.json")      # persisted removed cities

# seed with sample file if not exists (small sample)
if not os.path.exists(CITIES_FILE):
    sample = [
        {"name": "Belo Horizonte", "state": "MG"},
        {"name": "Uberlândia", "state": "MG"},
        {"name": "Divinópolis", "state": "MG"},
        {"name": "São Paulo", "state": "SP"},
        {"name": "Campinas", "state": "SP"},
        {"name": "Santos", "state": "SP"},
        {"name": "Rio de Janeiro", "state": "RJ"},
        {"name": "Niterói", "state": "RJ"},
        {"name": "Curitiba", "state": "PR"},
        {"name": "Londrina", "state": "PR"}
    ]
    with open(CITIES_FILE, "w", encoding="utf-8") as f:
        json.dump(sample, f, ensure_ascii=False, indent=2)

if not os.path.exists(REMOVED_FILE):
    with open(REMOVED_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)


@app.route("/")
def index():
    # Single-file HTML/JS/CSS template (responsive)
    return render_template_string("""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width,initial-scale=1" />
<title>Roleta de Cidades - Brasil</title>
<style>
    :root{
        --bg:#0f1724;
        --card:#0b1220;
        --accent:#06b6d4;
        --muted:#94a3b8;
    }
    html,body{height:100%;margin:0;font-family:Inter,system-ui,Segoe UI,Roboto,"Helvetica Neue",Arial;background:linear-gradient(180deg,#071024 0%, #0b1b2b 100%);color:#e6eef6}
    .wrap{max-width:1200px;margin:24px auto;padding:16px}
    header{display:flex;gap:12px;align-items:center;justify-content:space-between;margin-bottom:12px}
    h1{font-size:20px;margin:0}
    .controls{display:flex;gap:8px;flex-wrap:wrap}
    .card{background:rgba(255,255,255,0.03);padding:12px;border-radius:12px;box-shadow:0 6px 24px rgba(2,6,23,0.6)}
    .big{display:flex;gap:16px;flex-wrap:wrap}
    .left{flex:1;min-width:320px}
    .right{width:420px;min-width:280px}
    canvas{width:100%;height:auto;border-radius:12px;background:#081226}
    label{font-size:13px;color:var(--muted);display:block;margin-bottom:6px}
    input[type="number"], select{width:100%;padding:8px;border-radius:8px;border:1px solid rgba(255,255,255,0.06);background:transparent;color:inherit}
    .btn{background:var(--accent);color:#042028;padding:8px 12px;border-radius:10px;border:0;cursor:pointer;font-weight:600}
    .btn-ghost{background:transparent;border:1px solid rgba(255,255,255,0.06);color:inherit;padding:8px 12px;border-radius:10px}
    .row{display:flex;gap:8px}
    .small{font-size:13px;color:var(--muted)}
    .removed-list{max-height:280px;overflow:auto;margin-top:12px;padding:8px;border-radius:8px;border:1px dashed rgba(255,255,255,0.03);background:linear-gradient(180deg, rgba(255,255,255,0.01), rgba(255,255,255,0.00))}
    .removed-item{display:flex;align-items:center;gap:8px;padding:6px;border-radius:8px}
    .flag-thumb{width:36px;height:24px;border-radius:4px;flex-shrink:0;background:#0a1220;display:flex;align-items:center;justify-content:center;color:var(--muted);font-weight:700}
    .state-tag{font-size:12px;padding:4px 6px;border-radius:6px;background:rgba(255,255,255,0.02);margin-left:auto}
    .settings{display:grid;grid-template-columns:1fr 1fr;gap:8px}
    @media (max-width:900px){ .big{flex-direction:column} .right{width:100%} }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>Roleta de Cidades do Brasil</h1>
      <div class="small">Agrupada por estados — cada setor usa a bandeira do estado (se disponível).</div>
    </div>
    <div class="controls">
      <button class="btn" id="spinBtn">Girar</button>
      <button class="btn-ghost" id="multiSpinBtn">Girar várias vezes</button>
      <button class="btn-ghost" id="resetRemoved">Resetar removidos</button>
    </div>
  </header>

  <div class="big">
    <div class="left card">
      <canvas id="wheel" width="800" height="800"></canvas>
      <div style="display:flex;gap:12px;margin-top:8px;align-items:center">
        <div style="flex:1">
          <label>Remover por rodada</label>
          <input type="number" id="removeCount" min="1" max="100" value="10" />
        </div>
        <div style="width:140px">
          <label>Velocidade (0.1-2)</label>
          <input type="number" id="initSpeed" min="0.1" max="3" step="0.1" value="1.2"/>
        </div>
        <div style="width:110px">
          <label>Física</label>
          <select id="physicsToggle">
            <option value="on">Ativada</option>
            <option value="off">Desativada</option>
          </select>
        </div>
      </div>
      <div style="display:flex;gap:8px;margin-top:10px;align-items:center;flex-wrap:wrap">
        <label style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="soundToggle" checked/> Som</label>
        <label style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="autoRemove" /> Remover automaticamente ao final do giro</label>
        <label style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="confirmRemove" /> Pedir confirmação antes de remover</label>
      </div>
      <div style="margin-top:10px" class="small">Observação: para usar bandeiras dos estados, coloque imagens PNG em <code>static/flags/UF.png</code> (ex.: <code>MG.png</code>, <code>SP.png</code>)</div>
    </div>

    <div class="right card">
      <div>
        <label>Carregar arquivo de cidades (JSON array de {name,state})</label>
        <form id="uploadForm" enctype="multipart/form-data">
          <input type="file" id="fileInput" accept=".json" />
          <div style="margin-top:8px;display:flex;gap:8px">
            <button class="btn" type="button" id="uploadBtn">Upload</button>
            <button class="btn-ghost" id="downloadCurrent">Baixar arquivo atual</button>
          </div>
        </form>
      </div>

      <div style="margin-top:12px">
        <label>Estatísticas</label>
        <div style="display:flex;gap:8px;margin-top:8px">
          <div class="card" style="flex:1;padding:8px">
            <div class="small">Cidades na roleta</div>
            <div id="countActive" style="font-size:18px;font-weight:700">0</div>
          </div>
          <div class="card" style="flex:1;padding:8px">
            <div class="small">Cidades removidas</div>
            <div id="countRemoved" style="font-size:18px;font-weight:700">0</div>
          </div>
        </div>
      </div>

      <div style="margin-top:12px">
        <label>Cidades removidas</label>
        <div class="removed-list" id="removedList"></div>
      </div>
    </div>
  </div>
</div>

<script>
/* Core idea:
 - fetch cities (master) and removed list -> active = master - removed
 - build sectors grouped by state: for each state collect its cities and make consecutive sectors
 - draw wheel on canvas; for state sector we attempt to load /static/flags/UF.png as pattern
 - spin physics: either "physics on" (deceleration) or immediate easing
 - when pointer stops, compute which cities to remove (N) starting from stopped sector and continuing clockwise
 - removed saved to /api/remove
 - play tick sound on every pass over sector
*/

// Helpers & settings
const API = {
  cities:'/api/cities',
  removed:'/api/removed',
  remove:'/api/remove',
  upload:'/api/upload',
  download:'/api/download'
};
let settings = {
  removeCount: parseInt(document.getElementById('removeCount').value),
  sound: document.getElementById('soundToggle').checked,
  physics: document.getElementById('physicsToggle').value === 'on',
  autoRemove: document.getElementById('autoRemove').checked,
  confirmRemove: document.getElementById('confirmRemove').checked,
  initSpeed: parseFloat(document.getElementById('initSpeed').value)
};

const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
let W = canvas.width, H = canvas.height, cx = W/2, cy = H/2, radius = Math.min(W,H)/2 - 30;
const spinBtn = document.getElementById('spinBtn');
const multiSpinBtn = document.getElementById('multiSpinBtn');

let masterCities = [];
let removed = [];
let active = [];
let sectors = []; // {state, cities:[...], startAngle, endAngle, color, flagImg}
let spinState = {angle:0, angularVel:0, spinning:false};
let tickSoundEnabled = settings.sound;
let lastTickIndex = -1;

// generate deterministic color from state UF
function colorFromStr(s){
  let h = 0;
  for(let i=0;i<s.length;i++) h = (h*31 + s.charCodeAt(i)) % 360;
  return `hsl(${h}, 60%, 45%)`;
}

// fetch initial data
async function loadData(){
  let r = await fetch(API.cities);
  masterCities = await r.json();
  let r2 = await fetch(API.removed);
  removed = await r2.json();
  rebuildActive();
  drawWheel();
  renderRemovedList();
}
function rebuildActive(){
  const removedKeys = new Set(removed.map(x => (x.name + '||' + x.state)));
  active = masterCities.filter(c => !removedKeys.has(c.name + '||' + c.state));
  buildSectors();
  document.getElementById('countActive').innerText = active.length;
  document.getElementById('countRemoved').innerText = removed.length;
}
function buildSectors(){
  // group by state, keep cities order as in master for predictability
  const map = {};
  for(const c of active){
    if(!map[c.state]) map[c.state] = [];
    map[c.state].push(c);
  }
  sectors = [];
  for(const state of Object.keys(map)){
    sectors.push({state, cities: map[state]});
  }
  // compute angles proportional to number of cities
  const totalCities = active.length || 1;
  let angle = -Math.PI/2; // start top
  for(const s of sectors){
    const fraction = s.cities.length / totalCities;
    s.startAngle = angle;
    s.endAngle = angle + fraction * Math.PI*2;
    s.color = colorFromStr(s.state);
    s.midAngle = (s.startAngle + s.endAngle) / 2;
    angle = s.endAngle;
    // try to load flag image
    s.flag = new Image();
    s.flag.src = '/static/flags/' + s.state.toUpperCase() + '.png';
    s.flagLoaded = false;
    s.flag.onload = ()=>{ s.flagLoaded = true; drawWheel(); }
    s.flag.onerror = ()=>{ s.flagLoaded = false; }
  }
}

// Draw wheel
function drawWheel(){
  ctx.clearRect(0,0,W,H);
  // outer circle style
  ctx.save();
  ctx.translate(cx,cy);
  // sectors: but we need to split sectors further to display each city label if desired.
  // We'll draw by state-sector but internally show city names as small ticks.
  for(const s of sectors){
    // fill sector
    ctx.beginPath();
    ctx.moveTo(0,0);
    ctx.arc(0,0, radius, s.startAngle, s.endAngle);
    ctx.closePath();
    // if flag loaded, create pattern
    if(s.flagLoaded){
      // pattern drawing: draw image as pattern clipped into sector
      ctx.save();
      ctx.clip();
      // rotate canvas so sector fits nicely - draw image sized to radius*2
      // draw the flag centered
      const img = s.flag;
      // draw it so it covers the circle
      ctx.drawImage(img, -radius, -radius, radius*2, radius*2);
      ctx.restore();
    }else{
      ctx.fillStyle = s.color;
      ctx.fill();
    }
    // stroke
    ctx.strokeStyle = 'rgba(0,0,0,0.3)';
    ctx.lineWidth = 2;
    ctx.stroke();
    // small text: state code on outer edge
    const mid = s.midAngle;
    const tx = Math.cos(mid) * (radius*0.72);
    const ty = Math.sin(mid) * (radius*0.72);
    ctx.save();
    ctx.translate(tx,ty);
    ctx.rotate(mid + Math.PI/2);
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 16px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText(s.state.toUpperCase(), 0, 0);
    ctx.restore();

    // draw little city ticks inside sector
    const cityCount = s.cities.length;
    for(let i=0;i<cityCount;i++){
      const frac = i / cityCount;
      const angle = s.startAngle + (s.endAngle - s.startAngle) * (i + 0.5) / cityCount;
      const rx = Math.cos(angle) * (radius*0.92);
      const ry = Math.sin(angle) * (radius*0.92);
      ctx.beginPath();
      ctx.arc(rx, ry, 3, 0, Math.PI*2);
      ctx.fillStyle = 'rgba(255,255,255,0.9)';
      ctx.fill();
    }
  }

  // center circle
  ctx.beginPath();
  ctx.arc(0,0,60,0,Math.PI*2);
  ctx.fillStyle = 'rgba(0,0,0,0.6)';
  ctx.fill();
  ctx.lineWidth = 2;
  ctx.strokeStyle = 'rgba(255,255,255,0.06)';
  ctx.stroke();

  // pointer (top)
  ctx.restore();
  // draw pointer triangle
  ctx.save();
  ctx.translate(cx, cy - radius - 10);
  ctx.beginPath();
  ctx.moveTo(0, -10);
  ctx.lineTo(14, 18);
  ctx.lineTo(-14, 18);
  ctx.closePath();
  ctx.fillStyle = "#fffb";
  ctx.fill();
  ctx.restore();

  // rotate wheel by current spinState.angle
  // Actually we draw above unrotated; to show rotation we should rotate canvas before render.
  // Simpler approach: render wheel to offscreen canvas and draw rotated here.
}

// We'll use an offscreen canvas render to support rotation animation
const off = document.createElement('canvas');
off.width = W; off.height = H;
const octx = off.getContext('2d');
function renderOffscreen(){
  octx.clearRect(0,0,W,H);
  octx.save();
  octx.translate(cx,cy);
  const r = radius;
  for(const s of sectors){
    octx.beginPath();
    octx.moveTo(0,0);
    octx.arc(0,0, r, s.startAngle, s.endAngle);
    octx.closePath();
    if(s.flagLoaded){
      // clip and draw image
      octx.save();
      octx.clip();
      octx.drawImage(s.flag, -r, -r, r*2, r*2);
      octx.restore();
    }else{
      octx.fillStyle = s.color;
      octx.fill();
    }
    octx.strokeStyle = 'rgba(0,0,0,0.3)';
    octx.lineWidth = 2;
    octx.stroke();

    const mid = s.midAngle;
    const tx = Math.cos(mid) * (r*0.72);
    const ty = Math.sin(mid) * (r*0.72);
    octx.save();
    octx.translate(tx,ty);
    octx.rotate(mid + Math.PI/2);
    octx.fillStyle = '#fff';
    octx.font = 'bold 16px sans-serif';
    octx.textAlign = 'center';
    octx.fillText(s.state.toUpperCase(), 0, 0);
    octx.restore();

    // city ticks
    const cityCount = s.cities.length;
    for(let i=0;i<cityCount;i++){
      const angle = s.startAngle + (s.endAngle - s.startAngle) * (i + 0.5) / cityCount;
      const rx = Math.cos(angle) * (r*0.92);
      const ry = Math.sin(angle) * (r*0.92);
      octx.beginPath();
      octx.arc(rx, ry, 3, 0, Math.PI*2);
      octx.fillStyle = 'rgba(255,255,255,0.9)';
      octx.fill();
    }
  }
  // center disc
  octx.beginPath();
  octx.arc(0,0,60,0,Math.PI*2);
  octx.fillStyle = 'rgba(0,0,0,0.6)';
  octx.fill();
  octx.restore();
}
renderOffscreen();

// main animation
function animate(){
  requestAnimationFrame(animate);
  // physics
  if(spinState.spinning){
    if(settings.physics){
      // angularVel decreases
      spinState.angularVel *= 0.995; // friction factor
      if(Math.abs(spinState.angularVel) < 0.0005) {
        spinState.spinning = false;
        spinState.angularVel = 0;
        onSpinStop();
      }
      spinState.angle += spinState.angularVel;
    }else{
      // non-physics easing: slowly reduce until stop
      spinState.angularVel *= 0.98;
      spinState.angle += spinState.angularVel;
      if(Math.abs(spinState.angularVel) < 0.0005){ spinState.spinning=false; onSpinStop(); }
    }
    handleTicks();
  }
  // draw rotated offscreen
  ctx.clearRect(0,0,W,H);
  ctx.save();
  ctx.translate(cx,cy);
  ctx.rotate(spinState.angle);
  ctx.drawImage(off, -cx, -cy);
  ctx.restore();
  // draw pointer
  ctx.save();
  ctx.translate(cx, cy - radius - 10);
  ctx.beginPath();
  ctx.moveTo(0, -10);
  ctx.lineTo(14, 18);
  ctx.lineTo(-14, 18);
  ctx.closePath();
  ctx.fillStyle = "#fff";
  ctx.fill();
  ctx.restore();
}
requestAnimationFrame(animate);

// tick sound using WebAudio
let audioCtx = null;
function tick(){
  if(!tickSoundEnabled) return;
  if(!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
  const o = audioCtx.createOscillator();
  const g = audioCtx.createGain();
  o.type = 'square';
  o.frequency.setValueAtTime(1200, audioCtx.currentTime);
  g.gain.setValueAtTime(0.0001, audioCtx.currentTime);
  g.gain.exponentialRampToValueAtTime(0.2, audioCtx.currentTime + 0.001);
  g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + 0.07);
  o.connect(g); g.connect(audioCtx.destination);
  o.start();
  o.stop(audioCtx.currentTime + 0.08);
}

// tick handling: determine which sector pointer passes over
function handleTicks(){
  if(sectors.length === 0) return;
  // pointer at top corresponds to global angle = -spinState.angle + (-PI/2)
  // find the sector index at angle = -spinState.angle + (-PI/2)
  const pointerAngle = -spinState.angle - Math.PI/2;
  // normalize
  let a = pointerAngle;
  while(a < -Math.PI) a += Math.PI*2;
  while(a > Math.PI) a -= Math.PI*2;
  // find sector by mid angle range
  let idx = -1;
  for(let i=0;i<sectors.length;i++){
    const s = sectors[i];
    const start = normalizeAngle(s.startAngle);
    const end = normalizeAngle(s.endAngle);
    if(angleInRange(pointerAngle, s.startAngle, s.endAngle)){ idx = i; break; }
  }
  if(idx !== lastTickIndex){
    lastTickIndex = idx;
    tick();
  }
}

function normalizeAngle(x){
  // return in -pi..pi
  let a = x;
  while(a < -Math.PI) a += Math.PI*2;
  while(a > Math.PI) a -= Math.PI*2;
  return a;
}
function angleInRange(a, start, end){
  // a, start, end in radians; start<end potentially >2pi span
  let two = Math.PI*2;
  let an = (a + two) % two;
  let sn = (start + two) % two;
  let en = (end + two) % two;
  if(sn < en) return an >= sn && an < en;
  return an >= sn || an < en;
}

// spin controls
spinBtn.addEventListener('click', ()=>startSpinOnce());
multiSpinBtn.addEventListener('click', ()=>multiSpinPrompt());

function startSpinOnce(){
  if(active.length === 0){ alert('Não há cidades suficientes na roleta.'); return; }
  settings.removeCount = parseInt(document.getElementById('removeCount').value) || 1;
  settings.sound = document.getElementById('soundToggle').checked;
  settings.physics = document.getElementById('physicsToggle').value === 'on';
  tickSoundEnabled = settings.sound;
  // initial angularVel: based on initSpeed
  const v = parseFloat(document.getElementById('initSpeed').value) || 1.2;
  spinState.angularVel = v * 0.3; // tweak
  spinState.spinning = true;
}

function multiSpinPrompt(){
  let times = parseInt(prompt('Quantas vezes deseja girar (executará em sequência):', '3') || '0');
  if(!times || times <= 0) return;
  runMultipleSpins(times);
}

async function runMultipleSpins(times){
  for(let i=0;i<times;i++){
    startSpinOnce();
    // wait for spin to stop
    await waitForStop();
    // if autoRemove remove after each spin
    if(settings.autoRemove){
      await removeTopN();
    }
  }
}

// wait for spin state to finish
function waitForStop(){
  return new Promise(resolve=>{
    const id = setInterval(()=>{
      if(!spinState.spinning){
        clearInterval(id);
        resolve();
      }
    }, 120);
  });
}

function onSpinStop(){
  // compute pointer sector and the list of cities to remove (settings.removeCount)
  if(active.length === 0) return;
  getCurrentPointerSector().then(({sectorIndex, localCityIndex})=>{
    // choose N cities: start from that sector and city index, move clockwise across sectors and their cities
    const N = parseInt(document.getElementById('removeCount').value) || 1;
    const toRemove = [];
    let si = sectorIndex;
    let ci = localCityIndex;
    let collected = 0;
    while(collected < N && active.length > 0){
      const s = sectors[si];
      if(s && s.cities[ci]){
        toRemove.push(s.cities[ci]);
        collected++;
      }
      // increment city index
      ci++;
      if(!s || ci >= (s ? s.cities.length : 0)){
        // move to next sector
        si = (si + 1) % sectors.length;
        ci = 0;
        // safeguard: if sectors length zero -> break
        if(sectors.length === 0) break;
      }
      // safeguard infinite loop
      if(toRemove.length > active.length) break;
    }
    // confirm if needed
    (document.getElementById('confirmRemove').checked ? confirmRemoval(toRemove) : Promise.resolve(true))
      .then(ok=>{
        if(ok){
          if(document.getElementById('autoRemove').checked){
            postRemove(toRemove);
          }else{
            // show a quick dialog listing toRemove and ask if save
            if(confirm(`Remover as seguintes cidades (${toRemove.length})?\n` + toRemove.map(c=>c.name + ' - ' + c.state).join('\\n'))){
              postRemove(toRemove);
            }
          }
        }
    });
  });
}

function confirmRemoval(list){
  return new Promise(resolve=>{
    resolve(confirm('Confirmar remoção de ' + list.length + ' cidades?'));
  });
}

async function getCurrentPointerSector(){
  // pointer angle = -spinState.angle - PI/2
  const pointerAngle = -spinState.angle - Math.PI/2;
  // find sector and local city index inside sector
  let sectorIndex = 0;
  for(let i=0;i<sectors.length;i++){
    if(angleInRange(pointerAngle, sectors[i].startAngle, sectors[i].endAngle)){
      sectorIndex = i; break;
    }
  }
  // within the sector, determine approximate city index by fraction
  const s = sectors[sectorIndex];
  const span = sectors[sectorIndex].endAngle - sectors[sectorIndex].startAngle;
  const rel = (pointerAngle - sectors[sectorIndex].startAngle) / span;
  const localIdx = Math.floor(((rel + 1) % 1) * s.cities.length);
  return {sectorIndex, localCityIndex: localIdx};
}

// post remove to server
async function postRemove(list){
  if(list.length === 0) return;
  const res = await fetch(API.remove, {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({items:list})
  });
  if(res.ok){
    const data = await res.json();
    removed = data.removed;
    rebuildActive();
    renderRemovedList();
    renderOffscreen();
    alert('Removidas ' + list.length + ' cidades.');
  }else{
    alert('Erro ao salvar remoções.');
  }
}

async function removeTopN(){
  // compute top sector at pointer and remove N cities
  const {sectorIndex, localCityIndex} = await getCurrentPointerSector();
  const N = parseInt(document.getElementById('removeCount').value) || 1;
  const toRemove = [];
  let si = sectorIndex; let ci = localCityIndex;
  let collected = 0;
  while(collected < N && active.length > 0){
    const s = sectors[si];
    if(s && s.cities[ci]){
      toRemove.push(s.cities[ci]);
      collected++;
    }
    ci++;
    if(!s || ci >= (s ? s.cities.length : 0)){
      si = (si + 1) % sectors.length;
      ci = 0;
    }
    if(toRemove.length > active.length) break;
  }
  await postRemove(toRemove);
}

function renderRemovedList(){
  const container = document.getElementById('removedList');
  container.innerHTML = '';
  for(const r of removed.slice().reverse()){
    const div = document.createElement('div');
    div.className = 'removed-item';
    const thumb = document.createElement('div');
    thumb.className = 'flag-thumb';
    // try to show flag img
    const img = document.createElement('img');
    img.src = '/static/flags/' + r.state.toUpperCase() + '.png';
    img.style.width = '100%'; img.style.height='100%'; img.style.objectFit='cover';
    img.onerror = ()=>{ thumb.innerText = r.state.toUpperCase(); };
    img.onload = ()=>{ thumb.innerHTML=''; thumb.appendChild(img); }
    thumb.appendChild(img);
    const txt = document.createElement('div');
    txt.innerHTML = `<div style="font-weight:700">${r.name}</div><div class="small">${r.state}</div>`;
    const tag = document.createElement('div');
    tag.className = 'state-tag';
    tag.innerText = r.state.toUpperCase();
    div.appendChild(thumb);
    div.appendChild(txt);
    div.appendChild(tag);
    container.appendChild(div);
  }
}

// upload form
document.getElementById('uploadBtn').addEventListener('click', async ()=>{
  const fi = document.getElementById('fileInput');
  if(!fi.files || fi.files.length === 0){ alert('Escolha um arquivo .json com as cidades.'); return; }
  const f = fi.files[0];
  const fd = new FormData();
  fd.append('file', f, f.name);
  const resp = await fetch(API.upload, {method:'POST', body:fd});
  if(resp.ok){
    alert('Upload realizado e cidades atualizadas.');
    await loadData();
  }else{
    alert('Erro no upload.');
  }
});

// download current
document.getElementById('downloadCurrent').addEventListener('click', ()=>{
  window.location = API.download;
});

// reset removed
document.getElementById('resetRemoved').addEventListener('click', async ()=>{
  if(!confirm('Resetar lista de removidos? Isso restaurará todas as cidades na roleta.')) return;
  const resp = await fetch('/api/reset_removed', {method:'POST'});
  if(resp.ok){ await loadData(); alert('Reset feito.'); } else alert('Erro ao resetar.');
});

// settings change handlers
document.getElementById('soundToggle').addEventListener('change', (e)=>{ tickSoundEnabled = e.target.checked; });
document.getElementById('physicsToggle').addEventListener('change', (e)=>{ settings.physics = e.target.value === 'on'; });
document.getElementById('removeCount').addEventListener('change', ()=>{ settings.removeCount = parseInt(document.getElementById('removeCount').value) || 1; });
document.getElementById('initSpeed').addEventListener('change', ()=>{ settings.initSpeed = parseFloat(document.getElementById('initSpeed').value) || 1.2; });

loadData();
</script>

</body>
</html>""")

# API endpoints
@app.route("/api/cities")
def api_cities():
    with open(CITIES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/removed")
def api_removed():
    with open(REMOVED_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route("/api/remove", methods=["POST"])
def api_remove():
    payload = request.get_json() or {}
    items = payload.get("items", [])
    # Load existing removed
    with open(REMOVED_FILE, "r", encoding="utf-8") as f:
        removed = json.load(f)
    # Add new items (avoid duplicates)
    existing = set((r["name"], r["state"]) for r in removed)
    for it in items:
        key = (it["name"], it["state"])
        if key not in existing:
            removed.append({"name": it["name"], "state": it["state"]})
            existing.add(key)
    with open(REMOVED_FILE, "w", encoding="utf-8") as f:
        json.dump(removed, f, ensure_ascii=False, indent=2)
    return jsonify({"status":"ok", "removed": removed})

@app.route("/api/upload", methods=["POST"])
def api_upload():
    # Accept a JSON file upload and replace cities.json
    if "file" not in request.files:
        return "no file", 400
    f = request.files["file"]
    filename = secure_filename(f.filename)
    content = f.read().decode("utf-8")
    try:
        arr = json.loads(content)
        if not isinstance(arr, list):
            return "invalid json structure", 400
        # validate items minimally
        clean = []
        for it in arr:
            if isinstance(it, dict) and "name" in it and "state" in it:
                clean.append({"name": str(it["name"]), "state": str(it["state"]).upper()})
        with open(CITIES_FILE, "w", encoding="utf-8") as ff:
            json.dump(clean, ff, ensure_ascii=False, indent=2)
        return "ok", 200
    except Exception as e:
        return f"parse error: {e}", 400

@app.route("/api/download")
def api_download():
    return send_from_directory(DATA_DIR, "cities.json", as_attachment=True)

@app.route("/api/reset_removed", methods=["POST"])
def api_reset_removed():
    with open(REMOVED_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=2)
    return jsonify({"status":"ok"})

# static flags will be served automatically by Flask from /static/flags/<UF>.png
# run
if __name__ == "__main__":
    app.run(debug=True, port=5000)
