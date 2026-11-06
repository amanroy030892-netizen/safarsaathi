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

db.collection("rides").onSnapshot((snapshot) => {
    const listContainer = document.getElementById("rides-list");
    if (!listContainer) return;
    listContainer.innerHTML = "";

    if (snapshot.empty) {
        listContainer.innerHTML = "<p>Abhi koi live rides active nahi hain.</p>";
        return;
    }

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

    alert("Post Submit Ho Gaya Hai! Admin Panel Par UTR Confirmation Ke Liye Bhej Diya Gaya Hai.");
    e.target.reset();
});
