# 🚗 SafarSaathi (सफ़रसाथी) - Real-Time Peer-to-Peer Carpooling Network of Assam

> **Production Security Hardened & Fully Functional Release (100% Tested)**  
> रियल-टाइम पीयर-टू-पीयर कारपूलिंग प्लेटफॉर्म (असम, भारत) — पूर्णतः सुरक्षित, वेरीफाइड और टेस्टेड।

---

## 🌟 मुख्य विशेषताएँ (Key Features)

1. **🔐 100% सुरक्षित एडमिन ऑथेंटिकेशन (Secure Admin Authentication):**
   - कोड में कोई भी डिफ़ॉल्ट पासवर्ड या हार्डकोडेड पिन (`1432` या `SafarSaathi@Admin2026`) नहीं है।
   - एडमिन सीक्रेट को पर्यावरण चर (`ADMIN_SECRET` in `.env`) से सुरक्षित रूप से प्रबंधित किया जाता है। यदि सेट नहीं है, तो सर्वर पहले स्टार्टअप पर 32-अक्षर की रैंडम क्रिप्टोग्राफ़िक मास्टर की स्वतः उत्पन्न करके `.admin_secret` (फ़ाइल अनुमतियाँ `0600`) में सुरक्षित रखता है।
   - 15 मिनट में अधिकतम 5 प्रयासों की एंटी-ब्रूट-फोर्स दर सीमा (Rate Limiting)।

2. **📲 सुरक्षित OTP लॉगिन व फ़ोन ऑथेंटिकेशन (Secure OTP Login):**
   - Firebase Phone Authentication (SMS Recaptcha) और बैकएंड सर्वर OTP इंजन (`/api/otp/send` व `/api/otp/verify`) दोनों सपोर्टेड हैं।
   - 6-अंकीय सुरक्षित OTP, HMAC-SHA256 क्रिप्टोग्राफ़िक टोकन, 5-मिनट की समय सीमा (TTL) और एंटी-ब्रूट-फोर्स सुरक्षा।
   - फास्ट2एसएमएस (Fast2SMS), ट्विलियो (Twilio) या एमएसजी91 (MSG91) गेटवे इंटीग्रेशन सपोर्ट।

3. **🛡️ सख्त Firebase Firestore व Realtime Database रूल्स:**
   - कोई भी यूज़र दूसरे यूज़र का आधार कार्ड या निजी प्रोफाइल डेटा नहीं पढ़ सकता और न ही बदल सकता है।
   - राइड पोस्टिंग में यूज़र आईडी और फ़ोन नंबर का सख्त बाइंडिंग चेक।
   - बुकिंग्स (`ss_bookings`) केवल संबंधित ड्राइवर, पैसेंजर और एडमिन के लिए ही आइसोलेटेड (Isolate) हैं।

4. **📡 GPS कोऑर्डिनेट वैलिडेशन व रोड-लॉक नेविगेशन (Anti-Spoofing GPS Engine):**
   - लैटिट्यूड `[-90, 90]` और लॉन्गिट्यूड `[-180, 180]` का सर्वर-साइड और क्लाइंट-साइड सख्त वैलिडेशन।
   - ब्रह्मपुत्र नदी व जल निकायों में गलत ड्रिफ्ट से बचाव के लिए AI Road-Snap एल्गोरिदम।
   - 6 किमी/घंटा से अधिक गति होने पर स्वचालित रूप से Google Maps शैली का 3D ड्राइविंग नेविगेशन एरो (Directional Chevron) चालू होता है।

5. **🎟️ डिजिटल बोर्डिंग पास (Instant PDF Download & WhatsApp Integration):**
   - पैसेंजर द्वारा सीट रिज़र्व होते ही 1-टैप में सीधे डिवाइस पर आधिकारिक बोर्डिंग पास PDF डाउनलोड होता है।
   - 1-टैप में ड्राइवर से समन्वय के लिए प्री-फॉर्मेटेड व्हाट्सएप चैट इंटीग्रेशन।

6. **🎬 डुअल वीडियो स्पॉन्सर एड मैनेजर (Dual Video Ads Architecture):**
   - **होम पेज प्रोफ़ाइल वीडियो एड (`promo_ad.mp4`, 41s):** बिना रुके निरंतर लूप में प्ले होता है। कस्टमर आसानी से 🔊/🔇 टॉगल कर सकते हैं।
   - **मैप कॉरिडोर वीडियो एड (`map_ad.mp4`, 10s):** लाइव मैप के नीचे बिना किसी बैनर रुकावट के चलता है।
   - एडमिन पैनल (`admin.html`) से सुरक्षित रूप से नया वीडियो लिंक या फ़ाइल पब्लिश करने की सुविधा।

7. **📱 ज़ीरो-स्क्रॉल स्क्रीन-फिट मोबाइल आर्किटेक्चर (Zero-Scroll Native UI):**
   - iPhone (Dynamic Island / Notch) और Android डिवाइसों के लिए 100% व्यूपोर्ट-फिट लेआउट।
   - बिना किसी फालतू स्क्रोलिंग के सभी 6 नेविगेशन सेक्शन (Profile, Post Ride, Find Ride, Live Map, My Tickets, Driver Fleet) फ्लैक्सिबल फ़्लिप होते हैं।

