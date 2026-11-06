// Firebase Configuration - Paste your Firebase Console Config Details Here
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "safarsaathi.firebaseapp.com",
    projectId: "safarsaathi",
    storageBucket: "safarsaathi.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef"
};

// Initialize Firebase
if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const db = firebase.firestore();

// Real-time listener for Posts
db.collection("rides").onSnapshot((snapshot) => {
    const listContainer = document.getElementById("rides-list");
    if (!listContainer) return;
    listContainer.innerHTML = "";

    snapshot.forEach((doc) => {
        const data = doc.data();
        if (data.status === "APPROVED") {
            const card = document.createElement("div");
            card.className = "ride-card";
            card.innerHTML = `
                <h4>🚘 ${data.driverName} (${data.vehicleNo})</h4>
                <p><b>Route:</b> ${data.route}</p>
                <span class="badge active">LIVE ONLINE</span>
            `;
            listContainer.appendChild(card);
        }
    });
});

// Handle Form Submit
document.getElementById("ride-form")?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("driver-name").value;
    const vehicle = document.getElementById("vehicle-no").value;
    const route = document.getElementById("route-info").value;
    const utr = document.getElementById("utr-number").value;

    await db.collection("rides").add({
        driverName: name,
        vehicleNo: vehicle,
        route: route,
        utr: utr,
        status: "PENDING_ADMIN_UTR_CONFIRMATION",
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
    });

    alert("Post Submitted! Pending Admin UTR Confirmation.");
    e.target.reset();
});
