let allFiles = [];
let filteredFiles = [];
let currentSort = 'oldest';
let selectedVideoId = null;
let annotations = [];
let showAnnotations = true;
let hideEmpty = false;
let objectFilter = '';
let filterPerson = false;
let timeFilter = '';

async function init() {
  try {
    const res = await fetch('/api/videos');
    allFiles = await res.json();
    filteredFiles = [...allFiles];
    
    setupControls();
    updateVideoCount();
    sortAndRenderFiles();
  } catch (error) {
    console.error('Failed to load videos:', error);
    document.getElementById('file-list').innerHTML = '<p>Failed to load videos</p>';
  }
}


function setupControls() {
  // Hide empty videos toggle
  document.getElementById('hide-empty').addEventListener('change', (e) => {
    hideEmpty = e.target.checked;
    filterFiles();
  });
  
  // Object filter dropdown
  document.getElementById('object-filter').addEventListener('change', (e) => {
    objectFilter = e.target.value;
    filterFiles();
  });
  
  // Time filter dropdown
  document.getElementById('time-filter').addEventListener('change', (e) => {
    timeFilter = e.target.value;
    filterFiles();
  });
  
  // Filter person checkbox
  document.getElementById('filter-person').addEventListener('change', (e) => {
    filterPerson = e.target.checked;
    filterFiles();
  });
  
  // Sort by dropdown
  document.getElementById('sort-by').addEventListener('change', (e) => {
    currentSort = e.target.value;
    sortAndRenderFiles();
  });
  
  // Setup video player for annotation overlays
  setupVideoPlayer();
}


function filterFiles() {
  filteredFiles = [...allFiles];
  
  // Filter out videos with person if requested
  if (filterPerson) {
    filteredFiles = filteredFiles.filter(file => {
      if (!file.objects || file.objects.length === 0) {
        return true; // Keep empty videos
      }
      // Keep videos that don't have "person"
      return !file.objects.includes('person');
    });
  }
  
  // Filter by empty videos if requested
  if (hideEmpty) {
    filteredFiles = filteredFiles.filter(file => 
      file.objects && file.objects.length > 0
    );
  }
  
  // Filter by object type if specified
  if (objectFilter) {
    filteredFiles = filteredFiles.filter(file => 
      file.objects && file.objects.includes(objectFilter)
    );
  }
  
  // Filter by day/night if specified
  if (timeFilter) {
    filteredFiles = filteredFiles.filter(file => {
      if (timeFilter === 'day') {
        return !file.is_night;
      } else if (timeFilter === 'night') {
        return file.is_night;
      }
      return true; // 'day + night' or empty shows all
    });
  }
  
  updateVideoCount();
  sortAndRenderFiles();
}

function updateVideoCount() {
  const count = filteredFiles.length;
  const videoCountElement = document.getElementById('video-count');
  videoCountElement.textContent = `${count} video${count !== 1 ? 's' : ''}`;
}

function renderView() {
  const container = document.getElementById('file-list');
  container.innerHTML = '';
  
  if (filteredFiles.length === 0) {
    container.innerHTML = '<p style="text-align: center; opacity: 0.7;">No videos found</p>';
    return;
  }
  
  renderGridView(container);
}


function renderGridView(container) {
  const grid = document.createElement('div');
  grid.className = 'grid-view';
  
  // Calculate grid columns to determine row breaks
  const gridStyle = getComputedStyle(grid);
  const containerWidth = container.offsetWidth || 1200; // fallback width
  const minCardWidth = 280; // matches CSS minmax(280px, 1fr)
  const gap = 16; // matches CSS gap
  const columnsPerRow = Math.floor((containerWidth + gap) / (minCardWidth + gap));
  
  let expandedCardIndex = -1;
  if (selectedVideoId) {
    expandedCardIndex = filteredFiles.findIndex(file => file.vid === selectedVideoId);
  }
  
  // First, add all the regular/placeholder cards
  filteredFiles.forEach((file, index) => {
    let card;
    if (selectedVideoId === file.vid) {
      // Create placeholder card for expanded video
      card = createPlaceholderCard(file);
    } else {
      // Create regular collapsed card
      card = createCollapsedCard(file, document.createElement('div'));
    }
    grid.appendChild(card);
  });
  
  // If there's an expanded video, add the expanded view after the current row
  if (expandedCardIndex >= 0) {
    const currentRow = Math.floor(expandedCardIndex / columnsPerRow);
    const expandedCard = createExpandedCard(filteredFiles[expandedCardIndex]);
    
    // Insert expanded card after all cards in the current row
    const insertPosition = (currentRow + 1) * columnsPerRow;
    const allCards = grid.children;
    
    if (insertPosition < allCards.length) {
      grid.insertBefore(expandedCard, allCards[insertPosition]);
    } else {
      grid.appendChild(expandedCard);
    }
  }
  
  container.appendChild(grid);
}

