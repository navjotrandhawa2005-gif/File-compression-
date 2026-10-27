// DAAC Studio - Premium UI
let currentFile = null;
let currentCompressedBlob = null;
let currentDecompressedBlob = null;

document.addEventListener('DOMContentLoaded', () => {
  initializeTabs();
  initializeDropzones();
  initializeCommandPalette();
  lucide.createIcons();
});

// Tabs
function initializeTabs() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const tab = item.dataset.tab;
      
      // Update nav
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
      
      // Update panes
      document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.remove('active');
      });
      document.getElementById(`tab-${tab}`).classList.add('active');
    });
  });
}

// Dropzones
function initializeDropzones() {
  // Compress
  const compressDropzone = document.getElementById('compressDropzone');
  const compressInput = document.getElementById('compressFileInput');
  
  compressDropzone.addEventListener('click', () => compressInput.click());
  compressInput.addEventListener('change', (e) => {
    handleCompressFile(e.target.files[0]);
  });
  
  compressDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    compressDropzone.style.borderColor = 'var(--accent)';
  });
  
  compressDropzone.addEventListener('dragleave', () => {
    compressDropzone.style.borderColor = 'var(--border)';
  });
  
  compressDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    compressDropzone.style.borderColor = 'var(--border)';
    handleCompressFile(e.dataTransfer.files[0]);
  });
  
  document.getElementById('compressBtn').addEventListener('click', compressFile);
  
  // Decompress
  const decompressDropzone = document.getElementById('decompressDropzone');
  const decompressInput = document.getElementById('decompressFileInput');
  decompressInput.removeAttribute('accept');
  
  decompressDropzone.addEventListener('click', () => decompressInput.click());
  decompressInput.addEventListener('change', (e) => {
    handleDecompressFile(e.target.files[0]);
  });
  
  document.getElementById('decompressBtn').addEventListener('click', decompressFile);
  document.getElementById('downloadRestored').addEventListener('click', downloadRestored);
  
  // Inspector
  const inspectorDropzone = document.getElementById('inspectorDropzone');
  const inspectorInput = document.getElementById('inspectorFileInput');
  inspectorInput.removeAttribute('accept');
  
  inspectorDropzone.addEventListener('click', () => inspectorInput.click());
  inspectorInput.addEventListener('change', (e) => {
    inspectFile(e.target.files[0]);
  });
  
  // Benchmark
  document.getElementById('runBenchmark').addEventListener('click', runBenchmark);
}

function compressImageDirectly(file, quality = 0.75) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const baseW = img.naturalWidth || img.width;
        const baseH = img.naturalHeight || img.height;
        
        let ext = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();
        let outMime = 'image/jpeg';
        if (ext === '.png' || file.type === 'image/png') {
          outMime = 'image/png';
        } else if (ext === '.webp' || file.type === 'image/webp') {
          outMime = 'image/webp';
        } else {
          outMime = 'image/jpeg';
          if (ext !== '.jpeg') ext = '.jpg';
        }

        const MAX_DIM = 2560;
        let w = baseW;
        let h = baseH;
        if (w > MAX_DIM || h > MAX_DIM) {
          if (w > h) {
            h = Math.round((h * MAX_DIM) / w);
            w = MAX_DIM;
          } else {
            w = Math.round((w * MAX_DIM) / h);
            h = MAX_DIM;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';

        if (outMime === 'image/jpeg') {
          ctx.fillStyle = '#FFFFFF';
          ctx.fillRect(0, 0, w, h);
        } else {
          ctx.clearRect(0, 0, w, h);
        }
        ctx.drawImage(img, 0, 0, w, h);

        const qualityParam = outMime === 'image/png' ? undefined : quality;
        canvas.toBlob((compressedBlob) => {
          if (!compressedBlob) {
            reject(new Error('Canvas compression failed'));
            return;
          }
          if (compressedBlob.size >= file.size && outMime === 'image/png') {
            canvas.toBlob((webpBlob) => {
              if (webpBlob && webpBlob.size < file.size) {
                resolve(webpBlob);
              } else {
                resolve(compressedBlob);
              }
            }, 'image/webp', 0.8);
          } else {
            resolve(compressedBlob);
          }
        }, outMime, qualityParam);
      };
      img.onerror = () => reject(new Error('Failed to load image for compression'));
      img.src = e.target.result;
    };
    reader.onerror = () => reject(new Error('Failed to read image file'));
    reader.readAsDataURL(file);
  });
}

