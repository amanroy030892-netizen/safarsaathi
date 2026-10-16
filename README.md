# SafarSaathi - Updates & Architecture Guide

## 1. Admin-Only Video Ad Management (ऐड अपलोड केवल एडमिन पोर्टल से)
* **Problem Addressed:** Customer screen should not allow public ad uploads. Ads are strictly for platform monetization and official promotions.
* **Implementation:**
  - Removed all public video upload buttons and modals from `index.html`.
  - Added the **Home Screen Sponsor Video Ad Manager** directly inside `admin.html` (Admin PIN: 1432).
  - Admin can upload any MP4/WebM video ad (up to 1.5 minutes / 90 seconds) with sound, set title, description, and sponsor WhatsApp link.
  - On publishing, the ad syncs in real time via `BroadcastChannel` and Firebase Firestore to all customer Home screens.
  - Video ad is only active on the initial Home landing page (Login/Register view) and immediately stops and hides when navigating or logging in.

---

## 2. Default Drive Mode, Car Scene & Point of View (POV) Engine
* **Drive Mode by Default:** The map initializes in **Drive Mode (3D Navigation Car Scene)** from the start.
* **Car Scene (Navigation Mode):** Displays a 3D Navigation Vehicle Chevron with headlights beam and motion radar pointing and turning in the exact direction of travel.
* **Stationary Point of View (POV):** When a customer is stopped/stationary (speed < 1.5 km/h), the marker transforms into a **Point of View (POV) mode** with a 60° compass flashlight beam showing the exact direction the customer/phone is facing in the world.
* **Walking Direction Tracking:** When walking on foot (speed 1.5 - 7 km/h), the map shows a directional walking chevron displaying live walking speed (e.g. `🚶 4 km/h`) and heading direction.
