import re

# ==============================================================================
# PART 1: UPGRADE index.html (Strict UTR Validation + Admin Approval Queue + Full Live Sync)
# ==============================================================================
with open("index.html", "r", encoding="utf-8") as f:
    idx_html = f.read()

# 1A. Replace checkGeminiUtrRealtime and add validateStrictBankUtr + Client Device ID + Coin Requests state
old_utr_fn_marker = "// =========================================================================\n    // ✨ GEMINI AI UTR ANTI-FRAUD VERIFIER\n    // ========================================================================="
idx_utr_start = idx_html.find(old_utr_fn_marker)
idx_sync_end = idx_html.find("// 1. Data Store Initialization (Preserves real rides and bookings)")

assert idx_utr_start != -1 and idx_sync_end != -1, f"Markers not found: {idx_utr_start}, {idx_sync_end}"

new_utr_and_sync_engine = """// =========================================================================
    // ✨ STRICT NPCI 12-DIGIT BANK UTR ANTI-FRAUD & ADMIN VERIFICATION ENGINE
    // =========================================================================
    const FAKE_BLACKLISTED_UTRS = new Set([
      '000000000000', '111111111111', '222222222222', '333333333333',
      '444444444444', '555555555555', '666666666666', '777777777777',
      '888888888888', '999999999999', '123456789012', '012345678901',
      '987654321012', '987654321013', '987654321014', '987654321015',
      '987654321098', '123456123456', '112233445566', '100000000000',
      '123123123123', '456456456456', '789789789789', '145266378478'
    ]);

    function getClientDeviceId() {
      let cid = ssStorage.getItem('ss_client_device_id');
      if (!cid) {
        cid = 'DEV-' + Math.floor(100000 + Math.random() * 900000);
        ssStorage.setItem('ss_client_device_id', cid);
      }
      return cid;
    }

    function getCoinRequestsList() {
      try {
        const list = JSON.parse(ssStorage.getItem('ss_coin_requests')) || [];
        return Array.isArray(list) ? list : [];
      } catch(e) {
        return [];
      }
    }

    function validateStrictBankUtr(utrValue) {
      const val = (utrValue || '').trim();
      if (!val || val.length !== 12 || !/^\\d{12}$/.test(val)) {
        return { valid: false, reason: 'कृपया पूरे 12-अंकों का न्यूमेरिक बैंक UTR नंबर दर्ज करें!' };
      }
      if (val.startsWith('0')) {
        return { valid: false, reason: '❌ अमान्य UTR! असली बैंक/NPCI UPI UTR कभी 0 से शुरू नहीं होता।' };
      }
      if (FAKE_BLACKLISTED_UTRS.has(val) || /(\\d)\\1{5,}/.test(val)) {
        return { valid: false, reason: '❌ गलत / टेस्ट UTR नंबर! कृपया अपने UPI ऐप (PhonePe/GPay/Paytm) से असली 12-अंकों का UTR दर्ज करें।' };
      }
      // Check if a single digit appears more than 8 times
      const counts = {};
      for (let ch of val) counts[ch] = (counts[ch] || 0) + 1;
      if (Object.values(counts).some(c => c > 8)) {
        return { valid: false, reason: '❌ अमान्य UTR पैटर्न! कृपया अपने बैंक पेमेंट रसीद से सही UTR नंबर दर्ज करें।' };
      }
      // Check duplicate across rides, bookings, and coin requests
      const coinReqs = getCoinRequestsList();
      const usedUtrs = JSON.parse(ssStorage.getItem('ss_used_coin_utrs')) || [];
      const inRides = (typeof rides !== 'undefined' && Array.isArray(rides)) && rides.some(r => r.platformFeeUtr === val || r.utrNumber === val);
      const inBookings = (typeof bookings !== 'undefined' && Array.isArray(bookings)) && bookings.some(b => b.passengerUtr === val);
      const inCoins = coinReqs.some(c => c.utr === val);
      if (inRides || inBookings || inCoins || usedUtrs.includes(val)) {
        return { valid: false, reason: '⚠️ यह UTR नंबर पहले ही सबमिट किया जा चुका है! कृपया नया पेमेंट UTR दर्ज करें।' };
      }
      return { valid: true, reason: '✓ वैध 12-अंकीय UTR फॉर्मेट (Admin वेरिफिकेशन के लिए तैयार)' };
    }

    function checkGeminiUtrRealtime(utrValue, statusElementId) {
      const el = document.getElementById(statusElementId);
      if (!el) return;

      const val = (utrValue || '').trim();
      if (!val) {
        el.innerHTML = `<span>🛡️</span> <span>Strict Security: UTR सबमिट करने पर Admin Panel से वेरिफाई होने के बाद ही अप्रूव होगा</span>`;
        el.style.color = '#15803d';
        return;
      }

      if (val.length < 12) {
        el.innerHTML = `<span>⏳</span> <span style="color:#d97706;">12-अंकों का बैंक UTR दर्ज करें (${val.length}/12)</span>`;
        return;
      }

      const check = validateStrictBankUtr(val);
      if (!check.valid) {
        el.innerHTML = `<span>⚠️</span> <span style="color:#dc2626; font-weight:800;">${check.reason}</span>`;
      } else {
        el.innerHTML = `<span>✅</span> <span style="color:#15803d; font-weight:800;">${check.reason}</span>`;
      }
    }

    document.addEventListener('input', (e) => {
      if (e.target && e.target.id === 'df-utr') {
        checkGeminiUtrRealtime(e.target.value, 'df-gemini-utr-status');
      }
      if (e.target && e.target.id === 'bm-utr-input') {
        checkGeminiUtrRealtime(e.target.value, 'bm-gemini-utr-status');
      }
      if (e.target && e.target.id === 'buy-coins-utr-input') {
        checkGeminiUtrRealtime(e.target.value, 'buy-coins-utr-status');
      }
      if (e.target && (e.target.id === 'df-from' || e.target.id === 'df-to')) {
        updateGeminiRouteTelemetry();
      }
    });

    // =========================================================================
    // 🌐 REAL-TIME BIDIRECTIONAL ADMIN <-> APP LIVE SYNC ENGINE (<1s LATENCY)
    // Connects Rides, Bookings, Coin UTR Requests, Users & Video Ads
    // =========================================================================
    const MULTI_CLOUD_SYNC_KV = 'https://kvdb.io/safarsaathi_assam_2026/rides';
    const FIREBASE_RTDB_BASE = 'https://safarsaathi-1de86-default-rtdb.firebaseio.com';
    const FIREBASE_RTDB_SYNC_URL = FIREBASE_RTDB_BASE + '/ss_rides.json';
    const FIREBASE_RTDB_BOOKINGS_URL = FIREBASE_RTDB_BASE + '/ss_bookings.json';
    const FIREBASE_RTDB_COINS_URL = FIREBASE_RTDB_BASE + '/ss_coin_requests.json';
    const FIREBASE_RTDB_USERS_URL = FIREBASE_RTDB_BASE + '/ss_users_db.json';
    const FIREBASE_RTDB_VIDEO_AD_URL = FIREBASE_RTDB_BASE + '/ss_video_ad.json';

    let syncBroadcastChannel = null;
    let isAppTabActive = true;

    function handleIncomingChannelPayload(data) {
      if (!data || !data.type) return;
      if (data.type === 'RIDES_UPDATED' && Array.isArray(data.rides)) {
        mergeIncomingCloudRides(data.rides, true);
      } else if (data.type === 'BOOKINGS_UPDATED' && Array.isArray(data.bookings)) {
        mergeIncomingCloudBookings(data.bookings);
      } else if (data.type === 'COIN_REQUESTS_UPDATED' && Array.isArray(data.coinRequests)) {
        processSyncedCoinRequests(data.coinRequests);
      } else if (data.type === 'PROFILE_VIDEO_AD_UPDATED' && data.ad) {
        applyIncomingProfileVideoAd(data.ad, true);
      } else if (data.type === 'USERS_UPDATED' && data.users) {
        try { ssStorage.setItem('ss_users_db', JSON.stringify(data.users)); } catch(e){}
      }
    }

    try {
      if (typeof BroadcastChannel !== 'undefined') {
        syncBroadcastChannel = new BroadcastChannel('safarsaathi_multi_cloud_stream');
        syncBroadcastChannel.onmessage = (event) => {
          if (event && event.data) handleIncomingChannelPayload(event.data);
        };
      }
    } catch(e) {}

    // Cross-Tab LocalStorage Event Listener (Instant sync when Admin Panel & App are open in same browser)
    window.addEventListener('storage', (e) => {
      try {
        if (e.key === 'ss_rides' && e.newValue !== null) {
          const list = JSON.parse(e.newValue) || [];
          mergeIncomingCloudRides(list, true);
        } else if (e.key === 'ss_bookings' && e.newValue !== null) {
          const list = JSON.parse(e.newValue) || [];
          mergeIncomingCloudBookings(list);
        } else if (e.key === 'ss_coin_requests' && e.newValue !== null) {
          const list = JSON.parse(e.newValue) || [];
          processSyncedCoinRequests(list);
        } else if (e.key === 'ss_profile_video_ad' && e.newValue !== null) {
          const ad = JSON.parse(e.newValue);
          if (ad && ad.src) applyIncomingProfileVideoAd(ad, true);
        }
      } catch(err) {}
    });

    function broadcastRidesLocally(updatedRides) {
      try {
        ssStorage.setItem('ss_rides', JSON.stringify(updatedRides));
      } catch(e){}
      if (syncBroadcastChannel) {
        try {
          syncBroadcastChannel.postMessage({ type: 'RIDES_UPDATED', rides: updatedRides, timestamp: Date.now() });
        } catch(e){}
      }
      try {
        fetch(FIREBASE_RTDB_SYNC_URL, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedRides)
        }).catch(() => {});
      } catch(e){}
      try {
        fetch(MULTI_CLOUD_SYNC_KV, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedRides)
        }).catch(() => {});
      } catch(e){}
    }

    function broadcastBookingsEverywhere(updatedBookings) {
      try {
        ssStorage.setItem('ss_bookings', JSON.stringify(updatedBookings));
      } catch(e){}
      if (syncBroadcastChannel) {
        try {
          syncBroadcastChannel.postMessage({ type: 'BOOKINGS_UPDATED', bookings: updatedBookings, timestamp: Date.now() });
        } catch(e){}
      }
      try {
        fetch(FIREBASE_RTDB_BOOKINGS_URL, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedBookings)
        }).catch(() => {});
      } catch(e){}
    }

    function broadcastCoinRequestsEverywhere(updatedReqs) {
      try {
        ssStorage.setItem('ss_coin_requests', JSON.stringify(updatedReqs));
      } catch(e){}
      if (syncBroadcastChannel) {
        try {
          syncBroadcastChannel.postMessage({ type: 'COIN_REQUESTS_UPDATED', coinRequests: updatedReqs, timestamp: Date.now() });
        } catch(e){}
      }
      try {
        fetch(FIREBASE_RTDB_COINS_URL, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(updatedReqs)
        }).catch(() => {});
      } catch(e){}
    }

    function broadcastUsersEverywhere(usersObj) {
      try {
        ssStorage.setItem('ss_users_db', JSON.stringify(usersObj));
      } catch(e){}
      if (syncBroadcastChannel) {
        try {
          syncBroadcastChannel.postMessage({ type: 'USERS_UPDATED', users: usersObj, timestamp: Date.now() });
        } catch(e){}
      }
      try {
        fetch(FIREBASE_RTDB_USERS_URL, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(usersObj)
        }).catch(() => {});
      } catch(e){}
    }

    function mergeIncomingCloudBookings(cloudBookings) {
      if (!Array.isArray(cloudBookings)) return;
      bookings = cloudBookings;
      try { ssStorage.setItem('ss_bookings', JSON.stringify(bookings)); } catch(e){}
      try { renderPassengerBookings(); } catch(e){}
      try { renderDriverFleet(); } catch(e){}
      try { renderLiveCarsHome(); } catch(e){}
      try { updateNavCounts(); } catch(e){}
    }

    // Processes Coin Recharge Requests synced from Admin Panel — ONLY credits coins when Admin sets status === 'APPROVED'
    function processSyncedCoinRequests(incomingList) {
      if (!Array.isArray(incomingList)) return;
      const myUser = getActiveUserProfile();
      const myDevId = getClientDeviceId();
      let changed = false;

      incomingList.forEach(req => {
        if (!req) return;
        const isMyRequest = (req.deviceId && req.deviceId === myDevId) ||
                            (myUser && req.userPhone && req.userPhone === myUser.phone) ||
                            (myUser && req.userId && req.userId === myUser.userId);

        if (isMyRequest) {
          if (req.status === 'APPROVED' && !req.creditedToWallet) {
            req.creditedToWallet = true;
            req.creditedAt = new Date().toISOString();
            changed = true;
            const addAmt = parseInt(req.coins || req.amount) || 0;
            if (addAmt > 0) {
              setGameCoins(getGameCoins() + addAmt);
              try { playCoinSound(); } catch(e){}
              showToast(`🎉 Admin Verified UTR (${req.utr})! +🪙 ${addAmt} Coins (₹${addAmt}) आपके वॉलेट में जुड़ गए!`, '#15803d');
            }
            if (typeof db !== 'undefined' && db) {
              try { db.collection('ss_coin_requests').doc(req.id).set(req, { merge: true }); } catch(e){}
            }
          } else if (req.status === 'REJECTED' && !req.notifiedRejection) {
            req.notifiedRejection = true;
            changed = true;
            showToast(`❌ गलत UTR (${req.utr})! Admin द्वारा पेमेंट वेरिफाई नहीं हुआ, रिक्वेस्ट अस्वीकार कर दी गई।`, '#dc2626');
            if (typeof db !== 'undefined' && db) {
              try { db.collection('ss_coin_requests').doc(req.id).set(req, { merge: true }); } catch(e){}
            }
          }
        }
      });

      try {
        ssStorage.setItem('ss_coin_requests', JSON.stringify(incomingList));
      } catch(e){}
      if (changed) {
        broadcastCoinRequestsEverywhere(incomingList);
      }
      try { renderUserCoinRequestsStatus(); } catch(e){}
    }

    function manualForceRefreshLiveCars() {
      showToast('🔄 Syncing live with Admin Panel & Cloud...', '#16a34a');
      executeAiCloudSync();
      if (typeof db !== 'undefined' && db) {
        db.collection('ss_rides').get().then(snapshot => {
          const cloudRides = [];
          snapshot.forEach(doc => {
            const d = doc.data();
            if (d) { if (!d.id) d.id = doc.id; cloudRides.push(d); }
          });
          mergeIncomingCloudRides(cloudRides, true);
          renderLiveCarsHome();
          showToast('✓ Live sync with Admin Panel complete!', '#15803d');
        }).catch(() => {
          renderLiveCarsHome();
        });
      } else {
        renderLiveCarsHome();
      }
    }

    function executeAiCloudSync() {
      if (!isAppTabActive) return;

      // 1. Sync Rides from RTDB
      fetch(FIREBASE_RTDB_SYNC_URL)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data !== null && data !== undefined) {
            const list = Array.isArray(data) ? data : Object.values(data);
            mergeIncomingCloudRides(list, true);
          }
        })
        .catch(() => {});

      // 2. Sync Bookings from RTDB
      fetch(FIREBASE_RTDB_BOOKINGS_URL)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            const list = Array.isArray(data) ? data : Object.values(data);
            mergeIncomingCloudBookings(list);
          }
        })
        .catch(() => {});

      // 3. Sync Coin UTR Requests from RTDB
      fetch(FIREBASE_RTDB_COINS_URL)
        .then(res => res.ok ? res.json() : null)
        .then(data => {
          if (data) {
            const list = Array.isArray(data) ? data : Object.values(data);
            processSyncedCoinRequests(list);
          }
        })
        .catch(() => {});
    }

    document.addEventListener('visibilitychange', () => {
      isAppTabActive = (document.visibilityState === 'visible');
      if (isAppTabActive) {
        executeAiCloudSync();
      }
    });

    // Continuous 2.5-second live cloud sync with Admin Panel
    setInterval(executeAiCloudSync, 2500);

"""

