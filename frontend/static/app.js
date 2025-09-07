let allFiles = [];
let filteredFiles = [];
let currentView = 'table';
let currentSort = { column: 'movement', direction: 'desc' };
let selectedVideoId = null;
let annotations = [];
let showAnnotations = true;

async function init() {
  try {
    const res = await fetch('/api/videos');
    allFiles = await res.json();
    filteredFiles = [...allFiles];
    
    setupControls();
    renderView();
    
    // Select first video if available
    if (allFiles.length > 0) {
      selectVideo(allFiles[0].vid);
    }
  } catch (error) {
    console.error('Failed to load videos:', error);
    document.getElementById('file-list').innerHTML = '<p>Failed to load videos</p>';
  }
}

function setupControls() {
  // View toggle buttons
  document.getElementById('table-view-btn').addEventListener('click', () => setView('table'));
  document.getElementById('grid-view-btn').addEventListener('click', () => setView('grid'));
  
  // Search input
  document.getElementById('search').addEventListener('input', (e) => {
    filterFiles(e.target.value);
  });
  
  // Mode selector
  const mode = document.getElementById('mode');
  const opt1 = document.createElement('option'); opt1.value = 'normal'; opt1.textContent = "Normal"; mode.appendChild(opt1);
  const opt2 = document.createElement('option'); opt2.value = 'movement'; opt2.textContent = "Movement"; mode.appendChild(opt2);
  mode.addEventListener('change', updateVideoSource);
  
  // Annotations toggle
  document.getElementById('annotations').addEventListener('change', (e) => {
    showAnnotations = e.target.checked;
    drawAnnotations();
  });
  
  // Setup video player for annotation overlays
  setupVideoPlayer();
}

function setView(view) {
  currentView = view;
  document.querySelectorAll('.view-toggle button').forEach(btn => btn.classList.remove('active'));
  document.getElementById(`${view}-view-btn`).classList.add('active');
  renderView();
}

function filterFiles(searchTerm) {
  if (!searchTerm.trim()) {
    filteredFiles = [...allFiles];
  } else {
    const term = searchTerm.toLowerCase();
    filteredFiles = allFiles.filter(file => 
      file.name.toLowerCase().includes(term)
    );
  }
  renderView();
}

function renderView() {
  const container = document.getElementById('file-list');
  container.innerHTML = '';
  
  if (filteredFiles.length === 0) {
    container.innerHTML = '<p style="text-align: center; opacity: 0.7;">No videos found</p>';
    return;
  }
  
  if (currentView === 'table') {
    renderTableView(container);
  } else {
    renderGridView(container);
  }
}

function renderTableView(container) {
  const table = document.createElement('table');
  table.className = 'table-view';
  
  // Header
  const header = document.createElement('thead');
  const headerRow = document.createElement('tr');
  
  const columns = [
    { key: 'name', label: 'Name' },
    { key: 'size', label: 'Size' },
    { key: 'movement', label: 'Movement Score' }
  ];
  
  columns.forEach(col => {
    const th = document.createElement('th');
    th.textContent = col.label;
    th.className = 'sortable';
    if (currentSort.column === col.key) {
      th.classList.add(currentSort.direction);
    }
    th.addEventListener('click', () => sortFiles(col.key));
    headerRow.appendChild(th);
  });
  
  header.appendChild(headerRow);
  table.appendChild(header);
  
  // Body
  const tbody = document.createElement('tbody');
  
  filteredFiles.forEach(file => {
    const row = document.createElement('tr');
    row.dataset.vid = file.vid;
    if (selectedVideoId === file.vid) {
      row.classList.add('selected');
    }
    
    // Name
    const nameCell = document.createElement('td');
    nameCell.textContent = file.name;
    row.appendChild(nameCell);
    
    // Size
    const sizeCell = document.createElement('td');
    sizeCell.textContent = `${(file.size / 1048576).toFixed(1)} MB`;
    row.appendChild(sizeCell);
    
    // Movement Score
    const movementCell = document.createElement('td');
    const movementSpan = createMovementBadge(file.movement);
    movementCell.appendChild(movementSpan);
    row.appendChild(movementCell);
    
    row.addEventListener('click', () => selectVideo(file.vid));
    tbody.appendChild(row);
  });
  
  table.appendChild(tbody);
  container.appendChild(table);
}

function renderGridView(container) {
  const grid = document.createElement('div');
  grid.className = 'grid-view';
  
  filteredFiles.forEach(file => {
    const card = document.createElement('div');
    card.className = 'video-card';
    card.dataset.vid = file.vid;
    if (selectedVideoId === file.vid) {
      card.classList.add('selected');
    }
    
    const header = document.createElement('div');
    header.className = 'card-header';
    
    const title = document.createElement('h3');
    title.className = 'card-title';
    title.textContent = file.name;
    
    const movementBadge = createMovementBadge(file.movement);
    
    header.appendChild(title);
    header.appendChild(movementBadge);
    
    const meta = document.createElement('div');
    meta.className = 'card-meta';
    
    const sizeSpan = document.createElement('span');
    sizeSpan.innerHTML = `📁 ${(file.size / 1048576).toFixed(1)} MB`;
    
    meta.appendChild(sizeSpan);
    
    card.appendChild(header);
    card.appendChild(meta);
    
    card.addEventListener('click', () => selectVideo(file.vid));
    grid.appendChild(card);
  });
  
  container.appendChild(grid);
}

