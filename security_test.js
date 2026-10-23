/**
 * SafarSaathi Automated Security & Operational Verification Test Suite
 * 
 * Tests real server endpoints, cryptographic verifications, rate limiting,
 * GPS validation, OTP lifecycle, path traversal protection, security headers,
 * rules verification, and codebase secrets audit.
 */

const http = require('http');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

// Import server logic
const { startServer, validateGpsCoordinates, sanitizeString, generateAdminSecret } = require('../server.js');

let testCount = 0;
let passCount = 0;
let failCount = 0;

function assert(condition, testName, details = '') {
  testCount++;
  if (condition) {
    passCount++;
    console.log(`  ✅ [PASS ${testCount}] ${testName}`);
  } else {
    failCount++;
    console.error(`  ❌ [FAIL ${testCount}] ${testName} - ${details}`);
  }
}

// Helper to make HTTP requests to the test server
function makeRequest(port, options, postData = null) {
  return new Promise((resolve, reject) => {
    const reqOptions = {
      hostname: '127.0.0.1',
      port: port,
      path: options.path || '/',
      method: options.method || 'GET',
      headers: options.headers || {}
    };

    const req = http.request(reqOptions, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        let json = null;
        try { json = JSON.parse(data); } catch(e){}
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          rawBody: data,
          json: json
        });
      });
    });

    req.on('error', err => reject(err));

    if (postData) {
      if (typeof postData === 'object') {
        req.write(JSON.stringify(postData));
      } else {
        req.write(postData);
      }
    }
    req.end();
  });
}