idx_html = idx_html[:idx_utr_start] + new_utr_and_sync_engine + idx_html[idx_sync_end:]

# 1B. Upgrade submitPassengerBooking in index.html to use validateStrictBankUtr and broadcastBookingsEverywhere
old_pass_booking = """    function submitPassengerBooking() {
      if (!selectedRideForBooking) return;
      const utr = (document.getElementById('bm-utr-input')?.value || '').trim();
      if (!utr || utr.length !== 12 || !/^\\d{12}$/.test(utr)) {
        showToast('Please enter valid 12-digit numeric UPI UTR number from your payment receipt!', '#dc2626');
        document.getElementById('bm-utr-input')?.focus();
        return;
      }

      // Anti-Fraud UTR duplicate check
      const isUtrUsed = bookings.some(b => b.passengerUtr === utr);
      if (isUtrUsed) {
        showToast('⚠️ यह UTR नंबर पहले से ही किसी बुकिंग में दर्ज है! कृपया अपना वास्तविक पेमेंट UTR दर्ज करें।', '#dc2626');
        return;
      }"""

new_pass_booking = """    function submitPassengerBooking() {
      if (!selectedRideForBooking) return;
      const utr = (document.getElementById('bm-utr-input')?.value || '').trim();
      const utrCheck = validateStrictBankUtr(utr);
      if (!utrCheck.valid) {
        showToast(utrCheck.reason, '#dc2626');
        document.getElementById('bm-utr-input')?.focus();
        return;
      }"""