function createPlaceholderCard(file) {
  const card = document.createElement('div');
  card.className = 'video-card placeholder-card';
  card.dataset.vid = file.vid;
  
  // Thumbnail with play indicator
  const thumbnail = document.createElement('div');
  thumbnail.className = 'card-thumbnail';
  thumbnail.innerHTML = '▶️'; // Play icon to indicate this is playing
  
  const content = document.createElement('div');
  content.className = 'card-content';
  
  const header = document.createElement('div');
  header.className = 'card-header';

  const meta = document.createElement('div');
  meta.className = 'card-meta';
  
  const statusSpan = document.createElement('span');
  statusSpan.innerHTML = '🎬 Playing';
  statusSpan.style.color = '#238636';
  
  meta.appendChild(statusSpan);
  
  content.appendChild(header);
  content.appendChild(meta);
  
  card.appendChild(thumbnail);
  card.appendChild(content);
  
  // Click to collapse
  card.addEventListener('click', () => collapseVideo());
  return card;
}

function createCollapsedCard(file, card) {
  // Thumbnail with image
  const thumbnail = document.createElement('div');
  thumbnail.className = 'card-thumbnail';
  
  const img = document.createElement('img');
  img.src = file.thumbnail_url;
  img.alt = `Thumbnail for ${file.name}`;
  img.className = 'thumbnail-image';
  
  // Fallback to emoji if image fails to load
  img.onerror = function() {
    thumbnail.innerHTML = '🎥';
    thumbnail.classList.add('thumbnail-fallback');
  };
  
  thumbnail.appendChild(img);
  
  const content = document.createElement('div');
  content.className = 'card-content';
  
  const header = document.createElement('div');
  header.className = 'card-header';

  const meta = document.createElement('div');
  meta.className = 'card-meta';
  
  // Add metadata info
  const metaInfo = document.createElement('div');
  metaInfo.className = 'card-meta-info';
  
  // Modified date
  const modifiedSpan = document.createElement('span');
  modifiedSpan.className = 'meta-item';
  if (file.modified) {
    const date = new Date(file.modified * 1000);
    modifiedSpan.textContent = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
  } else {
    modifiedSpan.textContent = 'Unknown date';
  }
  metaInfo.appendChild(modifiedSpan);
  
  // Wildlife proportion
  const wildlifeSpan = document.createElement('span');
  wildlifeSpan.className = 'meta-item';
  const proportion = file.wildlife_prop || 0;
  wildlifeSpan.textContent = `${(proportion * 100).toFixed(1)}% wildlife`;
  metaInfo.appendChild(wildlifeSpan);
  
  meta.appendChild(metaInfo);
  
  // Add objects container
  const objectsContainer = document.createElement('div');
  objectsContainer.className = 'card-objects';
  
  // Display objects directly from the file data
  displayVideoObjects(file.objects, objectsContainer);
  meta.appendChild(objectsContainer);
  
  content.appendChild(header);
  content.appendChild(meta);
  
  card.appendChild(thumbnail);
  card.appendChild(content);
  
  card.addEventListener('click', () => selectVideo(file.vid));
  return card;
}

function createExpandedCard(file) {
  const card = document.createElement('div');
  card.className = 'video-card expanded-card';
  card.dataset.vid = file.vid;
  
  // Video thumbnail area with embedded player
  const thumbnail = document.createElement('div');
  thumbnail.className = 'card-thumbnail';
  
  const videoContainer = document.createElement('div');
  videoContainer.className = 'video-container';
  
  const video = document.createElement('video');
  video.id = 'player';
  video.controls = true;
  video.preload = 'auto';
  video.src = `/stream?vid=${file.vid}`;
  
  const canvas = document.createElement('canvas');
  canvas.id = 'annotation-overlay';
  
  videoContainer.appendChild(video);
  videoContainer.appendChild(canvas);
  thumbnail.appendChild(videoContainer);
  
  // Content area with info and controls
  const content = document.createElement('div');
  content.className = 'card-content';
  
  const info = document.createElement('div');
  info.className = 'card-info';
  
  const meta = document.createElement('div');
  meta.className = 'card-meta';
  
  // Add metadata info for expanded view
  const metaInfo = document.createElement('div');
  metaInfo.className = 'card-meta-info';
  
  // Modified date
  const modifiedSpan = document.createElement('span');
  modifiedSpan.className = 'meta-item';
  if (file.modified) {
    const date = new Date(file.modified * 1000);
    modifiedSpan.textContent = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;
  } else {
    modifiedSpan.textContent = 'Unknown';
  }
  metaInfo.appendChild(modifiedSpan);
  
  // Wildlife proportion
  const wildlifeSpan = document.createElement('span');
  wildlifeSpan.className = 'meta-item';
  const proportion = file.wildlife_prop || 0;
  wildlifeSpan.textContent = `Wildlife Activity: ${(proportion * 100).toFixed(1)}%`;
  metaInfo.appendChild(wildlifeSpan);
  
  meta.appendChild(metaInfo);
  
  // Add objects container for expanded view
  const objectsContainer = document.createElement('div');
  objectsContainer.className = 'card-objects';
  displayVideoObjects(file.objects, objectsContainer);
  meta.appendChild(objectsContainer);
  
  info.appendChild(meta);
  
  // Controls
  const controls = document.createElement('div');
  controls.className = 'card-controls';
  
  const closeButton = document.createElement('button');
  closeButton.className = 'close-button';
  closeButton.textContent = '✕ Close';
  closeButton.addEventListener('click', (e) => {
    e.stopPropagation();
    collapseVideo();
  });
  
  // Add annotation controls
  const annotationToggle = document.createElement('label');
  annotationToggle.innerHTML = '<input type="checkbox" checked> Show Annotations';
  const checkbox = annotationToggle.querySelector('input');
  checkbox.addEventListener('change', (e) => {
    showAnnotations = e.target.checked;
    drawAnnotations();
  });
  
  controls.appendChild(closeButton);
  controls.appendChild(annotationToggle);
  
  content.appendChild(info);
  content.appendChild(controls);
  
  card.appendChild(thumbnail);
  card.appendChild(content);
  
  // Setup video player for this expanded card
  setupVideoPlayerForCard(video, canvas);
  
  return card;
}

