const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "safarsaathi.firebaseapp.com",
    projectId: "safarsaathi",
    storageBucket: "safarsaathi.appspot.com",
    messagingSenderId: "123456789",
    appId: "1:123456789:web:abcdef"
};

if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const db = firebase.firestore();

// Admin Real-time Listener for Pending Approvals
db.collection("rides").where("status", "==", "PENDING_ADMIN_UTR_CONFIRMATION")
    .onSnapshot((snapshot) => {
        const pendingContainer = document.getElementById("admin-pending-list");
        pendingContainer.innerHTML = "";

        if (snapshot.empty) {
            pendingContainer.innerHTML = "<p>No pending approvals.</p>";
            return;
        }

        snapshot.forEach((doc) => {
            const data = doc.data();
            const div = document.createElement("div");
            div.className = "pending-card";
            div.innerHTML = `
                <p><b>Driver:</b> ${data.driverName} | <b>Vehicle:</b> ${data.vehicleNo}</p>
                <p><b>Route:</b> ${data.route}</p>
                <p><b>UTR / Transaction:</b> <mark>${data.utr}</mark></p>
                <button onclick="approveRide('${doc.id}')" class="btn-approve">Approve Ride</button>
                <button onclick="rejectRide('${doc.id}')" class="btn-reject">Reject</button>
            `;
            pendingContainer.appendChild(div);
        });
    });

function approveRide(id) {
    db.collection("rides").doc(id).update({ status: "APPROVED" });
}

function rejectRide(id) {
    db.collection("rides").doc(id).delete();
}