assert old_pass_booking in idx_html, "old_pass_booking not found"
idx_html = idx_html.replace(old_pass_booking, new_pass_booking, 1)

old_pass_save = """      bookings.unshift(booking);
      ssStorage.setItem('ss_bookings', JSON.stringify(bookings));

      selectedRideForBooking.seatsAvailable = Math.max(0, (selectedRideForBooking.seatsAvailable || 1) - seatsCount);
      ssStorage.setItem('ss_rides', JSON.stringify(rides));"""

new_pass_save = """      bookings.unshift(booking);
      broadcastBookingsEverywhere(bookings);

      selectedRideForBooking.seatsAvailable = Math.max(0, (selectedRideForBooking.seatsAvailable || 1) - seatsCount);
      broadcastRidesLocally(rides);"""

assert old_pass_save in idx_html, "old_pass_save not found"
idx_html = idx_html.replace(old_pass_save, new_pass_save, 1)

# 1C. Upgrade submitDriverRideDirect in index.html so it validates UTR strictly and sets status: 'PENDING_APPROVAL', verifiedByAdmin: false!
old_driver_submit = """      const utr = (document.getElementById('df-utr')?.value || '').trim();
      if (!utr || utr.length !== 12 || !/^\\d{12}$/.test(utr)) {
        showToast('Please enter valid 12-digit numeric payment UTR number for your ₹100 platform fee!', '#dc2626');
        document.getElementById('df-utr')?.focus();
        return;
      }

      const user = getActiveUserProfile();
      const from = (document.getElementById('df-from')?.value || 'Guwahati').trim();
      const to = (document.getElementById('df-to')?.value || 'Shillong').trim();
      const date = document.getElementById('df-date')?.value || getTomorrowDate(1);
      const time = document.getElementById('df-time')?.value || '08:30';
      const model = (document.getElementById('df-model')?.value || 'Swift Dzire').trim();
      const plate = (document.getElementById('df-plate')?.value || '').trim();
      const seats = parseInt(document.getElementById('df-seats')?.value) || 3;
      const fare = parseInt(document.getElementById('df-fare')?.value) || 300;
      const driverUpi = (document.getElementById('df-driver-upi')?.value || user.phone + '@upi').trim();

      const newRide = {
        id: 'RIDE-' + Math.floor(1000 + Math.random() * 9000),
        driverName: user.name,
        driverPhone: user.phone,
        driverUpi: driverUpi,
        driverQr: driverUploadedQrData || 'mitali_qr_compact.svg',
        farePerSeat: fare,
        origin: from,
        destination: to,
        date: date,
        time: time,
        seatsAvailable: seats,
        totalSeats: seats,
        vehicleModel: model,
        vehicleNumber: plate,
        platformFeeUtr: utr,
        utrNumber: utr,
        status: 'ACTIVE',
        verifiedByAdmin: true,
        postedAt: new Date().toISOString()
      };"""

