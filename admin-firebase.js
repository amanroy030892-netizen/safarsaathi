const firebaseConfig = {
    apiKey: "AIzaSyD6duAA-IgREunOMqe9WSHgvd6JPBGw2fw",
    authDomain: "safarsaathi-1de86.firebaseapp.com",
    databaseURL: "https://safarsaathi-1de86-default-rtdb.asia-southeast1.firebasedatabase.app",
    projectId: "safarsaathi-1de86",
    storageBucket: "safarsaathi-1de86.appspot.com",
    messagingSenderId: "560392119536",
    appId: "1:560392119536:web:e05ea0af4804b86fc2ce35",
    measurementId: "G-4E5YGMH43H"
};

if (!firebase.apps.length) {
    firebase.initializeApp(firebaseConfig);
}
const db = firebase.firestore();

db.collection("rides").where("status", "==", "PENDING_ADMIN_UTR_CONFIRMATION")
    .onSnapshot((snapshot) => {
        const pendingContainer = document.getElementById("admin-pending-list");
        if (!pendingContainer) return;
        pendingContainer.innerHTML = "";

        if (snapshot.empty) {
            pendingContainer.innerHTML = "<p>Koi bhi pending UTR request nahi hai.</p>";
            return;
        }

        snapshot.forEach((doc) => {
            const data = doc.data();
            const div = document.createElement("div");
            div.className = "pending-card";
            div.innerHTML = `
                <p><b>Driver Name:</b> ${data.driverName} | <b>Vehicle No:</b> ${data.vehicleNo}</p>
                <p><b>Route:</b> ${data.route}</p>
                <p><b>UTR Number:</b> <mark style="background:#ffeb3b; padding:2px 6px; font-size:16px;">${data.utr}</mark></p>
                <button onclick="approveRide('${doc.id}')" class="btn-approve">Approve Post</button>
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