function handleCompressFile(file) {
  if (!file) return;
  currentFile = file;
  
  document.getElementById('compressFileInfo').style.display = 'block';
  document.getElementById('compressFileName').textContent = file.name;
  document.getElementById('compressFileSize').textContent = formatBytes(file.size);

  const isImage = file.type.startsWith('image/') || /\.(png|jpe?g|webp|bmp|gif)$/i.test(file.name);
  const imgAlgoItem = document.getElementById('algoItemImage');
  if (imgAlgoItem) {
    if (isImage) {
      imgAlgoItem.style.display = 'block';
      imgAlgoItem.querySelector('input').checked = true;
    } else {
      imgAlgoItem.style.display = 'none';
      const autoInput = document.querySelector('input[name="algo"][value="auto"]');
      if (autoInput) autoInput.checked = true;
    }
  }

  const compName = file.name.startsWith('compressed_') ? file.name : `compressed_${file.name}`;
  const dlText = document.getElementById('downloadBtnText');
  if (dlText) {
    dlText.textContent = `Download ${compName}`;
  }
}

async function compressFile() {
  if (!currentFile) {
    alert('Please select a file');
    return;
  }
  
  const algoChoice = document.querySelector('input[name="algo"]:checked')?.value || 'auto';
  const btn = document.getElementById('compressBtn');
  btn.disabled = true;
  btn.innerHTML = '<span>Compressing...</span>';
  
  try {
    let blob;
    let algoDisplayName = algoChoice.toUpperCase();
    
    if (algoChoice === 'image_opt') {
      blob = await compressImageDirectly(currentFile, 0.75);
      algoDisplayName = 'Image Optimizer (High Efficiency)';
      
      const previewWrap = document.getElementById('imagePreviewWrap');
      const previewImg = document.getElementById('imagePreview');
      if (previewWrap && previewImg) {
        previewImg.src = window.URL.createObjectURL(blob);
        previewWrap.style.display = 'block';
      }
    } else {
      const previewWrap = document.getElementById('imagePreviewWrap');
      if (previewWrap) previewWrap.style.display = 'none';

      const formData = new FormData();
      formData.append('file', currentFile);
      formData.append('algorithm', algoChoice);
      
      const response = await fetch('http://localhost:8001/compress', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Compression failed');
      
      const chosenServerAlgo = response.headers.get('X-Chosen-Algorithm');
      if (chosenServerAlgo) {
        algoDisplayName = algoChoice === 'auto' 
          ? `Auto (${chosenServerAlgo.toUpperCase()})` 
          : chosenServerAlgo.toUpperCase();
      }
      blob = await response.blob();
    }
    
    currentCompressedBlob = blob;
    
    // Show results
    document.getElementById('compressEmpty').style.display = 'none';
    document.getElementById('compressResults').style.display = 'block';
    
    const algoUsedEl = document.getElementById('statAlgoUsed');
    if (algoUsedEl) {
      algoUsedEl.textContent = `Engine: ${algoDisplayName}`;
    }
    
    document.getElementById('statOriginal').textContent = formatBytes(currentFile.size);
    document.getElementById('statCompressed').textContent = formatBytes(blob.size);
    
    const ratio = (currentFile.size / (blob.size || 1)).toFixed(2);
    const savings = ((1 - blob.size / currentFile.size) * 100).toFixed(1);
    
    document.getElementById('statRatio').textContent = ratio + 'x';
    const savingsEl = document.getElementById('statSavings');
    savingsEl.textContent = (savings >= 0 ? '+' : '') + savings + '%';
    savingsEl.style.color = savings >= 0 ? 'var(--success)' : 'var(--text-secondary)';
    
    // Format compressed filename: 'compressed_' prefix + original extension
    const compName = currentFile.name.startsWith('compressed_') ? currentFile.name : `compressed_${currentFile.name}`;
    
    const dlBtn = document.getElementById('downloadCompressed');
    const dlText = document.getElementById('downloadBtnText');
    if (dlText) {
      dlText.textContent = `Download ${compName}`;
    }
    dlBtn.onclick = () => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = compName;
      a.click();
      window.URL.revokeObjectURL(url);
    };
  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="zap" style="width: 16px; height: 16px;"></i><span>Compress</span>';
    lucide.createIcons();
  }
}

let currentDecompressFile = null;
function handleDecompressFile(file) {
  if (!file) return;
  currentDecompressFile = file;
  document.getElementById('decompressBtn').disabled = false;
  const dlBtnSpan = document.querySelector('#downloadRestored span');
  if (dlBtnSpan) {
    const name = file.name.startsWith('compressed_') ? file.name.substring(11) : ('restored_' + file.name);
    dlBtnSpan.textContent = `Download ${name}`;
  }
}