new_driver_submit = """      const utr = (document.getElementById('df-utr')?.value || '').trim();
      const utrCheck = validateStrictBankUtr(utr);
      if (!utrCheck.valid) {
        showToast(utrCheck.reason, '#dc2626');
        document.getElementById('df-utr')?.focus();
        return;
      }

      const user = getActiveUserProfile();
      const from = (document.getElementById('df-from')?.value || 'Guwahati').trim();
      const to = (document.getElementById('df-to')?.value || 'Shillong').trim();
      const date = document.getElementById('df-date')?.value || getTomorrowDate(1);
      const time = document.getElementById('df-time')?.value || '08:30';
      const model = (document.getElementById('df-model')?.value || 'Swift Dzire').trim();
      const plate = (document.getElementById('df-plate')?.value || '').trim();
      const seats = parseInt(document.getElementById('df-seats')?.value) || 3;
      const fare = parseInt(document.getElementById('df-fare')?.value) || 300;
      const driverUpi = (document.getElementById('df-driver-upi')?.value || user.phone + '@upi').trim();

      const newRide = {
        id: 'RIDE-' + Math.floor(1000 + Math.random() * 9000),
        driverName: user.name,
        driverPhone: user.phone,
        driverUpi: driverUpi,
        driverQr: driverUploadedQrData || 'mitali_qr_compact.svg',
        farePerSeat: fare,
        origin: from,
        destination: to,
        date: date,
        time: time,
        seatsAvailable: seats,
        totalSeats: seats,
        vehicleModel: model,
        vehicleNumber: plate,
        platformFeeUtr: utr,
        utrNumber: utr,
        status: 'PENDING_APPROVAL',
        verifiedByAdmin: false,
        postedAt: new Date().toISOString()
      };"""

