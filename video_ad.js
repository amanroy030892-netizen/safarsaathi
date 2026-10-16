/**
 * SafarSaathi Profile Home Video Ad & Sound Engine
 * Supports Video Ads up to 1.5 minutes (90 seconds) with Audio.
 * Automatically displays on Home/Landing (Login & Register).
 * Automatically stops playback and hides when user navigates or logs in.
 */

let uploadedProfileVideoData = null;
let uploadedProfileVideoName = '';
let uploadedProfileVideoDuration = 0;

function initProfileHomeVideoAd() {
  const savedAd = localStorage.getItem('ss_profile_video_ad');
  const vidPlayer = document.getElementById('profile-video-player');
  const titleEl = document.getElementById('profile-video-title');

  if (savedAd) {
    try {
      const parsed = JSON.parse(savedAd);
      if (vidPlayer && parsed.src) vidPlayer.src = parsed.src;
      if (titleEl && parsed.title) titleEl.innerText = '🚗 ' + parsed.title;
    } catch(e){}
  }

  if (vidPlayer) {
    vidPlayer.volume = 1.0;
    vidPlayer.muted = false;
    // Enforce max 1.5 minutes (90 seconds)
    vidPlayer.ontimeupdate = function() {
      if (vidPlayer.currentTime >= 90) {
        vidPlayer.currentTime = 0;
        vidPlayer.play();
      }
    };
  }
}

function toggleProfileVideoSound() {
  const vid = document.getElementById('profile-video-player');
  const btn = document.getElementById('btn-toggle-profile-video-sound');
  if (!vid) return;

  if (vid.muted || vid.volume === 0) {
    vid.muted = false;
    vid.volume = 1.0;
    vid.play().catch(() => {});
    if (btn) btn.innerText = '🔊 Sound ON';
    if (typeof showToast === 'function') showToast('🔊 Audio Enabled (Full Sound)', '#15803d');
  } else {
    vid.muted = true;
    if (btn) btn.innerText = '🔇 Mute';
    if (typeof showToast === 'function') showToast('🔇 Video Muted', '#64748b');
  }
}

function stopProfileHomeVideoAd() {
  const vid = document.getElementById('profile-video-player');
  if (vid) {
    try {
      vid.pause();
      vid.currentTime = 0;
    } catch(e){}
  }
  const adBox = document.getElementById('profile-home-video-ad-box');
  if (adBox) {
    adBox.style.display = 'none';
  }
}

function resumeProfileHomeVideoAdIfNeeded() {
  const user = typeof getActiveUserProfile === 'function' ? getActiveUserProfile() : null;
  const adBox = document.getElementById('profile-home-video-ad-box');
  if (!user) {
    if (adBox) adBox.style.display = 'block';
  } else {
    stopProfileHomeVideoAd();
  }
}

function openProfileVideoAdUploadModal() {
  const modal = document.getElementById('profile-video-upload-modal');
  if (modal) modal.style.display = 'flex';
}

function closeProfileVideoAdUploadModal() {
  const modal = document.getElementById('profile-video-upload-modal');
  if (modal) modal.style.display = 'none';
}

function handleProfileVideoAdUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  uploadedProfileVideoName = file.name;
  const reader = new FileReader();
  reader.onload = function(e) {
    uploadedProfileVideoData = e.target.result;

    // Check video duration with temp video element
    const tempVid = document.createElement('video');
    tempVid.preload = 'metadata';
    tempVid.src = uploadedProfileVideoData;
    tempVid.onloadedmetadata = function() {
      uploadedProfileVideoDuration = Math.round(tempVid.duration || 0);
      const badge = document.getElementById('p-video-status-badge');
      const label = document.getElementById('p-video-file-label');

      if (badge) {
        badge.style.display = 'block';
        if (uploadedProfileVideoDuration > 95) {
          badge.innerText = `⚠️ Duration: ${uploadedProfileVideoDuration}s (Will play first 1.5 minutes)`;
          badge.style.color = '#f59e0b';
        } else {
          badge.innerText = `✓ Valid Video: ${uploadedProfileVideoDuration}s with Sound!`;
          badge.style.color = '#15803d';
        }
      }
      if (label) {
        label.innerText = '✓ Change Video (' + uploadedProfileVideoDuration + 's)';
        label.style.background = '#15803d';
      }
    };

    if (typeof showToast === 'function') showToast('✓ Video file loaded! Ready to save.', '#15803d');
  };
  reader.readAsDataURL(file);
}

function submitProfileVideoAd() {
  const title = (document.getElementById('p-video-title-input')?.value || '').trim();
  if (!uploadedProfileVideoData) {
    alert('Please choose a video file (MP4/WebM) up to 1.5 minutes!');
    return;
  }

  const adObj = {
    src: uploadedProfileVideoData,
    title: title || 'Featured Video Ad',
    duration: uploadedProfileVideoDuration,
    timestamp: new Date().toISOString()
  };

  try {
    localStorage.setItem('ss_profile_video_ad', JSON.stringify(adObj));
  } catch(e) {
    console.warn('Storage limit reached, keeping in active session');
  }

  const vidPlayer = document.getElementById('profile-video-player');
  const titleEl = document.getElementById('profile-video-title');
  if (vidPlayer) {
    vidPlayer.src = uploadedProfileVideoData;
    vidPlayer.muted = false;
    vidPlayer.volume = 1.0;
    vidPlayer.play().catch(() => {});
  }
  if (titleEl) {
    titleEl.innerText = '🚗 ' + (title || 'Featured Video Ad');
  }

  closeProfileVideoAdUploadModal();
  if (typeof showToast === 'function') showToast('🎉 Video Ad published with Sound (Up to 1.5 Min)!', '#15803d');
}