function createMovementBadge(movement) {
  const span = document.createElement('span');
  span.className = 'movement-score';
  
  if (movement === -1) {
    span.textContent = 'Not processed';
    span.classList.add('movement-none');
  } else {
    span.textContent = movement.toFixed(3);
    if (movement > 0.1) {
      span.classList.add('movement-high');
    } else if (movement > 0.05) {
      span.classList.add('movement-medium');
    } else {
      span.classList.add('movement-low');
    }
  }
  
  return span;
}

function sortFiles(column) {
  if (currentSort.column === column) {
    currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
  } else {
    currentSort.column = column;
    currentSort.direction = 'asc';
  }
  
  filteredFiles.sort((a, b) => {
    let valueA = a[column];
    let valueB = b[column];
    
    if (column === 'name') {
      valueA = valueA.toLowerCase();
      valueB = valueB.toLowerCase();
    }
    
    if (currentSort.direction === 'asc') {
      return valueA < valueB ? -1 : valueA > valueB ? 1 : 0;
    } else {
      return valueA > valueB ? -1 : valueA < valueB ? 1 : 0;
    }
  });
  
  renderView();
}

async function selectVideo(vid) {
  selectedVideoId = vid;
  await loadAnnotations(vid);
  updateVideoSource();
  renderView(); // Re-render to update selection
}

function updateVideoSource() {
  if (!selectedVideoId) return;
  
  const player = document.getElementById('player');
  const mode = document.getElementById('mode').value;
  const prevTime = player.currentTime;
  const wasPaused = player.paused;
  
  player.src = `/stream?vid=${selectedVideoId}&mode=${mode}`;
  player.currentTime = prevTime;
  if (!wasPaused) {
    player.play();
  }
}

async function loadAnnotations(vid) {
  try {
    const res = await fetch(`/api/annotations/${vid}`);
    annotations = await res.json();
  } catch (error) {
    console.error('Failed to load annotations:', error);
    annotations = [];
  }
}

function setupVideoPlayer() {
  const player = document.getElementById('player');
  const canvas = document.getElementById('annotation-overlay');
  
  // Update canvas size when video loads
  player.addEventListener('loadedmetadata', () => {
    resizeCanvas();
  });
  
  // Start annotation rendering when video plays
  player.addEventListener('play', () => {
    startAnnotationLoop(player);
  });

  // Stop rendering when paused or ended
  player.addEventListener('pause', () => {
    stopAnnotationLoop();
  });

  player.addEventListener('ended', () => {
    stopAnnotationLoop();
  });
  
  // Handle window resize
  window.addEventListener('resize', resizeCanvas);
}

let stopLoop = false;

function startAnnotationLoop(player) {
  stopLoop = false;

  if (player.requestVideoFrameCallback) {
    // Use high-precision API if available
    const onFrame = (now, metadata) => {
      if (stopLoop) return;
      drawAnnotations(metadata.mediaTime);
      player.requestVideoFrameCallback(onFrame);
    };
    player.requestVideoFrameCallback(onFrame);
  } else {
    // Fallback: poll with requestAnimationFrame
    const render = () => {
      if (stopLoop || player.paused || player.ended) return;
      drawAnnotations(player.currentTime);
      requestAnimationFrame(render);
    };
    requestAnimationFrame(render);
  }
}

function stopAnnotationLoop() {
  stopLoop = true;
}

function resizeCanvas() {
  const player = document.getElementById('player');
  const canvas = document.getElementById('annotation-overlay');
  
  canvas.width = player.offsetWidth;
  canvas.height = player.offsetHeight;
  drawAnnotations();
}

function drawAnnotations(time) {
  const player = document.getElementById('player');
  const canvas = document.getElementById('annotation-overlay');
  const ctx = canvas.getContext('2d');
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  if (!showAnnotations || annotations.length === 0 || player.paused) {
    return;
  }

  // TODO(jearly): Get FPS from video metadata
  // Calculate current frame (assuming 30fps)
  const fps = 30; // You might want to get this from video metadata
  const currentFrame = Math.floor(time * fps);
  
  // Get annotations for current frame
  const frameAnnotations = annotations.filter(ann => ann.frame_idx === currentFrame);
  
  if (frameAnnotations.length === 0) return;
  
  // Calculate scaling factors
  const scaleX = canvas.width / player.videoWidth;
  const scaleY = canvas.height / player.videoHeight;
  
  // Draw bounding boxes
  ctx.strokeStyle = '#00ff00';
  ctx.lineWidth = 2;
  ctx.font = '14px system-ui';
  ctx.fillStyle = '#00ff00';
  
  frameAnnotations.forEach(ann => {
    const x = ann.x1 * scaleX;
    const y = ann.y1 * scaleY;
    const width = (ann.x2 - ann.x1) * scaleX;
    const height = (ann.y2 - ann.y1) * scaleY;
    
    // Draw bounding box
    ctx.strokeRect(x, y, width, height);
    
    // Draw label background
    const label = `${ann.name} (${(ann.confidence * 100).toFixed(1)}%)`;
    const labelWidth = ctx.measureText(label).width + 8;
    const labelHeight = 20;
    
    ctx.fillStyle = '#00ff00';
    ctx.fillRect(x, y - labelHeight, labelWidth, labelHeight);
    
    // Draw label text
    ctx.fillStyle = '#000000';
    ctx.fillText(label, x + 4, y - 6);
    ctx.fillStyle = '#00ff00';
  });
}

// Initialize the app
init().catch(console.error);