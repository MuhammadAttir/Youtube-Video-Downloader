/**
 * StreamPull — Main App JS
 * Handles: URL fetch, format/quality selection, download trigger, toasts, theme
 */

/* ── State ────────────────────────────────────────────────── */
const state = {
  currentUrl: "",
  currentFormat: "mp4",
  currentQuality: null,
  mp4Qualities: [],
  mp3Qualities: [],
  isFetching: false,
  isDownloading: false,
};

/* ── DOM References ───────────────────────────────────────── */
const $ = (id) => document.getElementById(id);

const urlInput    = $("urlInput");
const fetchBtn    = $("fetchBtn");
const clearBtn    = $("clearBtn");
const infoPanel   = $("infoPanel");
const skeleton    = $("skeleton");
const videoInfo   = $("videoInfo");
const videoThumb  = $("videoThumb");
const videoDuration = $("videoDuration");
const videoTitle  = $("videoTitle");
const videoUploader = $("videoUploader");
const videoViews  = $("videoViews");
const videoDate   = $("videoDate");
const videoSize   = $("videoSize");
const btnMp4      = $("btnMp4");
const btnMp3      = $("btnMp3");
const mp4Grid     = $("mp4Qualities");
const mp3Grid     = $("mp3Qualities");
const downloadBtn = $("downloadBtn");
const progressWrap = $("progressWrap");
const progressBar = $("progressBar");
const progressLabel = $("progressLabel");
const resetBtn    = $("resetBtn");
const themeToggle = $("themeToggle");
const toastContainer = $("toastContainer");

/* ── Theme ────────────────────────────────────────────────── */
function initTheme() {
  const saved = localStorage.getItem("sp-theme") || "dark";
  setTheme(saved);
}

function setTheme(theme) {
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("sp-theme", theme);
  const sunIcon = document.querySelector(".sun-icon");
  const moonIcon = document.querySelector(".moon-icon");
  if (theme === "dark") {
    sunIcon.classList.remove("hidden");
    moonIcon.classList.add("hidden");
  } else {
    sunIcon.classList.add("hidden");
    moonIcon.classList.remove("hidden");
  }
}

themeToggle.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");
  setTheme(current === "dark" ? "light" : "dark");
});

/* ── Toast Notifications ──────────────────────────────────── */
function showToast(message, type = "info", duration = 4000) {
  const icons = {
    success: `<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>`,
    error: `<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`,
    info: `<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>`,
  };
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `${icons[type]}<span>${message}</span>`;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add("toast-exit");
    toast.addEventListener("animationend", () => toast.remove(), { once: true });
  }, duration);
}

/* ── URL Input Handling ───────────────────────────────────── */
urlInput.addEventListener("input", () => {
  const hasValue = urlInput.value.trim().length > 0;
  clearBtn.classList.toggle("hidden", !hasValue);
});

clearBtn.addEventListener("click", () => {
  urlInput.value = "";
  clearBtn.classList.add("hidden");
  urlInput.focus();
});

// Allow pressing Enter to fetch
urlInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter") fetchVideo();
});

fetchBtn.addEventListener("click", fetchVideo);
resetBtn.addEventListener("click", resetPanel);