function sortAndRenderFiles() {
  filteredFiles.sort((a, b) => {
    switch (currentSort) {
      case 'latest':
        return (b.modified || 0) - (a.modified || 0);
      case 'oldest':
        return (a.modified || 0) - (b.modified || 0);
      case 'most_activity':
        return (b.wildlife_prop || 0) - (a.wildlife_prop || 0);
      case 'least_activity':
        return (a.wildlife_prop || 0) - (b.wildlife_prop || 0);
      default:
        return (a.modified || 0) - (b.modified || 0);
    }
  });
  
  renderView();
}

async function selectVideo(vid) {
  // Store current scroll position before any DOM changes
  const currentScrollY = window.scrollY;
  const clickedCard = document.querySelector(`[data-vid="${vid}"]`);
  const clickedCardRect = clickedCard ? clickedCard.getBoundingClientRect() : null;
  
  // If there's already an expanded video, collapse it first without scrolling
  if (selectedVideoId && selectedVideoId !== vid) {
    await collapseVideoWithoutScroll();
  }
  
  selectedVideoId = vid;
  await loadAnnotations(vid);
  
  // Add expanding class before rendering
  const container = document.getElementById('file-list');
  container.classList.add('expanding');
  
  // Preserve scroll position during render
  renderView(); // Re-render to update selection and expand card
  
  // Immediately restore scroll position to prevent jumping
  window.scrollTo(0, currentScrollY);
  
  // Handle scrolling more intelligently with optimized timing
  requestAnimationFrame(() => {
    const expandedCard = document.querySelector('.video-card.expanded-card');
    const placeholderCard = document.querySelector('.video-card.placeholder-card');
    
    if (expandedCard && placeholderCard) {
      expandedCard.classList.add('entering');
      
      // Only scroll if the clicked card is not visible or if expanding would push content off screen
      const placeholderRect = placeholderCard.getBoundingClientRect();
      const viewportHeight = window.innerHeight;
      const headerHeight = 100; // Approximate header height
      
      // Check if placeholder is reasonably visible
      const isPlaceholderVisible = placeholderRect.top >= headerHeight && 
                                   placeholderRect.top < viewportHeight * 0.7;
      
      if (!isPlaceholderVisible) {
        // Use requestAnimationFrame for smoother scrolling timing
        requestAnimationFrame(() => {
          const targetY = window.scrollY + placeholderRect.top - headerHeight - 20;
          window.scrollTo({
            top: Math.max(0, targetY),
            behavior: 'smooth'
          });
        });
      }
      
      // Remove entering class after animation
      setTimeout(() => {
        expandedCard.classList.remove('entering');
      }, 500);
    }
    container.classList.remove('expanding');
  }, 150);
}

function collapseVideo() {
  collapseVideoWithTransition();
}