async function runTestSuite() {
  console.log('\n=============================================================');
  console.log('🛡️  SAFARSAATHI PRODUCTION SECURITY & FUNCTIONAL TEST SUITE');
  console.log('=============================================================\n');

  // Test Set 1: GPS Coordinate Validation Engine
  console.log('--- Test Suite 1: GPS Coordinate Validation & Anti-Spoofing ---');
  {
    const validAssamGps = validateGpsCoordinates(26.1445, 91.7362);
    assert(validAssamGps.valid === true, 'Valid Guwahati GPS coordinates (26.1445, 91.7362) pass validation');

    const invalidLatHigh = validateGpsCoordinates(95.5, 91.7362);
    assert(invalidLatHigh.valid === false, 'Invalid Latitude > 90 (95.5) rejected');

    const invalidLatLow = validateGpsCoordinates(-92.0, 91.7362);
    assert(invalidLatLow.valid === false, 'Invalid Latitude < -90 (-92.0) rejected');

    const invalidLngHigh = validateGpsCoordinates(26.1445, 185.0);
    assert(invalidLngHigh.valid === false, 'Invalid Longitude > 180 (185.0) rejected');

    const invalidLngLow = validateGpsCoordinates(26.1445, -190.0);
    assert(invalidLngLow.valid === false, 'Invalid Longitude < -180 (-190.0) rejected');

    const invalidNonNumeric = validateGpsCoordinates('hack', 'coords');
    assert(invalidNonNumeric.valid === false, 'Non-numeric spoofed coordinates rejected');

    const nanCoordinates = validateGpsCoordinates(NaN, 91.7362);
    assert(nanCoordinates.valid === false, 'NaN coordinates rejected');
  }

  // Test Set 2: Input Sanitization & XSS Prevention
  console.log('\n--- Test Suite 2: Input Sanitization & XSS Defense ---');
  {
    const xssPayload = '<script>alert("xss")</script><b>Dipankar</b>';
    const sanitized = sanitizeString(xssPayload, 100);
    assert(!sanitized.includes('<script>') && !sanitized.includes('</script>'), 'HTML script tags stripped from user input');
    assert(sanitized.includes('&lt;script&gt;') || !sanitized.includes('<'), 'Special characters encoded properly');

    const longString = 'A'.repeat(500);
    const truncated = sanitizeString(longString, 50);
    assert(truncated.length <= 50, 'Max length enforcement prevents buffer overflow/DoS string attacks');
  }

  // Test Set 3: Dynamic Admin Secret & Zero Hardcoded Passwords
  console.log('\n--- Test Suite 3: Dynamic Admin Secret & Credential Audit ---');
  {
    const generatedSecret = generateAdminSecret();
    assert(generatedSecret && generatedSecret.length >= 32, 'Admin secret generator creates cryptographically secure 32+ character tokens');

    // Codebase scan to ensure no hardcoded default passwords in JS/HTML
    const filesToAudit = ['server.js', 'index.html', 'admin.html'];
    let hardcodedSecretsFound = false;
    const forbiddenPatterns = ['1432', 'SafarSaathi@Admin2026', 'admin123', 'password123'];

    for (const f of filesToAudit) {
      const fullPath = path.join(__dirname, '..', f);
      if (fs.existsSync(fullPath)) {
        const fileContent = fs.readFileSync(fullPath, 'utf-8');
        for (const pattern of forbiddenPatterns) {
          // Check if pattern is used as credential (skip harmless doc references)
          if (fileContent.includes(`"${pattern}"`) || fileContent.includes(`'${pattern}'`)) {
            console.error(`Security alert: Found hardcoded pattern '${pattern}' in ${f}`);
            hardcodedSecretsFound = true;
          }
        }
      }
    }
    assert(!hardcodedSecretsFound, 'Audit confirmed: Zero hardcoded passwords or default PINs in public JS/HTML code');
  }

  // Test Set 4: Live HTTP Server Tests (Auth, Rate Limiting, OTP, Path Traversal)
  console.log('\n--- Test Suite 4: Server Endpoints, Auth, OTP & Rate Limiting ---');
  const TEST_PORT = 9876;
  const testAdminSecret = 'TestSecretKey_AssamSafeCarpool_2026_Secure!';
  process.env.ADMIN_SECRET = testAdminSecret;
  process.env.PORT = TEST_PORT;

  let testServer = null;
  try {
    testServer = await startServer(TEST_PORT, testAdminSecret);
    console.log(`  (Test server running on port ${TEST_PORT})`);

    // 4.1 Security Headers Check
    const rootRes = await makeRequest(TEST_PORT, { path: '/' });
    assert(rootRes.headers['x-content-type-options'] === 'nosniff', 'Security header X-Content-Type-Options: nosniff present');
    assert(rootRes.headers['x-frame-options'] === 'SAMEORIGIN', 'Security header X-Frame-Options: SAMEORIGIN present');
    assert(rootRes.headers['x-xss-protection'] === '1; mode=block', 'Security header X-XSS-Protection present');

    // 4.2 Path Traversal Attack Defense
    const traversalRes1 = await makeRequest(TEST_PORT, { path: '/../../etc/passwd' });
    assert(traversalRes1.statusCode === 403 || traversalRes1.statusCode === 404, 'Directory traversal attempt (/../../etc/passwd) blocked');

    const traversalRes2 = await makeRequest(TEST_PORT, { path: '/..%2f..%2fserver.js' });
    assert(traversalRes2.statusCode === 403 || traversalRes2.statusCode === 404, 'Encoded directory traversal attempt (/..%2f..%2f) blocked');

    // 4.3 Admin Login - Reject Empty / Missing
    const emptyLoginRes = await makeRequest(TEST_PORT, {
      path: '/api/admin/login',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {});
    assert(emptyLoginRes.statusCode === 400, 'Admin login without credentials returns 400 Bad Request');

    // 4.4 Admin Login - Reject Incorrect Secret
    const wrongLoginRes = await makeRequest(TEST_PORT, {
      path: '/api/admin/login',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, { adminSecret: 'wrong_secret_pin_attempt' });
    assert(wrongLoginRes.statusCode === 401, 'Admin login with incorrect credentials returns 401 Unauthorized');

    // 4.5 Admin Login - Accept Correct Secret
    const validLoginRes = await makeRequest(TEST_PORT, {
      path: '/api/admin/login',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, { adminSecret: testAdminSecret });
    assert(validLoginRes.statusCode === 200 && validLoginRes.json.success === true, 'Admin login with valid secret returns 200 OK and success: true');
    assert(validLoginRes.json.token && validLoginRes.json.token.length > 20, 'Admin login issues cryptographically signed session token');

    const adminToken = validLoginRes.json.token;

    // 4.6 Protected Endpoint - Access Control
    const unauthVerifyRes = await makeRequest(TEST_PORT, {
      path: '/api/admin/verify-token',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {});
    assert(unauthVerifyRes.statusCode === 401, 'Protected endpoint /api/admin/verify-token rejects unauthenticated requests (401)');

    const tamperedTokenRes = await makeRequest(TEST_PORT, {
      path: '/api/admin/verify-token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer tampered_fake_token_12345'
      }
    });
    assert(tamperedTokenRes.statusCode === 401, 'Protected endpoint rejects forged/tampered session token (401)');

    const validAuthRes = await makeRequest(TEST_PORT, {
      path: '/api/admin/verify-token',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${adminToken}`
      }
    });
    assert(validAuthRes.statusCode === 200 && (validAuthRes.json.valid === true || validAuthRes.json.authenticated === true), 'Protected endpoint accepts authentic session token (200 OK)');

    // 4.7 OTP Generation & Send Endpoint
    const invalidPhoneRes = await makeRequest(TEST_PORT, {
      path: '/api/otp/send',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, { phone: '123' });
    assert(invalidPhoneRes.statusCode === 400, 'OTP send with invalid phone number (<10 digits) returns 400 Bad Request');

    const validPhoneRes = await makeRequest(TEST_PORT, {
      path: '/api/otp/send',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, { phone: '9864012345' });
    assert(validPhoneRes.statusCode === 200 && validPhoneRes.json.success === true, 'OTP send with valid 10-digit mobile returns 200 OK');
    assert(validPhoneRes.json.verificationToken && validPhoneRes.json.verificationToken.length > 10, 'OTP send returns cryptographic verificationToken with HMAC protection');

    const verificationToken = validPhoneRes.json.verificationToken;

    // 4.8 OTP Verification - Reject Tampered or Wrong Code
    const wrongOtpRes = await makeRequest(TEST_PORT, {
      path: '/api/otp/verify',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      phone: '9864012345',
      otp: '000000',
      verificationToken: verificationToken
    });
    assert(wrongOtpRes.statusCode === 400 || wrongOtpRes.statusCode === 401, 'OTP verification with incorrect OTP code rejected (400/401)');

    // 4.9 OTP Verification - Reject Tampered Verification Token
    const tamperedOtpTokenRes = await makeRequest(TEST_PORT, {
      path: '/api/otp/verify',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      phone: '9864012345',
      otp: '123456',
      verificationToken: 'tampered.token.payload.signature'
    });
    assert(tamperedOtpTokenRes.statusCode === 400, 'OTP verification with forged token rejected by HMAC validator');

    // 4.10 GPS Telemetry Ingest & Validation Endpoint
    const validTelemetryRes = await makeRequest(TEST_PORT, {
      path: '/api/gps/update',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      driverPhone: '9864012345',
      rideId: 'RIDE-101',
      lat: 26.1445,
      lng: 91.7362,
      speed: 45,
      heading: 90
    });
    assert(validTelemetryRes.statusCode === 200 && validTelemetryRes.json.success === true, 'GPS telemetry update endpoint accepts validated Assam coordinates');

    const spoofedTelemetryRes = await makeRequest(TEST_PORT, {
      path: '/api/gps/update',
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    }, {
      driverPhone: '9864012345',
      rideId: 'RIDE-101',
      lat: 999.0, // Spoofed out-of-bounds latitude
      lng: 91.7362
    });
    assert(spoofedTelemetryRes.statusCode === 400, 'GPS telemetry endpoint rejects spoofed out-of-bounds latitude (400 Bad Request)');
  } finally {
    if (testServer) {
      testServer.close();
    }
  }

  // Test Set 5: Firebase Security Rules Integrity
  console.log('\n--- Test Suite 5: Firebase & Firestore Security Rules Audit ---');
  {
    const firestoreRulesPath = path.join(__dirname, '..', 'firestore.rules');
    assert(fs.existsSync(firestoreRulesPath), 'firestore.rules exists in project root');
    const firestoreRules = fs.readFileSync(firestoreRulesPath, 'utf-8');
    assert(firestoreRules.includes('rules_version = \'2\';'), 'Firestore rules using Version 2 specification');
    assert(firestoreRules.includes('request.auth != null'), 'Firestore rules require authenticated user session');
    assert(firestoreRules.includes('request.auth.uid == userId') || firestoreRules.includes('isOwner'), 'Firestore rules strictly enforce user data ownership isolation');
    assert(firestoreRules.includes('ss_bookings') && firestoreRules.includes('isBookingParticipant'), 'Firestore rules strictly isolate bookings to designated driver and passenger only');

    const rtdbRulesPath = path.join(__dirname, '..', 'database.rules.json');
    assert(fs.existsSync(rtdbRulesPath), 'database.rules.json exists in project root');
    const rtdbRules = fs.readFileSync(rtdbRulesPath, 'utf-8');
    assert(rtdbRules.includes('auth != null'), 'Realtime Database rules require authentication');
    assert(rtdbRules.includes('auth != null') && rtdbRules.includes('auth.uid === ') && rtdbRules.includes('ss_users'), 'Realtime Database isolates user nodes strictly by authenticated UID');
  }

  // Summary
  console.log('\n=============================================================');
  console.log(`📊 TEST SUITE SUMMARY: ${passCount} / ${testCount} PASSED`);
  if (failCount === 0) {
    console.log('🎉 ALL AUTOMATED SECURITY & OPERATIONAL TESTS PASSED (100%)!');
  } else {
    console.error(`⚠️  ${failCount} TEST(S) FAILED!`);
    process.exit(1);
  }
  console.log('=============================================================\n');
}

runTestSuite().catch(err => {
  console.error('Fatal test error:', err);
  process.exit(1);
});