assert old_driver_submit in idx_html, "old_driver_submit not found"
idx_html = idx_html.replace(old_driver_submit, new_driver_submit, 1)

# Also sync user registration to Admin Panel in submitAuthAction
old_user_save = """        users[uid] = newUser;
        ssStorage.setItem('ss_users_db', JSON.stringify(users));
        ssStorage.setItem('ss_current_user_id', uid);"""

new_user_save = """        users[uid] = newUser;
        broadcastUsersEverywhere(users);
        ssStorage.setItem('ss_current_user_id', uid);
        if (typeof db !== 'undefined' && db) {
          try { db.collection('ss_users').doc(uid).set(newUser, { merge: true }); } catch(e){}
        }"""

assert old_user_save in idx_html, "old_user_save not found"
idx_html = idx_html.replace(old_user_save, new_user_save, 1)

# Also broadcast confirmPassengerBooking and rejectPassengerBooking in index.html
old_confirm_reject = """    function confirmPassengerBooking(bookingId) {
      const user = getActiveUserProfile();
      const b = bookings.find(item => item.bookingId === bookingId);
      if (!b) return;
      if (!user || user.phone !== b.driverPhone) {
        showToast('Unauthorized: You can only manage bookings for your own posted vehicle.', '#dc2626');
        return;
      }
      b.status = 'CONFIRMED';
      ssStorage.setItem('ss_bookings', JSON.stringify(bookings));
      if (db) {
        try { db.collection('ss_bookings').doc(bookingId).update({ status: 'CONFIRMED' }); } catch(e){}
      }
      renderDriverFleet();
      showToast('✓ Seat Confirmed! Passenger notified.', '#15803d');
    }

    function rejectPassengerBooking(bookingId) {
      const user = getActiveUserProfile();
      const b = bookings.find(item => item.bookingId === bookingId);
      if (!b) return;
      if (!user || user.phone !== b.driverPhone) {
        showToast('Unauthorized: You can only manage bookings for your own posted vehicle.', '#dc2626');
        return;
      }
      b.status = 'REJECTED';
      ssStorage.setItem('ss_bookings', JSON.stringify(bookings));
      if (db) {
        try { db.collection('ss_bookings').doc(bookingId).update({ status: 'REJECTED' }); } catch(e){}
      }
      renderDriverFleet();
      showToast('Booking request rejected.', '#dc2626');
    }"""

new_confirm_reject = """    function confirmPassengerBooking(bookingId) {
      const user = getActiveUserProfile();
      const b = bookings.find(item => item.bookingId === bookingId);
      if (!b) return;
      if (!user || user.phone !== b.driverPhone) {
        showToast('Unauthorized: You can only manage bookings for your own posted vehicle.', '#dc2626');
        return;
      }
      b.status = 'CONFIRMED';
      broadcastBookingsEverywhere(bookings);
      if (db) {
        try { db.collection('ss_bookings').doc(bookingId).update({ status: 'CONFIRMED' }); } catch(e){}
      }
      renderDriverFleet();
      showToast('✓ Seat Confirmed! Passenger notified.', '#15803d');
    }

    function rejectPassengerBooking(bookingId) {
      const user = getActiveUserProfile();
      const b = bookings.find(item => item.bookingId === bookingId);
      if (!b) return;
      if (!user || user.phone !== b.driverPhone) {
        showToast('Unauthorized: You can only manage bookings for your own posted vehicle.', '#dc2626');
        return;
      }
      b.status = 'REJECTED';
      broadcastBookingsEverywhere(bookings);
      if (db) {
        try { db.collection('ss_bookings').doc(bookingId).update({ status: 'REJECTED' }); } catch(e){}
      }
      renderDriverFleet();
      showToast('Booking request rejected.', '#dc2626');
    }"""

assert old_confirm_reject in idx_html, "old_confirm_reject not found"
idx_html = idx_html.replace(old_confirm_reject, new_confirm_reject, 1)

# 1D. Upgrade mergeIncomingCloudRides and initFirebase in index.html so Firestore & RTDB sync rides, bookings, and coin_requests in real time
old_merge_and_fb = """    function mergeIncomingCloudRides(cloudRides) {
      if (!cloudRides || !Array.isArray(cloudRides)) return;

      const fakeDemoNames = new Set(['Bikram Das', 'Rahul Saikia', 'Pranab Bora']);
      const fakeDemoIds = new Set(['RIDE-101', 'RIDE-102', 'RIDE-103', 'RIDE-4921', 'RIDE-1902', 'RIDE-3311']);

      // Filter out ONLY the 3 fake mock demo drivers
      const cleanCloud = cloudRides.filter(r => !fakeDemoNames.has(r.driverName) && !fakeDemoIds.has(r.id));

      // Preserve only the current user's local pending post if any
      const user = getActiveUserProfile();
      const myPending = rides.filter(r => user && r.driverPhone === user.phone && r.status === 'PENDING_APPROVAL');
      const cloudIds = new Set(cleanCloud.map(r => r.id));
      const finalRides = [...cleanCloud];
      myPending.forEach(pr => {
        if (!cloudIds.has(pr.id)) finalRides.push(pr);
      });

      // Strict Zero Demo: If cloud has 0 cars, preserve 0 cars!


      rides = finalRides;
      ssStorage.setItem('ss_rides', JSON.stringify(rides));
      renderLiveCarsHome();
      renderDriverFleet();
      updateNavCounts();
    }

    function initFirebase() {
      if (typeof firebase !== 'undefined' && firebaseConfig && firebaseConfig.apiKey) {
        try {
          if (!firebase.apps.length) {
            firebase.initializeApp(firebaseConfig);
          }
          if (firebase.auth) {
            firebase.auth().signInAnonymously().catch(() => {});
          }
          if (firebase.firestore) {
            db = firebase.firestore();
            db.collection('ss_rides').onSnapshot(snapshot => {
              const cloudRides = [];
              snapshot.forEach(doc => {
                const data = doc.data();
                if (data) {
                  if (!data.id) data.id = doc.id;
                  cloudRides.push(data);
                }
              });
              if (cloudRides.length > 0) {
                mergeIncomingCloudRides(cloudRides);
              }
            });

            // 🔥 REAL-TIME ADMIN VIDEO AD CLOUD SYNC ACROSS ALL CUSTOMER PHONES
            try {
              db.collection('ss_settings').doc('video_ad').onSnapshot((doc) => {
                if (doc && doc.exists) {
                  const ad = doc.data();
                  if (ad && ad.src) {
                    applyIncomingProfileVideoAd(ad, false);
                  }
                }
              }, (err) => {
                console.warn('Video ad cloud sync notice:', err);
              });
            } catch(e){}
          }
        } catch(e){}
      }
    }"""