async function collapseVideoWithTransition() {
  const expandedCard = document.querySelector('.video-card.expanded-card');
  const placeholderCard = document.querySelector('.video-card.placeholder-card');
  const container = document.getElementById('file-list');
  
  if (expandedCard && placeholderCard) {
    // Store the placeholder position before collapsing
    const placeholderRect = placeholderCard.getBoundingClientRect();
    const scrollAdjustment = placeholderRect.top + window.scrollY;
    
    // Add exiting animation
    expandedCard.classList.add('exiting');
    container.classList.add('collapsing');
    
    // Wait for animation to complete
    await new Promise(resolve => setTimeout(resolve, 300));
    
    // Preserve scroll position after collapse
    const targetScrollY = Math.max(0, scrollAdjustment - 120); // Account for header
    window.scrollTo({
      top: targetScrollY,
      behavior: 'smooth'
    });
  }
  
  selectedVideoId = null;
  
  // Store scroll position before render
  const currentScrollY = window.scrollY;
  renderView(); // Re-render to collapse all cards
  
  // Restore scroll position immediately after render
  window.scrollTo(0, currentScrollY);
  
  // Clean up classes
  setTimeout(() => {
    container.classList.remove('collapsing');
  }, 50);
}

async function collapseVideoWithoutScroll() {
  const expandedCard = document.querySelector('.video-card.expanded-card');
  const container = document.getElementById('file-list');
  
  if (expandedCard) {
    // Quick collapse without scrolling adjustments
    expandedCard.classList.add('exiting');
    container.classList.add('collapsing');
    
    // Shorter wait time for smoother transitions between videos
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  
  selectedVideoId = null;
  
  // Store scroll position before render
  const currentScrollY = window.scrollY;
  renderView();
  
  // Restore scroll position immediately after render
  window.scrollTo(0, currentScrollY);
  
  setTimeout(() => {
    container.classList.remove('collapsing');
  }, 50);
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
  // Setup window resize handlers for any video players
  window.addEventListener('resize', () => {
    const canvas = document.getElementById('annotation-overlay');
    if (canvas) resizeCanvas();
  });
  
  // Handle fullscreen changes
  document.addEventListener('fullscreenchange', () => {
    const canvas = document.getElementById('annotation-overlay');
    if (canvas) resizeCanvas();
  });
  document.addEventListener('webkitfullscreenchange', () => {
    const canvas = document.getElementById('annotation-overlay');
    if (canvas) resizeCanvas();
  });
  document.addEventListener('mozfullscreenchange', () => {
    const canvas = document.getElementById('annotation-overlay');
    if (canvas) resizeCanvas();
  });
  document.addEventListener('MSFullscreenChange', () => {
    const canvas = document.getElementById('annotation-overlay');
    if (canvas) resizeCanvas();
  });
}

function setupVideoPlayerForCard(player, canvas) {
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
  const container = document.querySelector('.video-container');
  
  // Check if we're in fullscreen mode
  const isFullscreen = !!(document.fullscreenElement || document.webkitFullscreenElement || 
                         document.mozFullScreenElement || document.msFullscreenElement);
  
  if (isFullscreen) {
    // In fullscreen, make canvas fill the screen
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    canvas.style.width = '100vw';
    canvas.style.height = '100vh';
  } else {
    // Normal mode, match video dimensions
    canvas.width = player.offsetWidth;
    canvas.height = player.offsetHeight;
    canvas.style.width = '100%';
    canvas.style.height = '100%';
  }
  
  drawAnnotations();
}

function drawAnnotations(time) {
  const player = document.getElementById('player');
  const canvas = document.getElementById('annotation-overlay');
  
  // Exit early if no player or canvas (not expanded)
  if (!player || !canvas) {
    return;
  }
  
  const ctx = canvas.getContext('2d');
  
  // Clear canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  if (!showAnnotations || annotations.length === 0 || player.paused) {
    return;
  }

  // Get FPS from video metadata if available, otherwise assume 30fps
  let fps = 30;
  if (player.videoWidth && player.videoHeight) {
    // Try to get framerate from video element (if available)
    const tracks = player.captureStream ? player.captureStream().getVideoTracks() : [];
    if (tracks.length > 0 && tracks[0].getSettings) {
      const settings = tracks[0].getSettings();
      if (settings.frameRate) {
        fps = settings.frameRate;
      }
    }
  }
  const currentFrame = Math.floor(time * fps);
  
  // Get annotations for current frame
  let frameAnnotations = annotations.filter(ann => ann.frame_idx === currentFrame);
  
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

function displayVideoObjects(objects, container) {
  container.innerHTML = ''; // Clear existing content
  
  if (!objects || objects.length === 0) {
    const noObjectsSpan = document.createElement('span');
    noObjectsSpan.className = 'no-objects';
    noObjectsSpan.textContent = 'No objects detected';
    container.appendChild(noObjectsSpan);
    return;
  }
  
  // Convert Set to Array if needed
  const objectArray = Array.isArray(objects) ? objects : Array.from(objects);
  
  // Create labels for each object
  objectArray.forEach(objectName => {
    const label = document.createElement('span');
    label.className = 'object-label';
    label.textContent = objectName;
    container.appendChild(label);
  });
}

// Initialize the app
init().catch(console.error);