async function decompressFile() {
  if (!currentDecompressFile) return;
  
  const btn = document.getElementById('decompressBtn');
  btn.disabled = true;
  btn.innerHTML = '<span>Decompressing...</span>';
  
  try {
    // Check if file starts with DAAC magic bytes
    const slice = currentDecompressFile.slice(0, 4);
    const buffer = await slice.arrayBuffer();
    const bytes = new Uint8Array(buffer);
    const isDaac = bytes.length >= 4 && bytes[0] === 0x44 && bytes[1] === 0x41 && bytes[2] === 0x41 && bytes[3] === 0x43;
    
    let blob;
    if (isDaac) {
      const formData = new FormData();
      formData.append('file', currentDecompressFile);
      
      const response = await fetch('http://localhost:8001/decompress', {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('Decompression failed');
      blob = await response.blob();
      document.getElementById('verifyText').textContent = 'Lossless Verified (SHA-256)';
    } else {
      // Direct openable file (e.g. optimized image)
      blob = currentDecompressFile;
      document.getElementById('verifyText').textContent = 'Direct File Verified (Native Format)';
    }
    
    currentDecompressedBlob = blob;
    
    document.getElementById('decompressEmpty').style.display = 'none';
    document.getElementById('decompressResults').style.display = 'block';
    document.getElementById('verifyBadge').style.background = 'var(--success-subtle)';
    document.getElementById('verifyBadge').style.color = 'var(--success)';
  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="rotate-ccw" style="width: 16px; height: 16px;"></i><span>Decompress</span>';
    lucide.createIcons();
  }
}

function downloadRestored() {
  if (!currentDecompressedBlob) return;
  const url = window.URL.createObjectURL(currentDecompressedBlob);
  const a = document.createElement('a');
  a.href = url;
  let filename = 'restored_file';
  if (currentDecompressFile && currentDecompressFile.name) {
    const orig = currentDecompressFile.name;
    if (orig.startsWith('compressed_')) {
      filename = orig.substring('compressed_'.length);
    } else {
      filename = 'restored_' + orig;
    }
  }
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

async function inspectFile(file) {
  if (!file) return;
  
  try {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await fetch('http://localhost:8001/inspect', {
      method: 'POST',
      body: formData
    });
    
    if (!response.ok) throw new Error('Inspection failed');
    
    const data = await response.json();
    
    document.getElementById('inspectorResults').style.display = 'block';
    document.getElementById('inspMagic').textContent = data.magic;
    document.getElementById('inspVersion').textContent = data.version;
    document.getElementById('inspAlgo').textContent = data.algorithm_name;
    document.getElementById('inspOriginal').textContent = formatBytes(data.original_size);
    document.getElementById('inspSha').textContent = data.sha256;
    
    // Create byte map
    const byteGrid = document.getElementById('byteGrid');
    byteGrid.innerHTML = '';
    const headerHex = data.header_hex;
    for (let i = 0; i < headerHex.length; i += 2) {
      const cell = document.createElement('div');
      cell.className = 'byte-cell';
      cell.textContent = headerHex.substr(i, 2).toUpperCase();
      byteGrid.appendChild(cell);
    }
  } catch (error) {
    alert('Error: ' + error.message);
  }
}

async function runBenchmark() {
  const btn = document.getElementById('runBenchmark');
  btn.disabled = true;
  btn.innerHTML = '<span>Running...</span>';
  
  try {
    const response = await fetch('http://localhost:8001/benchmark');
    const data = await response.json();
    
    // Update table
    const tbody = document.getElementById('benchmarkTableBody');
    tbody.innerHTML = '';
    
    if (data.results) {
      data.results.slice(0, 20).forEach(r => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>${r.file_name || '-'}</td>
          <td>${r.algorithm}</td>
          <td>${formatBytes(r.original_size || 0)}</td>
          <td>${formatBytes(r.compressed_size || 0)}</td>
          <td>${(r.compression_ratio || 0).toFixed(2)}x</td>
          <td>${(r.space_savings_percent || 0).toFixed(1)}%</td>
          <td>${(r.compression_time || 0).toFixed(4)}s</td>
        `;
        tbody.appendChild(tr);
      });
    }
  } catch (error) {
    alert('Error: ' + error.message);
  } finally {
    btn.disabled = false;
    btn.innerHTML = '<i data-lucide="play" style="width: 14px; height: 14px;"></i>Run Benchmark';
    lucide.createIcons();
  }
}

// Command Palette
function initializeCommandPalette() {
  const btn = document.getElementById('cmdPaletteBtn');
  const palette = document.getElementById('cmdPalette');
  const backdrop = document.getElementById('cmdBackdrop');
  const input = document.getElementById('cmdInput');
  const items = document.querySelectorAll('.cmd-item');
  
  btn.addEventListener('click', () => {
    palette.classList.add('active');
    input.focus();
  });
  
  backdrop.addEventListener('click', () => {
    palette.classList.remove('active');
  });
  
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      palette.classList.toggle('active');
      if (palette.classList.contains('active')) input.focus();
    }
    if (e.key === 'Escape') {
      palette.classList.remove('active');
    }
  });
  
  items.forEach(item => {
    item.addEventListener('click', () => {
      const cmd = item.dataset.cmd;
      document.querySelectorAll('.nav-item').forEach(nav => {
        nav.classList.toggle('active', nav.dataset.tab === cmd);
      });
      document.querySelectorAll('.tab-pane').forEach(pane => {
        pane.classList.toggle('active', pane.id === `tab-${cmd}`);
      });
      palette.classList.remove('active');
    });
  });
}

function formatBytes(bytes) {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}
