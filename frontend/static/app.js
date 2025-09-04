async function init() {
  const res = await fetch('/api/videos');
  const files = await res.json();
  const sel = document.getElementById('videos');
  const meta = document.getElementById('meta');
  const mode = document.getElementById('mode');
  opt = document.createElement('option'); opt.textContent = "Normal"; mode.appendChild(opt);
  opt = document.createElement('option'); opt.textContent = "Movement"; mode.appendChild(opt);
  const player = document.getElementById('player');
  sel.innerHTML = '';
  if (!files.length) {
    sel.innerHTML = '<option>(Put .mp4 files in ./media)</option>';
    meta.textContent = '';
    return;
  }
  for (const f of files) {
    const opt = document.createElement('option');
    opt.value = f.vid; opt.textContent = `${f.name}`; sel.appendChild(opt);
  }
  function playCurrent() {
    const v = sel.value;
    const prev_time = player.currentTime;
    const paused = player.paused;
    player.src = `/stream?vid=${v}&mode=${mode.value.toLowerCase()}`;
    player.currentTime = prev_time;
    player.paused = paused;
    const f = files.find(x => x.vid == v);
    meta.textContent = f ? `${(f.size/1048576).toFixed(1)} MB` : '';
  }
  sel.addEventListener('change', playCurrent);
  mode.addEventListener('change', playCurrent);
  playCurrent();
}
init().catch(console.error);