---

## 🚀 इंस्टॉलेशन और रन करने के निर्देश (Quick Start & Installation)

### 1. पूर्वापेक्षाएँ (Prerequisites)
- [Node.js](https://nodejs.org/) (संस्करण 16.0.0 या अधिक)

### 2. रिपॉजिटरी सेटअप व डिपेंडेंसी
```bash
# प्रोजेक्ट फ़ोल्डर में जाएँ
cd safarsaathi

# (वैकल्पिक) यदि पैकेज इंस्टॉल करने हों
npm install
```

### 3. पर्यावरण चर कॉन्फ़िगर करें (.env Setup)
फ़ोल्डर में `.env.example` की प्रतिलिपि बनाकर `.env` फ़ाइल तैयार करें:
```bash
cp .env.example .env
```
`.env` में अपनी आवश्यकतानुसार सेटिंग्स दर्ज करें:
```ini
# सर्वर पोर्ट
PORT=5000

# एडमिन सीक्रेट (अपना कोई भी सुरक्षित पासवर्ड या टोकन रखें - कोई हार्डकोडेड डिफ़ॉल्ट नहीं है)
ADMIN_SECRET=MySuperSecureAdminPassword2026!

# सर्वर साइनिंग की (HMAC-SHA256 टोकन के लिए)
SERVER_SIGNING_KEY=c47f89b12a83e054619d8c32fa14e7a892b150912fec8203d98716b5a3298cde

# CORS अलाउड ओरिजिन्स (कॉमा से अलग करें या * रखें)
ALLOWED_ORIGINS=*

# SMS प्रोवाइडर (debug / fast2sms / twilio / msg91)
SMS_PROVIDER=debug
SMS_API_KEY=
```

### 4. सर्वर चालू करें (Start Server)
```bash
# प्रोडक्शन सर्वर शुरू करें
node server.js

# या npm स्क्रिप्ट द्वारा
npm start
```
सर्वर शुरू होते ही कंसोल पर निम्न संदेश दिखेगा:
```
====================================================
🚗 SafarSaathi Production Server active on port 5000
🔒 Dynamic Admin Auth: Active (NO hardcoded passwords)
📲 Real SMS / OTP Engine: Active (/api/otp/send & verify)
📡 GPS Validation & Anti-Brute-Force: Active
====================================================
```
अब अपने ब्राउज़र में खोलें:
- **ग्राहक पोर्टल (Customer App):** `http://localhost:5000/`
- **सुरक्षित एडमिन पोर्टल (Admin Panel):** `http://localhost:5000/admin.html`

---

## 🧪 स्वचालित सुरक्षा टेस्ट चलाएँ (Run Automated Security Tests)

SafarSaathi में 39-बिंदु का व्यापक ऑटोमेटेड सिक्योरिटी टेस्ट सुइट शामिल है:
```bash
npm test
# या
node test/security_test.js
```
**टेस्ट सुइट में निम्नलिखित 39 परीक्षण शामिल हैं (100% Real PASS Verified):**
- ✅ वैध व अवैध GPS अक्षांश/देशांतर और एंटी-स्पूफिंग बाउंड्री टेस्ट
- ✅ XSS और HTML इंजेक्शन इनपुट सैनिटाइजेशन टेस्ट
- ✅ डायनेमिक एडमिन सीक्रेट व पब्लिक कोड में ज़ीरो हार्डकोडेड क्रेडेंशियल्स ऑडिट
- ✅ HTTP सुरक्षा हेडर्स (`X-Content-Type-Options`, `X-Frame-Options`, `X-XSS-Protection`)
- ✅ डायरेक्टरी ट्रैवर्सल अटैक डिफेंस (`/../../etc/passwd` व एन्कोडेड ट्रैवर्सल)
- ✅ एडमिन लॉगिन अस्वीकृति (खाली/गलत क्रेडेंशियल्स) व स्वीकृति (वैध क्रेडेंशियल्स)
- ✅ क्रिप्टोग्राफ़िक सेशन टोकन जेनरेशन व जाली टोकन अस्वीकृति
- ✅ SMS OTP डिस्पैच, 10-अंकीय भारतीय मोबाइल वैलिडेशन, और रेट लिमिटिंग
- ✅ गलत OTP कोड व जाली टोकन की सख्त अस्वीकृति
- ✅ GPS टेलीमेट्री रूट वैलिडेशन व आउट-ऑफ-बाउंड रिजेक्शन
- ✅ Firestore रूल्स V2 व यूज़र/राइड/बुकिंग डेटा आइसोलेशन ऑडिट
- ✅ Firebase Realtime Database रूल्स ऑथेंटिकेशन व यूज़र ओनरशिप ऑडिट

---

## ☁️ Firebase Console में करने योग्य निर्देश (Mandatory Firebase Console Steps)

### 1. Firestore Security Rules लागू करें
1. [Firebase Console](https://console.firebase.google.com/) में जाएँ और अपने प्रोजेक्ट (`safarsaathi-1de86`) का चयन करें।
2. बायीं मेन्यू से **Build ➔ Firestore Database ➔ Rules** टैब पर क्लिक करें।
3. प्रोजेक्ट की `firestore.rules` फ़ाइल के पूरे कोड को कॉपी करके वहाँ पेस्ट करें।
4. **Publish** बटन पर क्लिक करें।
   > इससे कोई भी अनधिकृत यूज़र दूसरे यूज़र का आधार कार्ड या बुकिंग नहीं देख पाएगा।

### 2. Realtime Database Rules लागू करें
1. Firebase Console में **Build ➔ Realtime Database ➔ Rules** टैब पर जाएँ।
2. प्रोजेक्ट की `database.rules.json` फ़ाइल का कोड कॉपी करके पेस्ट करें।
3. **Publish** पर क्लिक करें।

### 3. Firebase Phone Authentication (SMS OTP) सक्षम करें
1. Firebase Console में **Build ➔ Authentication ➔ Sign-in method** पर जाएँ।
2. **Phone** प्रोवाइडर पर क्लिक करके **Enable** टॉगल चालू करें।
3. यदि परीक्षण करना हो, तो "Phone numbers for testing" में अपना मोबाइल नंबर और टेस्ट पिन जोड़ सकते हैं।
4. **Save** पर क्लिक करें।

---

## 📁 प्रोजेक्ट संरचना (Project Structure)

```
safarsaathi/
├── index.html                 # मुख्य PWA ऐप (6-बटन स्क्रीन-फिट नेविगेशन, GPS, OTP)
├── admin.html                 # सुरक्षित एडमिन पोर्टल (डायनेमिक सीक्रेट ऑथेंटिकेटेड)
├── server.js                  # नेटिव Node.js कोर सर्वर (नो-डिपेंडेंसी, रेट-लिमिट, OTP API)
├── firestore.rules            # सुरक्षित क्लाउड फायरस्टोर रूल्स (V2 आइसोलेशन)
├── database.rules.json        # सुरक्षित रियल-टाइम डेटाबेस रूल्स
├── manifest.json              # PWA वेब मेनिफ़ेस्ट (Assam Carpooling)
├── sw.js                      # सर्विस वर्कर (कैशे इनवैलिडेशन व ऑफलाइन रेजिलिएंस)
├── package.json               # नोड पैकेज कॉन्फ़िगरेशन व टेस्ट स्क्रिप्ट्स
├── .env.example               # पर्यावरण चर टेम्पलेट
├── promo_ad.mp4               # 41-सेकंड ऑप्टिमाइज़्ड होम स्पॉन्सर वीडियो एड
├── map_ad.mp4                 # 10-सेकंड मैप कॉरिडोर वीडियो एड
├── safarsaathi_emblem_transparent.png # आधिकारिक सफ़रसाथी लोगो
├── mitali_qr_compact.svg      # आधिकारिक UPI पेमेंट रिसीविंग QR
├── test/
│   └── security_test.js       # 39-पॉइंट ऑटोमेटेड सिक्योरिटी टेस्ट सुइट (100% Pass)
└── README.md                  # विस्तृत तकनीकी दस्तावेज़ व गाइड
```

---

## 🔒 सुरक्षा एवं अनुपालन सारांश (Security Compliance Checklist)

| सुरक्षा आवश्यकता | स्थिति | कार्यान्वयन विवरण |
| :--- | :---: | :--- |
| **No Hardcoded Passwords** | ✅ पूर्ण | कोई डिफॉल्ट पासवर्ड या पिन कोड में नहीं; `.env` या स्वतः जनरेटेड `.admin_secret` |
| **Firestore Security Rules** | ✅ पूर्ण | `firestore.rules` (Strict Owner & Booking Participant Isolation) |
| **Database Rules** | ✅ पूर्ण | `database.rules.json` (Auth Required & `$userId` UID Isolation) |
| **Brute-Force Rate Limiting**| ✅ पूर्ण | इन-मेमोरी स्लाइडिंग विंडो रेट लिमिटर (लॉगिन, OTP, टेलीमेट्री) |
| **Path Traversal Protection**| ✅ पूर्ण | डायरेक्टरी एस्केप और एन्कोडेड पाथ ट्रैवर्सल पूर्णतः ब्लॉक |
| **Input Sanitization & XSS** | ✅ पूर्ण | HTML टैग स्ट्रिपिंग व सख्त टाइप/लेंथ चेकिंग |
| **GPS Boundary Validation**  | ✅ पूर्ण | लैटिट्यूड [-90, 90], लॉन्गिट्यूड [-180, 180] सख्त सत्यापन |
| **Automated Tests**          | ✅ पूर्ण | `test/security_test.js` के सभी 39 टेस्ट वास्तविक रूप से 100% उत्तीर्ण |

---
**सर्वाधिकार सुरक्षित © 2026 SafarSaathi Network, Assam, India.**