new_merge_and_fb = """    function mergeIncomingCloudRides(cloudRides, allowEmpty = false) {
      if (!cloudRides || !Array.isArray(cloudRides)) return;

      const fakeDemoNames = new Set(['Bikram Das', 'Rahul Saikia', 'Pranab Bora']);
      const fakeDemoIds = new Set(['RIDE-101', 'RIDE-102', 'RIDE-103', 'RIDE-4921', 'RIDE-1902', 'RIDE-3311']);

      const cleanCloud = cloudRides.filter(r => r && !fakeDemoNames.has(r.driverName) && !fakeDemoIds.has(r.id));

      rides = cleanCloud;
      ssStorage.setItem('ss_rides', JSON.stringify(rides));
      renderLiveCarsHome();
      renderDriverFleet();
      updateNavCounts();
      try { updateMapLiveCarRadar(); } catch(e){}
    }

    function initFirebase() {
      if (typeof firebase !== 'undefined' && firebaseConfig && firebaseConfig.apiKey) {
        try {
          if (!firebase.apps.length) {
            firebase.initializeApp(firebaseConfig);
          }
          if (firebase.auth) {
            firebase.auth().signInAnonymously().catch(() => {});
          }
          if (firebase.firestore) {
            db = firebase.firestore();
            // 1. Live Rides Sync
            db.collection('ss_rides').onSnapshot(snapshot => {
              const cloudRides = [];
              snapshot.forEach(doc => {
                const data = doc.data();
                if (data) {
                  if (!data.id) data.id = doc.id;
                  cloudRides.push(data);
                }
              });
              mergeIncomingCloudRides(cloudRides, true);
            });

            // 2. Live Bookings Sync
            try {
              db.collection('ss_bookings').onSnapshot(snapshot => {
                const cloudBookings = [];
                snapshot.forEach(doc => {
                  const data = doc.data();
                  if (data) {
                    if (!data.bookingId) data.bookingId = doc.id;
                    cloudBookings.push(data);
                  }
                });
                if (cloudBookings.length > 0) {
                  mergeIncomingCloudBookings(cloudBookings);
                }
              });
            } catch(e){}

            // 3. Live Coin UTR Requests Sync (Admin Approval -> Instant Wallet Credit)
            try {
              db.collection('ss_coin_requests').onSnapshot(snapshot => {
                const cloudCoinReqs = [];
                snapshot.forEach(doc => {
                  const data = doc.data();
                  if (data) {
                    if (!data.id) data.id = doc.id;
                    cloudCoinReqs.push(data);
                  }
                });
                if (cloudCoinReqs.length > 0) {
                  processSyncedCoinRequests(cloudCoinReqs);
                }
              });
            } catch(e){}

            // 4. Live Video Ad Sync
            try {
              db.collection('ss_settings').doc('video_ad').onSnapshot((doc) => {
                if (doc && doc.exists) {
                  const ad = doc.data();
                  if (ad && ad.src) {
                    applyIncomingProfileVideoAd(ad, false);
                  }
                }
              }, (err) => {
                console.warn('Video ad cloud sync notice:', err);
              });
            } catch(e){}
          }
        } catch(e){}
      }
    }"""

assert old_merge_and_fb in idx_html, "old_merge_and_fb not found"
idx_html = idx_html.replace(old_merge_and_fb, new_merge_and_fb, 1)

# 1E. Upgrade submitBuyCoinsUtr and openBuyCoinsModal in index.html so wrong UTR NEVER adds ₹100!
old_buy_coins_js = """    function openBuyCoinsModal(preselectCoins) {
      if (preselectCoins && preselectCoins > 0) {
        selectBuyCoinPack(preselectCoins);
      } else {
        selectBuyCoinPack(100);
      }
      const modal = document.getElementById('buy-coins-modal');
      if (modal) modal.style.display = 'flex';
    }

    function closeBuyCoinsModal() {
      const modal = document.getElementById('buy-coins-modal');
      if (modal) modal.style.display = 'none';
      const utrInp = document.getElementById('buy-coins-utr-input');
      if (utrInp) utrInp.value = '';
    }"""

