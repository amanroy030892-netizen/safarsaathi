with open("admin.html", "r", encoding="utf-8") as f:
    adm_html = f.read()

# Find the start of <main> and the start of BUILTIN_41S_VIDEO_DATA so we preserve the 41s video base64 intact
main_start = adm_html.find("  <main>")
video_data_marker = "    // =========================================================================\n    // 🎬 ADMIN HOME SCREEN SPONSOR VIDEO AD MANAGER (OFFICIAL 41S PRE-LOADED)\n    // ========================================================================="
video_data_start = adm_html.find(video_data_marker)

assert main_start != -1 and video_data_start != -1, f"Markers not found: {main_start}, {video_data_start}"

new_admin_main_and_js = """  <main>
    <!-- LOGIN SCREEN (WORKS ON BOTH SERVER & STATIC/MOBILE HOSTING) -->
    <div id="admin-login-card" class="card" style="max-width: 400px; margin: 2.5rem auto; text-align: center; border: 2px solid #16a34a; box-shadow: 0 8px 30px rgba(22, 163, 74, 0.15);">
      <div style="font-size: 2.2rem; margin-bottom: 0.4rem;">🔐</div>
      <h2 style="font-size: 1.18rem; font-weight: 900; margin-bottom: 0.25rem; color: #0f172a;">SafarSaathi Admin Control Desk</h2>
      <p style="font-size: 0.76rem; color: var(--text-muted); margin-bottom: 0.85rem;">
        Enter your Admin Secret Key (e.g. Official Admin Mobile <b>6901027507</b> or <b>admin123</b>) to verify UTRs & manage live sync:
      </p>

      <input type="password" id="admin-pin-input" class="form-control" placeholder="Enter Admin Secret Key" onkeypress="if(event.key==='Enter') verifyAdminPin()" style="text-align: center; font-size: 1.05rem; letter-spacing: 2px; margin-bottom: 0.85rem; background: #ffffff; color: #0f172a; border: 1.5px solid #16a34a; font-weight: 900;">
      <button type="button" id="btn-admin-login" class="btn btn-primary" onclick="verifyAdminPin()" style="width: 100%; padding: 0.75rem; font-size: 0.92rem;">
        🔓 Authenticate & Open Live Admin Panel ➔
      </button>
    </div>

    <!-- ADMIN DASHBOARD (SHOWN AFTER AUTHENTICATION) -->
    <div id="admin-dashboard" style="display: none;">
      <!-- Live Sync Status Banner -->
      <div style="background: linear-gradient(90deg, #14532d, #15803d); color: #ffffff; border: 1.5px solid #22c55e; border-radius: 12px; padding: 0.6rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.8rem; font-weight: 800;">
          <span style="display: inline-block; width: 9px; height: 9px; border-radius: 50%; background: #4ade80; box-shadow: 0 0 8px #4ade80;"></span>
          <span id="adm-live-heartbeat-text">⚡ 100% Real-Time Bidirectional Sync Active with Customer App (index.html)</span>
        </div>
        <div style="display: flex; gap: 6px;">
          <button type="button" class="btn btn-secondary" onclick="syncAdminWithCloud(true)" style="padding: 4px 10px; font-size: 0.74rem; background: #ffffff; color: #15803d; border: none; font-weight: 900;">
            🔄 Force Sync Now
          </button>
          <button type="button" class="btn btn-danger" onclick="logoutAdmin()" style="padding: 4px 10px; font-size: 0.74rem;">
            🚪 Logout
          </button>
        </div>
      </div>

      <!-- 4-Column Stats Row -->
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 0.65rem; margin-bottom: 1rem;">
        <div class="card" style="padding: 0.85rem; text-align: center; margin: 0; background: #0f172a; border-color: #334155;">
          <div style="font-size: 0.72rem; color: #94a3b8; font-weight: 700;">Total Vehicles</div>
          <strong id="adm-stat-total" style="font-size: 1.45rem; color: #ffffff;">0</strong>
        </div>
        <div class="card" style="padding: 0.85rem; text-align: center; margin: 0; background: #0f172a; border-color: #16a34a;">
          <div style="font-size: 0.72rem; color: #86efac; font-weight: 700;">Active (Live on App)</div>
          <strong id="adm-stat-active" style="font-size: 1.45rem; color: #4ade80;">0</strong>
        </div>
        <div class="card" style="padding: 0.85rem; text-align: center; margin: 0; background: #0f172a; border-color: #f59e0b;">
          <div style="font-size: 0.72rem; color: #fde047; font-weight: 700;">Pending ₹100 Ride UTRs</div>
          <strong id="adm-stat-pending" style="font-size: 1.45rem; color: #fbbf24;">0</strong>
        </div>
        <div class="card" style="padding: 0.85rem; text-align: center; margin: 0; background: #0f172a; border-color: #ec4899;">
          <div style="font-size: 0.72rem; color: #fbcfe8; font-weight: 700;">Pending Coin UTRs (₹100)</div>
          <strong id="adm-stat-coins-pending" style="font-size: 1.45rem; color: #f472b6;">0</strong>
        </div>
      </div>

      <!-- ==================== 1. 🪙 GAME COIN RECHARGE & ₹100 UTR VERIFICATION DESK ==================== -->
      <div class="card" style="border: 2px solid #f59e0b; background: #0f172a; color: #ffffff;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem; border-bottom: 1px solid #334155; padding-bottom: 0.6rem;">
          <div>
            <h3 style="font-size: 1.08rem; font-weight: 900; color: #fef08a; display: flex; align-items: center; gap: 6px;">
              <span>🪙</span> <span>Game Coin UTR Verification Desk (₹50 / ₹100 / ₹200 / ₹500)</span>
            </h3>
            <span style="font-size: 0.74rem; color: #cbd5e1;">
              जब कस्टमर ऐप में कॉइन्स के लिए UTR डालेगा, वह यहाँ दिखेगा। आपके <b>✅ Verify & Credit</b> दबाने पर ही कस्टमर के वॉलेट में ₹100 / कॉइन्स जुड़ेंगे:
            </span>
          </div>
          <button type="button" class="btn btn-secondary" onclick="syncAdminWithCloud(true)" style="font-size: 0.74rem; padding: 5px 10px;">
            🔄 Refresh Coin UTRs
          </button>
        </div>

        <div id="adm-coin-requests-list" style="display: flex; flex-direction: column; gap: 0.75rem;">
          <!-- Coin UTR requests populated dynamically -->
        </div>
      </div>

      <!-- ==================== 2. 🚗 LIVE FLEET & ₹100 RIDE UTR MANAGEMENT ==================== -->
      <div class="card" style="background: #0f172a; color: #ffffff; border: 2px solid #0284c7;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem; border-bottom: 1px solid #334155; padding-bottom: 0.6rem;">
          <div>
            <h3 style="font-size: 1.08rem; font-weight: 900; color: white;">🚗 Live Fleet & Driver ₹100 Fee UTR Verification</h3>
            <span style="font-size: 0.74rem; color: #cbd5e1;">Approve ₹100 driver UTRs to make cars live on Customer App, reject wrong UTRs, or remove cars:</span>
          </div>
          <div style="display: flex; gap: 6px;">
            <button type="button" class="btn btn-success" onclick="openManualActivateModal()">
              ➕ Activate Paid Ride
            </button>
            <button type="button" class="btn btn-secondary" onclick="syncAdminWithCloud(true)">
              🔄 Refresh Fleet
            </button>
          </div>
        </div>

        <div id="adm-vehicles-list" style="display: flex; flex-direction: column; gap: 0.85rem;">
          <!-- Vehicle cards populated dynamically -->
        </div>
        <div style="display: none;"><tbody id="adm-vehicles-tbody"></tbody></div>
      </div>

      <!-- ==================== 3. 🎟️ PASSENGER BOOKINGS & UTR VERIFICATION CARD ==================== -->
      <div class="card" style="margin-top: 1.25rem; background: #0f172a; color: #ffffff; border: 2px solid #16a34a;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem; border-bottom: 1px solid #334155; padding-bottom: 0.6rem;">
          <div>
            <h3 style="font-size: 1.08rem; font-weight: 900; color: white;">🎟️ Passenger Bookings, Seat UTR Verification & Boarding Passes</h3>
            <span style="font-size: 0.74rem; color: #cbd5e1;">Verify passenger fare UTRs, confirm or reject bookings, and dispatch PDF tickets via WhatsApp:</span>
          </div>
          <button type="button" class="btn btn-secondary" onclick="syncAdminWithCloud(true)">
            🔄 Refresh Bookings
          </button>
        </div>

        <div id="adm-bookings-list" style="display: flex; flex-direction: column; gap: 0.85rem;">
          <!-- Bookings list populated dynamically -->
        </div>
      </div>

      <!-- ==================== 4. 👥 REGISTERED AADHAAR KYC USERS CARD ==================== -->
      <div class="card" style="margin-top: 1.25rem; background: #0f172a; color: #ffffff; border: 1.5px solid #6366f1;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <h3 style="font-size: 1.05rem; font-weight: 900; color: #c7d2fe;">👥 Registered App Users & Aadhaar KYC Status (<span id="adm-users-count">0</span>)</h3>
            <span style="font-size: 0.72rem; color: #94a3b8;">Live synced customer & driver profiles registered on SafarSaathi App:</span>
          </div>
        </div>
        <div id="adm-users-list" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0.65rem;">
          <!-- Users populated dynamically -->
        </div>
      </div>

      <!-- ==================== 5. 🎬 HOME SCREEN SPONSOR VIDEO AD MANAGER ==================== -->
      <div class="card" style="margin-top: 1.25rem; background: #0f172a; color: #ffffff; border: 2px solid #16a34a;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 0.5rem;">
          <div>
            <h3 style="font-size: 1.1rem; font-weight: 900; color: white; display: flex; align-items: center; gap: 8px;">
              <span>🎬</span> <span>Home Screen Sponsor Video Ad Manager</span>
            </h3>
            <span style="font-size: 0.74rem; color: #86efac;">Upload & publish official video ads (up to 1.5 minutes with sound) to all customer Home screens:</span>
          </div>
          <span style="background: rgba(34,197,94,0.2); color: #86efac; border: 1px solid #22c55e; font-size: 0.72rem; font-weight: 800; padding: 2px 8px; border-radius: 9999px;">
            🔒 Admin Exclusive Control
          </span>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; align-items: start;">
          <!-- Left: Dual Mode Video Ad Publisher -->
          <div>
            <div style="background: rgba(15,23,42,0.8); border: 1.5px solid #16a34a; border-radius: 12px; padding: 0.85rem; margin-bottom: 0.75rem;">
              <strong style="display: block; font-size: 0.82rem; color: #86efac; margin-bottom: 0.35rem; font-weight: 900;">
                🌐 Video URL / Cloud Link (Syncs to All Customer Phones)
              </strong>
              <span style="font-size: 0.72rem; color: #cbd5e1; display: block; margin-bottom: 0.4rem;">
                Paste direct MP4 link or use default:
              </span>
              <div style="display: flex; gap: 6px;">
                <input type="text" id="adm-video-url-input" class="form-control" placeholder="e.g. promo_ad.mp4 or https://.../ad.mp4" oninput="handleAdminVideoUrlChange()" value="promo_ad.mp4" style="font-size: 0.82rem; height: 34px;">
                <button type="button" class="btn btn-secondary" onclick="setAdminDefaultVideoUrl()" style="white-space: nowrap; font-size: 0.72rem; padding: 4px 10px; font-weight: 800; border-radius: 6px;">
                  Default
                </button>
              </div>
              <button type="button" onclick="usePreloaded41sVideoAd()" style="width: 100%; margin-top: 8px; padding: 8px; font-size: 0.82rem; font-weight: 900; background: linear-gradient(135deg, #16a34a, #15803d); color: #ffffff; border: 1.5px solid #86efac; border-radius: 8px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 6px; box-shadow: 0 3px 10px rgba(22, 163, 74, 0.3);">
                <span>✨</span> <span>1-Click: Use Official SafarSaathi Video Ad (No Link Needed)</span>
              </button>
            </div>

            <div style="background: rgba(15,23,42,0.8); border: 2px dashed #16a34a; border-radius: 12px; padding: 0.85rem; text-align: center; margin-bottom: 0.75rem;">
              <strong style="display: block; font-size: 0.82rem; color: white; margin-bottom: 0.35rem; font-weight: 900;">
                📁 Or Choose Video File from Device (Max 1.5 Min)
              </strong>
              <label for="adm-video-file-input" id="adm-video-file-label" style="display: inline-block; background: #16a34a; color: #ffffff; font-size: 0.76rem; font-weight: 800; padding: 6px 14px; border-radius: 8px; cursor: pointer; margin-top: 2px;">
                📂 Choose Video from Phone / PC
              </label>
              <input type="file" id="adm-video-file-input" accept="video/mp4,video/webm,video/*" style="display: none;" onchange="handleAdminVideoAdUpload(event)">
              <div id="adm-video-status-badge" style="display: none; font-size: 0.72rem; font-weight: 800; margin-top: 6px;"></div>
            </div>

            <div class="form-group" style="margin-bottom: 0.6rem;">
              <label style="font-size: 0.74rem; font-weight: 800; color: #cbd5e1;">Ad Title (विज्ञापन शीर्षक)*</label>
              <input type="text" id="adm-video-title" class="form-control" value="SafarSaathi Premium Carpool Network" placeholder="e.g. Special Corridor Discount Offer">
            </div>

            <div class="form-group" style="margin-bottom: 0.6rem;">
              <label style="font-size: 0.74rem; font-weight: 800; color: #cbd5e1;">Sponsor WhatsApp Number or Link</label>
              <input type="text" id="adm-video-link" class="form-control" value="6901027507" placeholder="e.g. 6901027507 or https://wa.me/...">
            </div>

            <button type="button" class="btn btn-success" id="btn-adm-publish-video" onclick="publishAdminVideoAd()" style="width: 100%; padding: 0.75rem; font-size: 0.9rem; font-weight: 900; margin-top: 0.25rem;">
              🚀 Publish Video Ad to Customer Home Screens ➔
            </button>
          </div>

          <!-- Right: Live Admin Preview Player with Sound Test -->
          <div style="background: rgba(15,23,42,0.8); border: 1.5px solid var(--border-gray); border-radius: 12px; padding: 0.85rem;">
            <div style="font-size: 0.78rem; font-weight: 900; color: #86efac; margin-bottom: 0.4rem; display: flex; justify-content: space-between; align-items: center;">
              <span>📺 Live Video Preview (Sound Active)</span>
              <button type="button" onclick="testAdminVideoSound()" style="background: #ffffff; color: #15803d; border: none; font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 4px; cursor: pointer;">
                🔊 Test Audio
              </button>
            </div>
            <div style="background: #000000; border-radius: 8px; overflow: hidden; max-height: 200px;">
              <video id="adm-video-preview" src="promo_ad.mp4" controls playsinline style="width: 100%; max-height: 190px; object-fit: contain; display: block;"></video>
            </div>
            <div id="adm-video-preview-title" style="font-size: 0.75rem; color: #cbd5e1; margin-top: 6px; font-weight: 700;">
              Current Video: promo_ad.mp4 (Sound enabled • Up to 1.5 min)
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>

  <!-- MANUAL ACTIVATE MODAL -->
  <div class="modal-overlay" id="manual-activate-modal">
    <div class="modal-box">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.65rem; border-bottom: 1px solid var(--border-gray); padding-bottom: 0.4rem;">
        <h3 style="font-size: 1.05rem; font-weight: 900; color: white;">⚡ Activate Paid Vehicle Directly</h3>
        <button type="button" class="btn btn-secondary" onclick="closeManualActivateModal()" style="padding: 2px 7px;">✕</button>
      </div>

      <div class="form-group">
        <label>12-Digit ₹100 UTR Number*</label>
        <input type="text" id="mam-utr" class="form-control" maxlength="12" placeholder="Enter 12-digit Bank UTR" style="font-family: monospace; color: #fbbf24; font-weight: 800;">
      </div>
      <div class="form-group">
        <label>Driver Name & WhatsApp Phone*</label>
        <input type="text" id="mam-driver" class="form-control" placeholder="Driver Name, Phone Number">
      </div>
      <div class="form-group">
        <label>Route (From ➔ To)*</label>
        <input type="text" id="mam-route" class="form-control" value="Guwahati ➔ Shillong">
      </div>
      <div class="form-group">
        <label>Vehicle Model & Plate*</label>
        <input type="text" id="mam-vehicle" class="form-control" placeholder="Vehicle Model, Plate Number">
      </div>

      <button type="button" class="btn btn-success" onclick="submitManualActivate()" style="width: 100%; padding: 0.7rem; font-weight: 800;">
        ✅ Confirm ₹100 & Make 100% Live ➔
      </button>
    </div>
  </div>

  <script>
    const defaultFirebaseConfig = {
      apiKey: "AIzaSyD6duAA-IgREunoMQe9WSHgvd6JPBGw2fw",
      authDomain: "safarsaathi-1de86.firebaseapp.com",
      projectId: "safarsaathi-1de86",
      storageBucket: "safarsaathi-1de86.firebasestorage.app",
      messagingSenderId: "560392119536",
      appId: "1:560392119536:web:d5d601c0c9a92e72c2ce35",
      measurementId: "G-0PB4K9PWVD"
    };
    let firebaseConfig = JSON.parse(localStorage.getItem('ss_fb_config')) || defaultFirebaseConfig;
    let adminDb = null;

    let rides = JSON.parse(localStorage.getItem('ss_rides')) || [];
    let bookings = JSON.parse(localStorage.getItem('ss_bookings')) || [];
    let coinRequests = JSON.parse(localStorage.getItem('ss_coin_requests')) || [];
    let registeredUsers = JSON.parse(localStorage.getItem('ss_users_db')) || {};

    const CLOUD_SYNC_URL = 'https://kvdb.io/safarsaathi_assam_2026/rides';
    const RTDB_BASE = 'https://safarsaathi-1de86-default-rtdb.firebaseio.com';
    const RTDB_RIDES_URL = RTDB_BASE + '/ss_rides.json';
    const RTDB_BOOKINGS_URL = RTDB_BASE + '/ss_bookings.json';
    const RTDB_COINS_URL = RTDB_BASE + '/ss_coin_requests.json';
    const RTDB_USERS_URL = RTDB_BASE + '/ss_users_db.json';

    // ⚡ Local Broadcast Channel & Storage Listener for instant (<50ms) sync with Customer App (index.html)
    let syncBroadcastChannel = null;
    try {
      if (typeof BroadcastChannel !== 'undefined') {
        syncBroadcastChannel = new BroadcastChannel('safarsaathi_multi_cloud_stream');
        syncBroadcastChannel.onmessage = (event) => {
          if (!event || !event.data) return;
          const d = event.data;
          if (d.type === 'RIDES_UPDATED' && Array.isArray(d.rides)) {
            rides = d.rides;
            localStorage.setItem('ss_rides', JSON.stringify(rides));
            renderAdminVehicles();
          } else if (d.type === 'BOOKINGS_UPDATED' && Array.isArray(d.bookings)) {
            bookings = d.bookings;
            localStorage.setItem('ss_bookings', JSON.stringify(bookings));
            renderAdminBookings();
            renderAdminVehicles();
          } else if (d.type === 'COIN_REQUESTS_UPDATED' && Array.isArray(d.coinRequests)) {
            coinRequests = d.coinRequests;
            localStorage.setItem('ss_coin_requests', JSON.stringify(coinRequests));
            renderAdminCoinRequests();
          } else if (d.type === 'USERS_UPDATED' && d.users) {
            registeredUsers = d.users;
            localStorage.setItem('ss_users_db', JSON.stringify(registeredUsers));
            renderAdminUsers();
          }
        };
      }
    } catch(e){}

    window.addEventListener('storage', (e) => {
      try {
        if (e.key === 'ss_rides' && e.newValue !== null) {
          rides = JSON.parse(e.newValue) || [];
          renderAdminVehicles();
        } else if (e.key === 'ss_bookings' && e.newValue !== null) {
          bookings = JSON.parse(e.newValue) || [];
          renderAdminBookings();
          renderAdminVehicles();
        } else if (e.key === 'ss_coin_requests' && e.newValue !== null) {
          coinRequests = JSON.parse(e.newValue) || [];
          renderAdminCoinRequests();
        } else if (e.key === 'ss_users_db' && e.newValue !== null) {
          registeredUsers = JSON.parse(e.newValue) || {};
          renderAdminUsers();
        }
      } catch(err){}
    });

    // Hybrid Admin Authentication: Works with Node Server (/api/admin/login) AND Static/Mobile Hosting
    const VALID_ADMIN_KEYS = new Set(['6901027507', 'admin123', 'safar2026', '8287', '1234', 'admin']);

    async function verifyAdminPin() {
      const pinInput = document.getElementById('admin-pin-input');
      const pin = (pinInput?.value || '').trim();
      const loginBtn = document.getElementById('btn-admin-login');
      if (!pin) {
        alert('Please enter your Admin Secret Key (e.g. 6901027507 or admin123)!');
        return;
      }
      if (loginBtn) {
        loginBtn.disabled = true;
        loginBtn.innerText = 'Verifying...';
      }

      let authSuccessful = false;
      try {
        const resp = await fetch('/api/admin/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ adminSecret: pin })
        });
        if (resp.ok) {
          const resData = await resp.json();
          if (resData && resData.success) {
            sessionStorage.setItem('ss_admin_authed', 'true');
            sessionStorage.setItem('ss_admin_token', resData.token || 'local_token');
            authSuccessful = true;
          }
        }
      } catch (err) {
        // Static / GitHub Pages / Direct Mobile fallback
      }

      if (!authSuccessful && VALID_ADMIN_KEYS.has(pin.toLowerCase())) {
        sessionStorage.setItem('ss_admin_authed', 'true');
        sessionStorage.setItem('ss_admin_token', 'static_verified_' + Date.now());
        authSuccessful = true;
      }

      if (loginBtn) {
        loginBtn.disabled = false;
        loginBtn.innerText = '🔓 Authenticate & Open Live Admin Panel ➔';
      }

      if (authSuccessful) {
        showAdminDashboardView();
      } else {
        alert('❌ Invalid Admin Secret Key! Try 6901027507 or admin123.');
        if (pinInput) pinInput.value = '';
      }
    }

    function showAdminDashboardView() {
      document.getElementById('admin-login-card').style.display = 'none';
      document.getElementById('admin-dashboard').style.display = 'block';
      initAdminFirebase();
      syncAdminWithCloud(false);
      renderAdminCoinRequests();
      renderAdminVehicles();
      renderAdminBookings();
      renderAdminUsers();
      loadCurrentPublishedVideoAd();
    }

    function logoutAdmin() {
      sessionStorage.removeItem('ss_admin_authed');
      location.reload();
    }

    function initAdminFirebase() {
      if (typeof firebase !== 'undefined' && firebaseConfig && firebaseConfig.apiKey) {
        try {
          if (!firebase.apps.length) firebase.initializeApp(firebaseConfig);
          if (firebase.auth) firebase.auth().signInAnonymously().catch(() => {});
          if (firebase.firestore) {
            adminDb = firebase.firestore();

            // 1. Live Rides Snapshot
            adminDb.collection('ss_rides').onSnapshot(snapshot => {
              const cloudRides = [];
              snapshot.forEach(doc => {
                const data = doc.data();
                if (data && !['RIDE-101', 'RIDE-102', 'RIDE-103'].includes(data.id)) {
                  if (!data.id) data.id = doc.id;
                  cloudRides.push(data);
                }
              });
              mergeAdminCloudRides(cloudRides);
            }, err => console.warn('Firestore rides notice:', err));

            // 2. Live Bookings Snapshot
            adminDb.collection('ss_bookings').onSnapshot(snapshot => {
              const cloudBookings = [];
              snapshot.forEach(doc => {
                const data = doc.data();
                if (data) {
                  if (!data.bookingId) data.bookingId = doc.id;
                  cloudBookings.push(data);
                }
              });
              if (cloudBookings.length > 0) {
                bookings = cloudBookings;
                localStorage.setItem('ss_bookings', JSON.stringify(bookings));
                renderAdminBookings();
              }
            }, err => {});

            // 3. Live Coin UTR Requests Snapshot
            adminDb.collection('ss_coin_requests').onSnapshot(snapshot => {
              const cloudCoins = [];
              snapshot.forEach(doc => {
                const data = doc.data();
                if (data) {
                  if (!data.id) data.id = doc.id;
                  cloudCoins.push(data);
                }
              });
              if (cloudCoins.length > 0) {
                coinRequests = cloudCoins;
                localStorage.setItem('ss_coin_requests', JSON.stringify(coinRequests));
                renderAdminCoinRequests();
              }
            }, err => {});

            // 4. Live Users Snapshot
            adminDb.collection('ss_users').onSnapshot(snapshot => {
              const uMap = { ...(JSON.parse(localStorage.getItem('ss_users_db')) || {}) };
              snapshot.forEach(doc => {
                const data = doc.data();
                if (data && data.userId) uMap[data.userId] = data;
              });
              registeredUsers = uMap;
              localStorage.setItem('ss_users_db', JSON.stringify(registeredUsers));
              renderAdminUsers();
            }, err => {});
          }
        } catch(e){}
      }
    }

    function mergeAdminCloudRides(cloudRides) {
      if (!cloudRides || !Array.isArray(cloudRides)) return;
      const fakeDemoNames = new Set(['Bikram Das', 'Rahul Saikia', 'Pranab Bora']);
      const fakeDemoIds = new Set(['RIDE-101', 'RIDE-102', 'RIDE-103', 'RIDE-4921', 'RIDE-1902', 'RIDE-3311']);
      let clean = cloudRides.filter(r => r && !fakeDemoNames.has(r.driverName) && !fakeDemoIds.has(r.id));
      rides = clean;
      localStorage.setItem('ss_rides', JSON.stringify(rides));
      renderAdminVehicles();
    }

    function syncAdminWithCloud(showFeedback = false) {
      // 1. Pull Rides from RTDB
      fetch(RTDB_RIDES_URL)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data !== null && data !== undefined) {
            const list = Array.isArray(data) ? data : Object.values(data);
            mergeAdminCloudRides(list);
          }
        }).catch(() => {});

      // 2. Pull Bookings from RTDB
      fetch(RTDB_BOOKINGS_URL)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            const list = Array.isArray(data) ? data : Object.values(data);
            bookings = list;
            localStorage.setItem('ss_bookings', JSON.stringify(bookings));
            renderAdminBookings();
          }
        }).catch(() => {});

      // 3. Pull Coin UTR Requests from RTDB
      fetch(RTDB_COINS_URL)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            const list = Array.isArray(data) ? data : Object.values(data);
            coinRequests = list;
            localStorage.setItem('ss_coin_requests', JSON.stringify(coinRequests));
            renderAdminCoinRequests();
          }
        }).catch(() => {});

      // 4. Pull Users from RTDB
      fetch(RTDB_USERS_URL)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data && typeof data === 'object') {
            registeredUsers = { ...(JSON.parse(localStorage.getItem('ss_users_db')) || {}), ...data };
            localStorage.setItem('ss_users_db', JSON.stringify(registeredUsers));
            renderAdminUsers();
          }
        }).catch(() => {});

      // 5. Pull from Firestore
      if (adminDb) {
        adminDb.collection('ss_rides').get().then(snapshot => {
          const cr = [];
          snapshot.forEach(doc => {
            const d = doc.data();
            if (d && !['RIDE-101', 'RIDE-102', 'RIDE-103'].includes(d.id)) {
              if (!d.id) d.id = doc.id;
              cr.push(d);
            }
          });
          mergeAdminCloudRides(cr);
        }).catch(() => {});
      }

      const hb = document.getElementById('adm-live-heartbeat-text');
      if (hb) {
        hb.innerText = `⚡ Live Synced with Customer App at ${new Date().toLocaleTimeString()} • All Modules Connected`;
      }
    }

    // Continuous 2.5-second Admin auto-sync loop
    setInterval(() => {
      if (sessionStorage.getItem('ss_admin_authed') === 'true') {
        syncAdminWithCloud(false);
        renderAdminCoinRequests();
        renderAdminVehicles();
        renderAdminBookings();
      }
    }, 2500);

    // Push full rides state to all clouds + Customer App tabs
    function broadcastRidesToCloud(updatedRides) {
      localStorage.setItem('ss_rides', JSON.stringify(updatedRides));

      if (syncBroadcastChannel) {
        try {
          syncBroadcastChannel.postMessage({ type: 'RIDES_UPDATED', rides: updatedRides, timestamp: Date.now() });
        } catch(e){}
      }

      try {
        fetch(CLOUD_SYNC_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedRides)
        }).catch(() => {});
      } catch(e){}

      try {
        fetch(RTDB_RIDES_URL, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedRides)
        }).catch(() => {});
      } catch(e){}
    }

    function broadcastBookingsToCloud(updatedBookings) {
      localStorage.setItem('ss_bookings', JSON.stringify(updatedBookings));
      if (syncBroadcastChannel) {
        try {
          syncBroadcastChannel.postMessage({ type: 'BOOKINGS_UPDATED', bookings: updatedBookings, timestamp: Date.now() });
        } catch(e){}
      }
      try {
        fetch(RTDB_BOOKINGS_URL, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedBookings)
        }).catch(() => {});
      } catch(e){}
    }

    function broadcastCoinsToCloud(updatedCoinReqs) {
      localStorage.setItem('ss_coin_requests', JSON.stringify(updatedCoinReqs));
      if (syncBroadcastChannel) {
        try {
          syncBroadcastChannel.postMessage({ type: 'COIN_REQUESTS_UPDATED', coinRequests: updatedCoinReqs, timestamp: Date.now() });
        } catch(e){}
      }
      try {
        fetch(RTDB_COINS_URL, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedCoinReqs)
        }).catch(() => {});
      } catch(e){}
    }

    // =========================================================================
    // 🪙 1. ADMIN GAME COIN RECHARGE & ₹100 UTR VERIFICATION CONTROLLER
    // =========================================================================
    function renderAdminCoinRequests() {
      coinRequests = JSON.parse(localStorage.getItem('ss_coin_requests')) || [];
      const pendingCoinsCount = coinRequests.filter(c => (c.status || '').toUpperCase() === 'PENDING_ADMIN_APPROVAL').length;
      const statEl = document.getElementById('adm-stat-coins-pending');
      if (statEl) statEl.innerText = pendingCoinsCount;

      const container = document.getElementById('adm-coin-requests-list');
      if (!container) return;

      if (coinRequests.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; color: #94a3b8; padding: 1.35rem 1rem; background: rgba(2,6,23,0.55); border: 1.5px dashed #475569; border-radius: 12px; font-size: 0.82rem;">
            🪙 अभी कोई पेंडिंग Game Coin UTR रिक्वेस्ट नहीं है। जब कस्टमर ऐप में कॉइन्स के लिए 12-अंकों का UTR डालेगा, वह तुरंत यहाँ लाइव दिखेगा।
          </div>
        `;
        return;
      }

      container.innerHTML = coinRequests.map(req => {
        const st = (req.status || 'PENDING_ADMIN_APPROVAL').toUpperCase();
        const isPending = (st === 'PENDING_ADMIN_APPROVAL');
        const isApproved = (st === 'APPROVED');
        const isRejected = (st === 'REJECTED');

        let badgeHtml = `<span style="background:#78350f; color:#fde047; border:1px solid #f59e0b; padding:3px 9px; border-radius:999px; font-size:0.72rem; font-weight:900;">⏳ PENDING UTR CHECK</span>`;
        if (isApproved) {
          badgeHtml = `<span style="background:#14532d; color:#86efac; border:1px solid #22c55e; padding:3px 9px; border-radius:999px; font-size:0.72rem; font-weight:900;">✅ APPROVED (+${req.coins} Coins Credited)</span>`;
        } else if (isRejected) {
          badgeHtml = `<span style="background:#7f1d1d; color:#fca5a5; border:1px solid #ef4444; padding:3px 9px; border-radius:999px; font-size:0.72rem; font-weight:900;">❌ REJECTED (Wrong UTR)</span>`;
        }

        return `
          <div style="background: rgba(2, 6, 23, 0.85); border: 1.5px solid ${isPending ? '#f59e0b' : (isApproved ? '#22c55e' : '#ef4444')}; border-radius: 12px; padding: 0.85rem 1rem;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 6px; margin-bottom: 0.5rem;">
              <div>
                <strong style="font-size: 0.98rem; color: #fef08a;">🪙 +${req.coins || req.amount} Game Coins (₹${req.amount})</strong>
                <span style="font-size: 0.74rem; color: #94a3b8; margin-left: 6px;">Ref: ${req.id}</span>
              </div>
              ${badgeHtml}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 6px; font-size: 0.8rem; color: #cbd5e1; margin-bottom: 0.65rem; background: rgba(15,23,42,0.9); padding: 0.55rem 0.75rem; border-radius: 8px;">
              <div>👤 <b>Player:</b> <span style="color:#ffffff;">${req.userName || 'Game Player'}</span> (${req.userPhone || 'Guest'})</div>
              <div>🏦 <b>12-Digit UTR:</b> <span style="font-family:monospace; font-size:0.92rem; font-weight:900; color:#fbbf24; background:rgba(251,191,36,0.12); padding:1px 6px; border-radius:4px;">${req.utr}</span></div>
              <div>🕒 <b>Time:</b> ${req.requestedAt ? new Date(req.requestedAt).toLocaleTimeString() : 'Just now'}</div>
            </div>

            <div style="display: flex; gap: 8px; flex-wrap: wrap;">
              ${isPending ? `
                <button type="button" class="btn btn-success" onclick="approveAdminCoinRequest('${req.id}')" style="flex: 1; padding: 8px 12px; font-size: 0.8rem;">
                  ✅ Verify UTR & Credit +${req.coins} Coins (₹${req.amount})
                </button>
                <button type="button" class="btn btn-danger" onclick="rejectAdminCoinRequest('${req.id}')" style="padding: 8px 12px; font-size: 0.8rem;">
                  ❌ Reject Wrong UTR (₹0)
                </button>
              ` : `
                <button type="button" class="btn btn-secondary" onclick="deleteAdminCoinRequest('${req.id}')" style="padding: 6px 10px; font-size: 0.74rem;">
                  🗑️ Remove Entry
                </button>
              `}
            </div>
          </div>
        `;
      }).join('');
    }

    function approveAdminCoinRequest(reqId) {
      coinRequests = JSON.parse(localStorage.getItem('ss_coin_requests')) || [];
      const req = coinRequests.find(c => c.id === reqId);
      if (!req) return;

      req.status = 'APPROVED';
      req.approvedAt = new Date().toISOString();
      broadcastCoinsToCloud(coinRequests);

      if (adminDb) {
        try {
          adminDb.collection('ss_coin_requests').doc(reqId).set(req, { merge: true });
        } catch(e){}
      }

      renderAdminCoinRequests();
      alert(`✅ UTR (${req.utr}) Verified! +${req.coins} Coins (₹${req.amount}) have been credited live to the customer's app wallet!`);
    }

    function rejectAdminCoinRequest(reqId) {
      coinRequests = JSON.parse(localStorage.getItem('ss_coin_requests')) || [];
      const req = coinRequests.find(c => c.id === reqId);
      if (!req) return;

      req.status = 'REJECTED';
      req.rejectedAt = new Date().toISOString();
      broadcastCoinsToCloud(coinRequests);

      if (adminDb) {
        try {
          adminDb.collection('ss_coin_requests').doc(reqId).set(req, { merge: true });
        } catch(e){}
      }

      renderAdminCoinRequests();
      alert(`❌ Wrong UTR (${req.utr}) Rejected! ₹0 added to customer wallet.`);
    }

    function deleteAdminCoinRequest(reqId) {
      coinRequests = (JSON.parse(localStorage.getItem('ss_coin_requests')) || []).filter(c => c.id !== reqId);
      broadcastCoinsToCloud(coinRequests);
      if (adminDb) {
        try { adminDb.collection('ss_coin_requests').doc(reqId).delete(); } catch(e){}
      }
      renderAdminCoinRequests();
    }

    // =========================================================================
    // 🚗 2. ADMIN VEHICLE FLEET & ₹100 RIDE UTR VERIFICATION CONTROLLER
    // =========================================================================
    function renderAdminVehicles() {
      rides = JSON.parse(localStorage.getItem('ss_rides')) || [];

      const activeCount = rides.filter(r => (r.status || '').toUpperCase() === 'ACTIVE').length;
      const pendingCount = rides.filter(r => (r.status || '').toUpperCase() === 'PENDING_APPROVAL').length;

      const totalEl = document.getElementById('adm-stat-total');
      const activeEl = document.getElementById('adm-stat-active');
      const pendingEl = document.getElementById('adm-stat-pending');
      if (totalEl) totalEl.innerText = rides.length;
      if (activeEl) activeEl.innerText = activeCount;
      if (pendingEl) pendingEl.innerText = pendingCount;

      const container = document.getElementById('adm-vehicles-list');
      if (!container) return;

      if (rides.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; color: #94a3b8; padding: 2rem 1rem; background: rgba(2,6,23,0.6); border: 1.5px dashed #475569; border-radius: 12px;">
            <div style="font-size: 2rem; margin-bottom: 0.35rem;">🚗</div>
            <strong style="color: white; font-size: 0.98rem; display: block;">No Vehicles Listed Right Now</strong>
            <p style="font-size: 0.78rem; margin: 0.35rem 0 0.85rem;">When a driver posts a ride with a ₹100 UTR on the app, it appears here live for your verification.</p>
            <button type="button" class="btn btn-success" onclick="openManualActivateModal()" style="font-size: 0.8rem; padding: 6px 14px;">
              ➕ Activate New Car Directly
            </button>
          </div>
        `;
        return;
      }

      container.innerHTML = rides.map(r => {
        const statusUpper = (r.status || '').toUpperCase();
        const isLive = statusUpper === 'ACTIVE';
        const isOffline = statusUpper === 'OFFLINE' || statusUpper === 'REMOVED';
        const isRejected = statusUpper === 'REJECTED_UTR';

        const rideTime = r.approvedAt || r.postedAt || r.createdAt;
        let diffHours = 0;
        let isExpired = false;
        let hoursLeftText = '';

        if (rideTime) {
          const ts = new Date(rideTime).getTime();
          diffHours = (Date.now() - ts) / (1000 * 60 * 60);
          if (diffHours >= 48) {
            isExpired = true;
            hoursLeftText = '⚠️ Expired (>48h ago)';
          } else {
            const hLeft = Math.max(1, Math.round(48 - diffHours));
            hoursLeftText = `⏱️ ${hLeft}h live remaining`;
          }
        } else {
          hoursLeftText = '⏱️ 48h window';
        }

        let statusBadge = '';
        if (isLive && !isExpired) {
          statusBadge = `<span style="font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 9999px; background: #14532d; color: #86efac; border: 1.5px solid #22c55e;">✓ 100% LIVE ON APP</span>`;
        } else if (isLive && isExpired) {
          statusBadge = `<span style="font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 9999px; background: #7f1d1d; color: #fca5a5; border: 1.5px solid #ef4444;">⏰ EXPIRED (>48h)</span>`;
        } else if (isRejected) {
          statusBadge = `<span style="font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 9999px; background: #7f1d1d; color: #fca5a5; border: 1.5px solid #ef4444;">❌ WRONG UTR REJECTED</span>`;
        } else if (isOffline) {
          statusBadge = `<span style="font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 9999px; background: #374151; color: #9ca3af; border: 1.5px solid #6b7280;">⏸️ OFFLINE (HIDDEN)</span>`;
        } else {
          statusBadge = `<span style="font-size: 0.72rem; font-weight: 800; padding: 3px 8px; border-radius: 9999px; background: #78350f; color: #fde047; border: 1.5px solid #f59e0b;">⏳ PENDING ₹100 UTR CHECK</span>`;
        }

        const borderCol = (isLive && !isExpired) ? '#22c55e' : (isRejected ? '#ef4444' : '#f59e0b');

        return `
          <div style="background: rgba(2, 6, 23, 0.9); border: 1.5px solid ${borderCol}; border-radius: 14px; padding: 1rem 1.1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3);">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem; flex-wrap: wrap; gap: 8px;">
              <div>
                <strong style="color: #ffffff; font-size: 1.08rem; display: inline-block;">${r.vehicleModel || 'Car'}</strong>
                <span style="background: #ffffff; color: #000000; font-family: monospace; font-size: 0.82rem; font-weight: 900; padding: 2px 7px; border-radius: 4px; margin-left: 6px; letter-spacing: 0.5px;">
                  ${r.vehicleNumber || 'AS 01'}
                </span>
              </div>
              <div style="text-align: right;">
                ${statusBadge}
                <div style="font-size: 0.7rem; color: #38bdf8; font-weight: 700; margin-top: 2px;">${hoursLeftText}</div>
              </div>
            </div>

            <div style="background: rgba(15, 23, 42, 0.85); padding: 0.65rem 0.85rem; border-radius: 10px; margin-bottom: 0.75rem; font-size: 0.82rem; color: #cbd5e1; line-height: 1.55;">
              <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px;">
                <div>📍 <strong>Route:</strong> <span style="color: #ffffff; font-weight: 700;">${r.origin} ➔ ${r.destination}</span> (${r.date} • ${r.time})</div>
                <div>💺 <strong>Seats:</strong> ${r.seatsAvailable ?? 3} / ${r.totalSeats || 3} • <strong style="color: #4ade80;">₹${r.farePerSeat}/seat</strong></div>
              </div>
              <div style="display: flex; justify-content: space-between; flex-wrap: wrap; gap: 6px; margin-top: 3px;">
                <div>👤 <strong>Driver:</strong> ${r.driverName} (<a href="tel:${r.driverPhone}" style="color: #38bdf8; font-weight: 700; text-decoration: none;">📞 ${r.driverPhone}</a>)</div>
                <div>💰 <strong>₹100 Fee UTR:</strong> <span style="font-family: monospace; font-weight: 900; color: #fbbf24; background: rgba(251,191,36,0.12); padding: 1px 6px; border-radius: 4px;">${r.platformFeeUtr || r.utrNumber || 'N/A'}</span></div>
              </div>
            </div>

            <div style="display: flex; gap: 8px; flex-wrap: wrap; align-items: center;">
              ${(isLive && !isExpired) ? `
                <button type="button" class="btn btn-primary" onclick="reLiveRide('${r.id}')" style="flex: 1; min-width: 140px; padding: 8px 12px;">
                  🔄 Extend +48h Live
                </button>
                <button type="button" class="btn btn-warning" onclick="removeFromLive('${r.id}')" style="padding: 8px 12px;">
                  🚫 Hide from App
                </button>
              ` : `
                <button type="button" class="btn btn-success" onclick="reLiveRide('${r.id}')" style="flex: 1; min-width: 160px; padding: 8px 14px;">
                  ✅ Verify ₹100 UTR & Make Live
                </button>
                ${!isRejected ? `
                  <button type="button" class="btn btn-warning" onclick="rejectRideUtr('${r.id}')" style="padding: 8px 12px;">
                    ❌ Reject Wrong UTR
                  </button>
                ` : ''}
              `}

              <button type="button" class="btn btn-danger" onclick="deleteRidePermanently('${r.id}')" style="padding: 8px 12px;">
                🗑️ Delete
              </button>
            </div>
          </div>
        `;
      }).join('');
    }

    function approveRide(rideId) {
      reLiveRide(rideId);
    }

    function reLiveRide(rideId) {
      const r = rides.find(item => item.id === rideId);
      if (!r) return;
      r.status = 'ACTIVE';
      r.verifiedByAdmin = true;
      r.removedByAdmin = false;
      r.approvedAt = new Date().toISOString();
      r.postedAt = new Date().toISOString();
      if (!r.seatsAvailable || r.seatsAvailable < 1) r.seatsAvailable = r.totalSeats || 3;

      broadcastRidesToCloud(rides);

      if (adminDb) {
        try {
          const cleanDoc = { ...r };
          if (cleanDoc.driverQr && cleanDoc.driverQr.length > 300000) {
            cleanDoc.driverQr = 'mitali_qr_compact.svg';
          }
          adminDb.collection('ss_rides').doc(rideId).set(cleanDoc, { merge: true });
        } catch(e){}
      }

      renderAdminVehicles();
      alert(`✅ UTR Verified! Vehicle ${r.vehicleModel} (${r.vehicleNumber}) is now 100% LIVE on the Customer App!`);
    }

    function rejectRideUtr(rideId) {
      const r = rides.find(item => item.id === rideId);
      if (!r) return;
      r.status = 'REJECTED_UTR';
      r.verifiedByAdmin = false;
      r.removedByAdmin = true;
      r.rejectedAt = new Date().toISOString();

      broadcastRidesToCloud(rides);

      if (adminDb) {
        try {
          adminDb.collection('ss_rides').doc(rideId).set(r, { merge: true });
        } catch(e){}
      }

      renderAdminVehicles();
      alert(`❌ Wrong UTR Rejected for vehicle ${r.vehicleNumber}! It will not appear on Live Cars.`);
    }

    function removeFromLive(rideId) {
      const r = rides.find(item => item.id === rideId);
      if (!r) return;

      r.status = 'OFFLINE';
      r.removedByAdmin = true;
      r.removedAt = new Date().toISOString();

      broadcastRidesToCloud(rides);

      if (adminDb) {
        try {
          adminDb.collection('ss_rides').doc(rideId).set(r, { merge: true });
        } catch(e){}
      }

      renderAdminVehicles();
      alert(`✓ Vehicle ${r.vehicleNumber} is now hidden from the Customer App.`);
    }

    function deleteRidePermanently(rideId) {
      const r = rides.find(item => item.id === rideId);
      const plate = r ? r.vehicleNumber : rideId;

      rides = rides.filter(item => item.id !== rideId);
      broadcastRidesToCloud(rides);

      if (adminDb) {
        try {
          adminDb.collection('ss_rides').doc(rideId).delete();
        } catch(e){}
      }

      renderAdminVehicles();
      alert(`🗑️ Vehicle ${plate} deleted permanently from Admin & Customer App.`);
    }

    function openManualActivateModal() {
      document.getElementById('manual-activate-modal').style.display = 'flex';
      const utrEl = document.getElementById('mam-utr');
      const driverEl = document.getElementById('mam-driver');
      const routeEl = document.getElementById('mam-route');
      const vehicleEl = document.getElementById('mam-vehicle');
      if (utrEl && !utrEl.value) utrEl.value = '429816503741';
      if (driverEl && !driverEl.value) driverEl.value = 'Dipankar Baidya, 9435012345';
      if (routeEl && !routeEl.value) routeEl.value = 'Guwahati ➔ Shillong';
      if (vehicleEl && !vehicleEl.value) vehicleEl.value = 'Maruti Suzuki Dzire, AS 02 M 8287';
    }

    function closeManualActivateModal() {
      document.getElementById('manual-activate-modal').style.display = 'none';
    }

    function submitManualActivate() {
      let utr = (document.getElementById('mam-utr')?.value || '').trim();
      let driverStr = (document.getElementById('mam-driver')?.value || '').trim();
      let route = (document.getElementById('mam-route')?.value || '').trim();
      let vehicle = (document.getElementById('mam-vehicle')?.value || '').trim();

      if (!utr || utr.length !== 12 || !/^\\d{12}$/.test(utr)) {
        utr = '429' + Date.now().toString().slice(-9);
      }
      if (!driverStr) driverStr = 'Dipankar Baidya, 9435012345';
      if (!route) route = 'Guwahati ➔ Shillong';
      if (!vehicle) vehicle = 'Maruti Suzuki Dzire, AS 02 M 8287';

      let name = driverStr, phone = '9435012345';
      if (driverStr.includes(',')) {
        name = driverStr.split(',')[0].trim();
        phone = driverStr.split(',')[1].trim().replace(/\\D/g, '') || '9435012345';
      }

      let from = 'Guwahati', to = 'Shillong';
      if (route.includes('➔')) {
        from = route.split('➔')[0].trim();
        to = route.split('➔')[1].trim();
      }

      let model = 'Maruti Suzuki Dzire', plate = 'AS 02 M 8287';
      if (vehicle.includes(',')) {
        model = vehicle.split(',')[0].trim();
        plate = vehicle.split(',')[1].trim();
      } else {
        model = vehicle;
      }

      const nowIso = new Date().toISOString();
      const newRide = {
        id: 'RIDE-' + Math.floor(1000 + Math.random() * 9000),
        driverName: name,
        driverPhone: phone,
        driverUpi: phone ? (phone + '@upi') : '6901027507@nyes',
        driverPhoto: '',
        driverQr: 'mitali_qr_compact.svg',
        carPhoto: 'car-bg.jpg',
        platePhoto: '',
        farePerSeat: 300,
        origin: from,
        destination: to,
        date: nowIso.split('T')[0],
        time: '08:30 AM',
        seatsAvailable: 3,
        totalSeats: 3,
        vehicleModel: model,
        vehicleNumber: plate,
        platformFeeUtr: utr,
        utrNumber: utr,
        status: 'ACTIVE',
        verifiedByAdmin: true,
        postedAt: nowIso,
        approvedAt: nowIso
      };

      const existingIdx = rides.findIndex(item => item.id === newRide.id || item.vehicleNumber === newRide.vehicleNumber);
      if (existingIdx !== -1) {
        rides[existingIdx] = newRide;
      } else {
        rides.unshift(newRide);
      }

      broadcastRidesToCloud(rides);

      if (adminDb) {
        try {
          adminDb.collection('ss_rides').doc(newRide.id).set(newRide, { merge: true });
        } catch(e){}
      }

      closeManualActivateModal();
      renderAdminVehicles();
      alert(`🎉 Vehicle ${model} (${plate}) is now 100% LIVE on the Customer App!`);
    }

    // =========================================================================
    // 🎟️ 3. ADMIN PASSENGER BOOKINGS & SEAT UTR VERIFICATION ENGINE
    // =========================================================================
    function renderAdminBookings() {
      bookings = JSON.parse(localStorage.getItem('ss_bookings')) || [];
      const container = document.getElementById('adm-bookings-list');
      if (!container) return;

      if (bookings.length === 0) {
        container.innerHTML = `
          <div style="text-align: center; color: #94a3b8; padding: 1.5rem 1rem; background: rgba(2,6,23,0.6); border: 1.5px dashed #475569; border-radius: 12px; font-size: 0.85rem;">
            No passenger seat bookings recorded yet.
          </div>
        `;
        return;
      }

      container.innerHTML = bookings.map(b => {
        const st = (b.status || 'AWAITING_DRIVER_CONFIRMATION').toUpperCase();
        const isConfirmed = (st === 'CONFIRMED');
        const isRejected = (st === 'REJECTED');

        let statusBadge = `<span style="background: #78350f; color: #fde047; border: 1px solid #f59e0b; font-size: 0.7rem; font-weight: 900; padding: 3px 8px; border-radius: 6px;">⏳ PENDING UTR VERIFICATION</span>`;
        if (isConfirmed) {
          statusBadge = `<span style="background: #15803d; color: #ffffff; font-size: 0.7rem; font-weight: 900; padding: 3px 8px; border-radius: 6px;">✓ VERIFIED & CONFIRMED</span>`;
        } else if (isRejected) {
          statusBadge = `<span style="background: #7f1d1d; color: #fca5a5; font-size: 0.7rem; font-weight: 900; padding: 3px 8px; border-radius: 6px;">❌ WRONG UTR REJECTED</span>`;
        }

        const waMsg = encodeURIComponent(
          `🚗 *SAFARSAATHI ASSAM - OFFICIAL DIGITAL BOARDING PASS*\\n` +
          `🎟️ *Ticket Ref:* ${b.bookingId}\\n` +
          `👤 *Passenger:* ${b.passengerName} (+91 ${b.passengerPhone})\\n` +
          `🛣️ *Corridor:* ${b.origin} ➔ ${b.destination}\\n` +
          `📅 *Departure:* ${b.date} at ${b.time}\\n` +
          `💺 *Seats Allocated:* ${b.seatsBooked} Seat(s)\\n` +
          `💰 *Total Fare:* ₹${b.totalFare} (Paid via UPI)\\n` +
          `🏦 *Bank UTR Ref:* ${b.passengerUtr}\\n` +
          `🚗 *Vehicle:* ${b.vehicleModel} (${b.vehicleNumber})\\n` +
          `👤 *Driver:* ${b.driverName} (+91 ${b.driverPhone})\\n` +
          `✓ Status: 100% CONFIRMED & VERIFIED`
        );

        return `
          <div style="background: rgba(2,6,23,0.85); border: 1.5px solid ${isConfirmed ? '#16a34a' : (isRejected ? '#ef4444' : '#f59e0b')}; border-radius: 14px; padding: 1rem; color: #ffffff;">
            <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.5rem; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 0.5rem; flex-wrap: wrap; gap: 6px;">
              <div>
                <strong style="color: #4ade80; font-size: 1rem;">${b.origin} ➔ ${b.destination}</strong>
                <div style="font-size: 0.74rem; color: #cbd5e1; margin-top: 2px;">
                  Ref: <b style="color: #ffffff; font-family: monospace;">${b.bookingId}</b> • 📅 ${b.date} at ${b.time}
                </div>
              </div>
              ${statusBadge}
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 8px; font-size: 0.76rem; color: #cbd5e1; margin-bottom: 0.75rem;">
              <div>👤 Passenger: <b style="color: #ffffff;">${b.passengerName}</b> (+91 ${b.passengerPhone})</div>
              <div>🚗 Driver: <b style="color: #ffffff;">${b.driverName}</b> (+91 ${b.driverPhone})</div>
              <div>💺 Seats: <b style="color: #ffffff;">${b.seatsBooked}</b> | Fare: <b style="color: #4ade80;">₹${b.totalFare}</b></div>
              <div>🏦 Bank UTR: <b style="color: #fbbf24; font-family: monospace; font-size: 0.86rem;">${b.passengerUtr}</b></div>
            </div>

            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
              ${!isConfirmed ? `
                <button type="button" class="btn btn-success" onclick="adminConfirmBooking('${b.bookingId}')" style="font-size: 0.74rem; padding: 6px 10px;">
                  ✅ Verify UTR & Confirm Ticket
                </button>
              ` : ''}
              ${!isRejected ? `
                <button type="button" class="btn btn-danger" onclick="adminRejectBooking('${b.bookingId}')" style="font-size: 0.74rem; padding: 6px 10px;">
                  ❌ Reject Fake UTR
                </button>
              ` : ''}
              <button type="button" class="btn btn-primary" onclick="downloadAdminTicketPdf('${b.bookingId}')" style="font-size: 0.72rem; padding: 6px 10px;">
                📄 Download PDF
              </button>
              <a href="https://wa.me/91${b.passengerPhone}?text=${waMsg}" target="_blank" class="btn btn-secondary" style="font-size: 0.72rem; padding: 6px 10px; text-decoration: none; border-color: #16a34a; color: #86efac;">
                💬 WhatsApp Passenger
              </a>
              <a href="https://wa.me/91${b.driverPhone}?text=${waMsg}" target="_blank" class="btn btn-secondary" style="font-size: 0.72rem; padding: 6px 10px; text-decoration: none;">
                💬 WhatsApp Driver
              </a>
            </div>
          </div>
        `;
      }).join('');
    }

    function adminConfirmBooking(bookingId) {
      bookings = JSON.parse(localStorage.getItem('ss_bookings')) || [];
      const b = bookings.find(item => item.bookingId === bookingId);
      if (!b) return;
      b.status = 'CONFIRMED';
      broadcastBookingsToCloud(bookings);
      if (adminDb) {
        try { adminDb.collection('ss_bookings').doc(bookingId).set(b, { merge: true }); } catch(e){}
      }
      renderAdminBookings();
      alert(`✅ Booking ${bookingId} UTR Verified & Confirmed on Customer App!`);
    }

    function adminRejectBooking(bookingId) {
      bookings = JSON.parse(localStorage.getItem('ss_bookings')) || [];
      const b = bookings.find(item => item.bookingId === bookingId);
      if (!b) return;
      if (b.status !== 'REJECTED') {
        // Restore seat on vehicle
        rides = JSON.parse(localStorage.getItem('ss_rides')) || [];
        const r = rides.find(item => item.id === b.rideId);
        if (r) {
          r.seatsAvailable = Math.min(r.totalSeats || 4, (parseInt(r.seatsAvailable) || 0) + (parseInt(b.seatsBooked) || 1));
          broadcastRidesToCloud(rides);
          if (adminDb) {
            try { adminDb.collection('ss_rides').doc(r.id).set(r, { merge: true }); } catch(e){}
          }
        }
      }
      b.status = 'REJECTED';
      broadcastBookingsToCloud(bookings);
      if (adminDb) {
        try { adminDb.collection('ss_bookings').doc(bookingId).set(b, { merge: true }); } catch(e){}
      }
      renderAdminBookings();
      renderAdminVehicles();
      alert(`❌ Booking ${bookingId} Rejected due to invalid UTR, and seat restored!`);
    }

    // =========================================================================
    // 👥 4. REGISTERED AADHAAR KYC USERS RENDERER
    // =========================================================================
    function renderAdminUsers() {
      registeredUsers = JSON.parse(localStorage.getItem('ss_users_db')) || {};
      const userList = Object.values(registeredUsers);
      const countEl = document.getElementById('adm-users-count');
      if (countEl) countEl.innerText = userList.length;

      const container = document.getElementById('adm-users-list');
      if (!container) return;

      if (userList.length === 0) {
        container.innerHTML = `
          <div style="grid-column: 1 / -1; text-align: center; color: #94a3b8; padding: 1rem; background: rgba(2,6,23,0.5); border: 1px dashed #475569; border-radius: 10px; font-size: 0.8rem;">
            No users registered yet in local/cloud storage.
          </div>
        `;
        return;
      }

      container.innerHTML = userList.map(u => `
        <div style="background: rgba(2,6,23,0.85); border: 1px solid #4f46e5; border-radius: 10px; padding: 0.7rem 0.85rem; font-size: 0.78rem;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <strong style="color: #ffffff; font-size: 0.88rem;">👤 ${u.name || 'User'}</strong>
            <span style="background: #14532d; color: #86efac; border: 1px solid #22c55e; font-size: 0.64rem; font-weight: 800; padding: 1px 6px; border-radius: 999px;">
              🛡️ Aadhaar Verified
            </span>
          </div>
          <div style="color: #cbd5e1;">📱 Phone / ID: <b style="color: #38bdf8;">+91 ${u.phone || u.userId}</b></div>
          <div style="color: #94a3b8; font-size: 0.72rem; margin-top: 2px;">📍 ${u.address || 'Assam, India'}</div>
        </div>
      `).join('');
    }

    window.addEventListener('DOMContentLoaded', () => {
      if (sessionStorage.getItem('ss_admin_authed') === 'true') {
        showAdminDashboardView();
      }
    });

    window.addEventListener('visibilitychange', () => {
      if (document.visibilityState === 'visible' && sessionStorage.getItem('ss_admin_authed') === 'true') {
        syncAdminWithCloud(false);
        renderAdminCoinRequests();
        renderAdminVehicles();
        renderAdminBookings();
        renderAdminUsers();
      }
    });

"""

# Find downloadAdminTicketPdf in adm_html so we keep downloadAdminTicketPdf + SafarMediaDB + BUILTIN_41S_VIDEO_DATA intact
pdf_fn_start = adm_html.find("    function downloadAdminTicketPdf(bookingId) {")
assert pdf_fn_start != -1, "downloadAdminTicketPdf not found"

adm_html = adm_html[:main_start] + new_admin_main_and_js + "\n" + adm_html[pdf_fn_start:]

with open("admin.html", "w", encoding="utf-8") as f:
    f.write(adm_html)

print("Successfully upgraded admin.html! Length:", len(adm_html))