/* ── Fetch Video Info ─────────────────────────────────────── */
async function fetchVideo() {
  if (state.isFetching) return;
  const url = urlInput.value.trim();
  if (!url) {
    showToast("Please paste a YouTube URL first.", "error");
    urlInput.focus();
    return;
  }

  state.isFetching = true;
  state.currentUrl = url;
  setFetchLoading(true);
  showInfoPanel("skeleton");

  try {
    const resp = await fetch("/api/info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const json = await resp.json();

    if (!resp.ok || !json.success) {
      throw new Error(json.error || "Failed to fetch video info.");
    }

    populateInfo(json.data);
    showInfoPanel("info");
  } catch (err) {
    showInfoPanel("none");
    showToast(err.message || "Something went wrong. Try again.", "error");
  } finally {
    state.isFetching = false;
    setFetchLoading(false);
  }
}

/* ── UI State Helpers ─────────────────────────────────────── */
function setFetchLoading(loading) {
  const txtEl = fetchBtn.querySelector(".fetch-btn-text");
  const iconEl = fetchBtn.querySelector(".fetch-btn-icon");
  const spinEl = fetchBtn.querySelector(".fetch-spinner");
  fetchBtn.disabled = loading;
  txtEl.classList.toggle("hidden", loading);
  iconEl.classList.toggle("hidden", loading);
  spinEl.classList.toggle("hidden", !loading);
}

function showInfoPanel(mode) {
  // mode: "skeleton" | "info" | "none"
  infoPanel.classList.remove("hidden");
  skeleton.classList.add("hidden");
  videoInfo.classList.add("hidden");

  if (mode === "skeleton") {
    skeleton.classList.remove("hidden");
  } else if (mode === "info") {
    videoInfo.classList.remove("hidden");
  } else {
    infoPanel.classList.add("hidden");
  }
}

function resetPanel() {
  showInfoPanel("none");
  urlInput.value = "";
  clearBtn.classList.add("hidden");
  state.currentUrl = "";
  state.currentQuality = null;
  progressWrap.classList.add("hidden");
  urlInput.focus();
}

/* ── Populate Video Info ──────────────────────────────────── */
function populateInfo(data) {
  // Thumbnail
  videoThumb.src = data.thumbnail || "";
  videoThumb.alt = data.title;
  videoDuration.textContent = data.duration || "";

  // Meta
  videoTitle.textContent = data.title;
  videoUploader.textContent = data.uploader;

  // Stats - Dynamically styled with modern vector SVGs
  if (data.view_count) {
    videoViews.innerHTML = `<svg class="inline-block shrink-0 w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg><span>${Number(data.view_count).toLocaleString()} views</span>`;
    videoViews.classList.remove("hidden");
  } else {
    videoViews.innerHTML = "";
    videoViews.classList.add("hidden");
  }

  const formattedDate = formatDate(data.upload_date);
  if (formattedDate) {
    videoDate.innerHTML = `<svg class="inline-block shrink-0 w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg><span>${formattedDate}</span>`;
    videoDate.classList.remove("hidden");
  } else {
    videoDate.innerHTML = "";
    videoDate.classList.add("hidden");
  }

  if (data.estimated_size) {
    videoSize.innerHTML = `<svg class="inline-block shrink-0 w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg><span>~${data.estimated_size}</span>`;
    videoSize.classList.remove("hidden");
  } else {
    videoSize.innerHTML = "";
    videoSize.classList.add("hidden");
  }

  // Qualities
  state.mp4Qualities = data.mp4_qualities || [];
  state.mp3Qualities = data.mp3_qualities || [];

  buildQualityChips(mp4Grid, state.mp4Qualities, "mp4");
  buildQualityChips(mp3Grid, state.mp3Qualities, "mp3");

  // Default format
  selectFormat("mp4");
}

function formatDate(raw) {
  if (!raw || raw.length < 8) return "";
  const y = raw.slice(0, 4), m = raw.slice(4, 6), d = raw.slice(6, 8);
  try {
    return new Date(`${y}-${m}-${d}`).toLocaleDateString("en-US", {
      year: "numeric", month: "short", day: "numeric",
    });
  } catch { return ""; }
}

/* ── Quality Chips ────────────────────────────────────────── */
function buildQualityChips(container, qualities, format) {
  container.innerHTML = "";
  qualities.forEach((q, i) => {
    const chip = document.createElement("button");
    chip.className = "quality-chip" + (i === 0 ? " selected" : "");
    chip.textContent = q === "best" ? "✦ Best" : q;
    chip.dataset.quality = q;
    chip.addEventListener("click", () => selectQuality(container, chip, q));
    container.appendChild(chip);
  });
  // Set first as default selected
  if (qualities.length) {
    state.currentQuality = qualities[0];
  }
}

function selectQuality(container, chip, quality) {
  container.querySelectorAll(".quality-chip").forEach(c => c.classList.remove("selected"));
  chip.classList.add("selected");
  state.currentQuality = quality;
}

/* ── Format Toggle ────────────────────────────────────────── */
btnMp4.addEventListener("click", () => selectFormat("mp4"));
btnMp3.addEventListener("click", () => selectFormat("mp3"));

function selectFormat(fmt) {
  state.currentFormat = fmt;
  btnMp4.classList.toggle("active", fmt === "mp4");
  btnMp3.classList.toggle("active", fmt === "mp3");
  btnMp4.setAttribute("aria-pressed", fmt === "mp4" ? "true" : "false");
  btnMp3.setAttribute("aria-pressed", fmt === "mp3" ? "true" : "false");
  mp4Grid.classList.toggle("hidden", fmt !== "mp4");
  mp3Grid.classList.toggle("hidden", fmt !== "mp3");

  // Reset quality to first chip of new format
  const activeGrid = fmt === "mp4" ? mp4Grid : mp3Grid;
  const firstChip = activeGrid.querySelector(".quality-chip");
  if (firstChip) {
    activeGrid.querySelectorAll(".quality-chip").forEach(c => c.classList.remove("selected"));
    firstChip.classList.add("selected");
    state.currentQuality = firstChip.dataset.quality;
  }
}

/* ── Download ─────────────────────────────────────────────── */
downloadBtn.addEventListener("click", startDownload);

async function startDownload() {
  if (state.isDownloading) return;
  if (!state.currentUrl) {
    showToast("No URL loaded. Fetch a video first.", "error");
    return;
  }
  if (!state.currentQuality) {
    showToast("Please select a quality.", "error");
    return;
  }

  state.isDownloading = true;
  setDownloadLoading(true);
  showProgress(true, "Requesting download from server…");

  // Fake progress animation
  const fakeProgress = animateFakeProgress();

  try {
    const resp = await fetch("/api/download", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        url: state.currentUrl,
        format: state.currentFormat,
        quality: state.currentQuality,
      }),
    });

    if (!resp.ok) {
      // Parse JSON error
      let errMsg = "Download failed.";
      try {
        const j = await resp.json();
        errMsg = j.error || errMsg;
      } catch (_) {}
      throw new Error(errMsg);
    }

    // Server returned a file — trigger browser download
    clearInterval(fakeProgress);
    progressBar.style.width = "100%";
    progressLabel.textContent = "Download complete! Saving file…";

    const blob = await resp.blob();

    // Extract filename from Content-Disposition header
    let filename = "download." + state.currentFormat;
    const cd = resp.headers.get("Content-Disposition");
    if (cd) {
      const match = cd.match(/filename\*?=(?:UTF-8'')?["']?([^"';\n]+)/i);
      if (match) filename = decodeURIComponent(match[1].replace(/['"]/g, ""));
    }

    // Trigger native browser download
    const blobUrl = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = blobUrl;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(blobUrl), 5000);

    showToast(`${filename} — download started!`, "success");

    setTimeout(() => {
      showProgress(false);
    }, 2000);

  } catch (err) {
    clearInterval(fakeProgress);
    progressBar.style.width = "0%";
    showProgress(false);
    showToast(err.message || "Download failed. Try again.", "error");
  } finally {
    state.isDownloading = false;
    setDownloadLoading(false);
  }
}

function setDownloadLoading(loading) {
  const labelEl = downloadBtn.querySelector(".dl-label");
  const iconEl  = downloadBtn.querySelector(".dl-icon");
  const spinEl  = downloadBtn.querySelector(".dl-spinner");
  downloadBtn.disabled = loading;
  labelEl.textContent = loading ? "Downloading…" : "Download Now";
  iconEl.classList.toggle("hidden", loading);
  spinEl.classList.toggle("hidden", !loading);
}

function showProgress(visible, label = "") {
  progressWrap.classList.toggle("hidden", !visible);
  if (visible) {
    progressBar.style.width = "0%";
    progressLabel.textContent = label;
  }
}

function animateFakeProgress() {
  let pct = 0;
  const stages = [
    { target: 20, speed: 400, label: "Fetching video stream…" },
    { target: 55, speed: 300, label: "Downloading from YouTube…" },
    { target: 80, speed: 500, label: "Processing & converting…" },
    { target: 93, speed: 800, label: "Finalizing file…" },
  ];
  let stageIdx = 0;

  const interval = setInterval(() => {
    const stage = stages[stageIdx];
    if (!stage) return;

    pct = Math.min(pct + (Math.random() * 3 + 1), stage.target);
    progressBar.style.width = pct + "%";
    progressLabel.textContent = stage.label;

    if (pct >= stage.target) stageIdx++;
  }, 250);

  return interval;
}

/* ── Init ──────────────────────────────────────────────────── */
initTheme();