new_buy_coins_js = """    function openBuyCoinsModal(preselectCoins) {
      if (preselectCoins && preselectCoins > 0) {
        selectBuyCoinPack(preselectCoins);
      } else {
        selectBuyCoinPack(100);
      }
      renderUserCoinRequestsStatus();
      const modal = document.getElementById('buy-coins-modal');
      if (modal) modal.style.display = 'flex';
    }

    function closeBuyCoinsModal() {
      const modal = document.getElementById('buy-coins-modal');
      if (modal) modal.style.display = 'none';
      const utrInp = document.getElementById('buy-coins-utr-input');
      if (utrInp) utrInp.value = '';
    }

    function renderUserCoinRequestsStatus() {
      const box = document.getElementById('user-coin-requests-status-box');
      if (!box) return;
      const myUser = getActiveUserProfile();
      const myDevId = getClientDeviceId();
      const allReqs = getCoinRequestsList();
      const myReqs = allReqs.filter(r =>
        (r.deviceId && r.deviceId === myDevId) ||
        (myUser && r.userPhone && r.userPhone === myUser.phone)
      ).slice(0, 3);

      if (myReqs.length === 0) {
        box.style.display = 'none';
        box.innerHTML = '';
        return;
      }

      box.style.display = 'block';
      box.innerHTML = `<div style="font-size:0.68rem; font-weight:900; color:#0f172a; margin-bottom:4px;">📋 Recent UTR Verification Status (Live Admin Sync):</div>` +
        myReqs.map(r => {
          const st = (r.status || '').toUpperCase();
          let badge = `<span style="background:#fef3c7; color:#b45309; border:1px solid #f59e0b; padding:1px 6px; border-radius:4px; font-size:0.62rem; font-weight:900;">⏳ Pending Admin Check</span>`;
          if (st === 'APPROVED') {
            badge = `<span style="background:#dcfce7; color:#15803d; border:1px solid #16a34a; padding:1px 6px; border-radius:4px; font-size:0.62rem; font-weight:900;">✅ Approved (+${r.coins} Coins)</span>`;
          } else if (st === 'REJECTED') {
            badge = `<span style="background:#fee2e2; color:#dc2626; border:1px solid #ef4444; padding:1px 6px; border-radius:4px; font-size:0.62rem; font-weight:900;">❌ Wrong UTR Rejected</span>`;
          }
          return `<div style="display:flex; justify-content:space-between; align-items:center; background:#f8fafc; border:1px solid #cbd5e1; border-radius:6px; padding:4px 7px; margin-bottom:3px; font-size:0.68rem;">
            <span><b>₹${r.amount}</b> • UTR: <code style="font-weight:900;">${r.utr}</code></span>
            ${badge}
          </div>`;
        }).join('');
    }"""

assert old_buy_coins_js in idx_html, "old_buy_coins_js not found"
idx_html = idx_html.replace(old_buy_coins_js, new_buy_coins_js, 1)

old_submit_buy_coins = """    function submitBuyCoinsUtr() {
      const utrInp = document.getElementById('buy-coins-utr-input');
      const utr = (utrInp?.value || '').trim();
      if (!utr || utr.length !== 12 || !/^\\d{12}$/.test(utr)) {
        showToast('कृपया अपने बैंक पेमेंट SMS या UPI ऐप की रसीद से सही 12-अंकों का न्यूमेरिक UTR नंबर दर्ज करें!', '#dc2626');
        utrInp?.focus();
        return;
      }

      // Check anti-fraud duplicate
      let usedUtrs = JSON.parse(ssStorage.getItem('ss_used_coin_utrs')) || [];
      if (usedUtrs.includes(utr)) {
        showToast('⚠️ यह UTR नंबर पहले ही इस्तेमाल किया जा चुका है!', '#dc2626');
        return;
      }
      usedUtrs.push(utr);
      ssStorage.setItem('ss_used_coin_utrs', JSON.stringify(usedUtrs));

      // Credit Coins (1 Coin = ₹1)
      const addedCoins = currentBuyCoinPack;
      setGameCoins(getGameCoins() + addedCoins);
      playCoinSound();

      closeBuyCoinsModal();
      showToast(`🎉 Payment Verified! +🪙 ${addedCoins} Coins (₹${addedCoins}) credited to your wallet!`, '#15803d');
    }"""

new_submit_buy_coins = """    function submitBuyCoinsUtr() {
      const utrInp = document.getElementById('buy-coins-utr-input');
      const utr = (utrInp?.value || '').trim();
      const utrCheck = validateStrictBankUtr(utr);
      if (!utrCheck.valid) {
        showToast(utrCheck.reason, '#dc2626');
        utrInp?.focus();
        return;
      }

      const user = getActiveUserProfile();
      const devId = getClientDeviceId();
      const reqObj = {
        id: 'COIN-' + Math.floor(100000 + Math.random() * 900000),
        deviceId: devId,
        userId: user ? user.userId : devId,
        userName: user ? user.name : 'Game Player',
        userPhone: user ? user.phone : 'Not Logged In',
        coins: currentBuyCoinPack,
        amount: currentBuyCoinPack,
        utr: utr,
        status: 'PENDING_ADMIN_APPROVAL',
        creditedToWallet: false,
        notifiedRejection: false,
        requestedAt: new Date().toISOString()
      };

      const allReqs = getCoinRequestsList();
      allReqs.unshift(reqObj);
      broadcastCoinRequestsEverywhere(allReqs);

      if (typeof db !== 'undefined' && db) {
        try {
          db.collection('ss_coin_requests').doc(reqObj.id).set(reqObj, { merge: true });
        } catch(e){}
      }

      if (utrInp) utrInp.value = '';
      renderUserCoinRequestsStatus();
      showToast(`⏳ UTR (${utr}) वेरिफिकेशन के लिए Admin Panel में भेज दिया गया है! Admin द्वारा बैंक में ₹${currentBuyCoinPack} पेमेंट वेरिफाई करते ही कॉइन्स अपने आप जुड़ जाएंगे।`, '#d97706');
    }"""

assert old_submit_buy_coins in idx_html, "old_submit_buy_coins not found"
idx_html = idx_html.replace(old_submit_buy_coins, new_submit_buy_coins, 1)

# 1F. Update Buy Coins Modal HTML in index.html to show the strict Admin Verification banner & live status box
old_buy_modal_html = """      <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 6px 10px; margin-bottom: 0.75rem; font-size: 0.76rem; color: #166534; font-weight: 800;">
        ⚡ Instant Credit: <b>1 Coin = ₹1</b> • Jana Small Finance Bank
      </div>"""

new_buy_modal_html = """      <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 6px 10px; margin-bottom: 0.75rem; font-size: 0.74rem; color: #166534; font-weight: 800;">
        🛡️ <b>100% Admin Verified Recharge:</b> 1 Coin = ₹1 • बिना Admin UTR वेरिफिकेशन के कॉइन्स ऐड नहीं होते
      </div>"""

assert old_buy_modal_html in idx_html, "old_buy_modal_html not found"
idx_html = idx_html.replace(old_buy_modal_html, new_buy_modal_html, 1)

old_buy_utr_field = """      <!-- UTR Input Field -->
      <div class="form-group" style="margin-bottom: 0.75rem; text-align: left;">
        <label style="font-size: 0.72rem; font-weight: 800; color: #000000; margin-bottom: 2px;">12-Digit Bank Payment UTR Number*</label>
        <input type="text" id="buy-coins-utr-input" class="form-control" maxlength="12" placeholder="e.g. 987654321012" style="font-family: monospace; font-size: 1rem; font-weight: 900; text-align: center; border: 1.5px solid #16a34a; background: #ffffff; color: #000000;">
      </div>

      <button type="button" class="btn btn-primary" onclick="submitBuyCoinsUtr()" style="width: 100%; padding: 0.75rem; font-weight: 900; font-size: 0.92rem; background: linear-gradient(135deg, #16a34a, #15803d); color: #ffffff; border-radius: 10px; box-shadow: 0 4px 14px rgba(22, 163, 74, 0.35);">
        ✅ Verify Payment & Add Coins ➔
      </button>"""

new_buy_utr_field = """      <!-- UTR Input Field -->
      <div class="form-group" style="margin-bottom: 0.55rem; text-align: left;">
        <label style="font-size: 0.72rem; font-weight: 800; color: #000000; margin-bottom: 2px;">12-Digit Bank Payment UTR Number*</label>
        <input type="text" id="buy-coins-utr-input" class="form-control" maxlength="12" placeholder="Enter real 12-digit Bank UTR" style="font-family: monospace; font-size: 1rem; font-weight: 900; text-align: center; border: 1.5px solid #16a34a; background: #ffffff; color: #000000;">
        <div id="buy-coins-utr-status" style="margin-top: 4px; font-size: 0.68rem; color: #15803d; font-weight: 700; display: flex; align-items: center; gap: 4px;">
          <span>🛡️</span> <span>Strict Security: गलत UTR डालने पर ₹0 ऐड होगा; Admin वेरिफिकेशन अनिवार्य है</span>
        </div>
      </div>

      <button type="button" class="btn btn-primary" onclick="submitBuyCoinsUtr()" style="width: 100%; padding: 0.75rem; font-weight: 900; font-size: 0.9rem; background: linear-gradient(135deg, #16a34a, #15803d); color: #ffffff; border-radius: 10px; box-shadow: 0 4px 14px rgba(22, 163, 74, 0.35);">
        📤 Submit UTR for Admin Verification ➔
      </button>

      <!-- Live Status Tracker for Submitted Coin UTRs -->
      <div id="user-coin-requests-status-box" style="display: none; margin-top: 0.65rem; text-align: left;"></div>"""

assert old_buy_utr_field in idx_html, "old_buy_utr_field not found"
idx_html = idx_html.replace(old_buy_utr_field, new_buy_utr_field, 1)

# Also update Driver Fleet card badge in index.html to show REJECTED_UTR clearly if Admin rejected a fake UTR
old_fleet_badge = """              <span style="background: ${isLive ? '#14532d' : '#78350f'}; color: ${isLive ? '#86efac' : '#fde68a'}; border: 1px solid ${isLive ? '#22c55e' : '#f59e0b'}; font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 6px;">
                ${isLive ? '✓ 100% LIVE ON PORTAL' : '⏳ PENDING ₹100 VERIFICATION'}
              </span>"""

new_fleet_badge = """              <span style="background: ${isLive ? '#14532d' : ((r.status || '').toUpperCase() === 'REJECTED_UTR' ? '#7f1d1d' : '#78350f')}; color: ${isLive ? '#86efac' : ((r.status || '').toUpperCase() === 'REJECTED_UTR' ? '#fca5a5' : '#fde68a')}; border: 1px solid ${isLive ? '#22c55e' : ((r.status || '').toUpperCase() === 'REJECTED_UTR' ? '#ef4444' : '#f59e0b')}; font-size: 0.68rem; font-weight: 800; padding: 2px 7px; border-radius: 6px;">
                ${isLive ? '✓ 100% LIVE ON PORTAL' : ((r.status || '').toUpperCase() === 'REJECTED_UTR' ? '❌ WRONG UTR REJECTED BY ADMIN' : '⏳ PENDING ₹100 ADMIN VERIFICATION')}
              </span>"""

assert old_fleet_badge in idx_html, "old_fleet_badge not found"
idx_html = idx_html.replace(old_fleet_badge, new_fleet_badge, 1)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(idx_html)

print("Successfully upgraded index.html! Length:", len(idx_html))
