// ================= GLOBAL VARIABLES =================
let map;
let selectedLat = null;
let selectedLng = null;
let markers = [];
let markerGroup; // 🔥 clustering group
let userLat = null;
let userLng = null;



// ================= SET LOCATION =================
function setLocation(){

    const place = document.getElementById("locationInput").value;

    if (!place){
        alert("Please enter a location");
        return;
    }

    fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${place}`)
    .then(res => res.json())
    .then(data => {

        if (data.length === 0){
            alert("Location not found");
            return;
        }

        selectedLat = parseFloat(data[0].lat);
        selectedLng = parseFloat(data[0].lon);

        if (!map){
            map = L.map('map').setView([selectedLat, selectedLng], 13);

            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png')
                .addTo(map);

            // 🔥 initialize cluster group
            markerGroup = L.layerGroup();
            map.addLayer(markerGroup);
        } else {
            map.setView([selectedLat, selectedLng], 13);
        }

        markerGroup.clearLayers();

        let marker = L.marker([selectedLat, selectedLng]).addTo(markerGroup)
            .bindPopup("📍 Selected Location")
            .openPopup();
    });
}


// ================= SET CURRENT LOCATION =================
function getCurrentLocation(){

    navigator.geolocation.getCurrentPosition(

        function(position){

            userLat = position.coords.latitude;
            userLng = position.coords.longitude;

            alert("Current location set!");

            console.log(userLat, userLng);
        },

        function(error){
            alert("Location access denied");
        }

    );
}


// ================= DISTANCE FUNCTION =================
function getDistance(lat1, lon1, lat2, lon2) {
    let R = 6371; // km
    let dLat = (lat2-lat1) * Math.PI / 180;
    let dLon = (lon2-lon1) * Math.PI / 180;

    let a =
        Math.sin(dLat/2) * Math.sin(dLat/2) +
        Math.cos(lat1 * Math.PI/180) *
        Math.cos(lat2 * Math.PI/180) *
        Math.sin(dLon/2) * Math.sin(dLon/2);

    let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return (R * c).toFixed(2);
}


// ================= VENUES =================
function getVenues(){

    console.log("getVenues called");

    if (selectedLat === null || selectedLng === null){
        alert("❗ Please click 'Set Location' first!");
        return;
    }

    if (!map){
        alert("Map not initialized");
        return;
    }

    // 🔥 user budget input
    let userBudget = document.getElementById("venueBudget")?.value || 0;
    document.getElementById("loading").style.display = "block";

    fetch("/venues", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({
        
            user_lat: userLat,
            user_lng: userLng,
            venue_lat: selectedLat,
            venue_lng: selectedLng,
            search_place: document.getElementById("locationInput").value,
            type: document.getElementById("userVenueType").value,
            budget: document.getElementById("venueBudget").value
        })
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("loading").style.display = "none";

        console.log("VENUES:", data);

        if (!data || data.length === 0){
            document.getElementById("list").innerHTML =
                "<p>No venues found for this location</p>";
            return;
        }

        // ================= 🔥 RECOMMENDATION LOGIC =================

        // distance function
        function getDistance(lat1, lon1, lat2, lon2){
            let R = 6371;
            let dLat = (lat2-lat1) * Math.PI/180;
            let dLon = (lon2-lon1) * Math.PI/180;

            let a =
                Math.sin(dLat/2) * Math.sin(dLat/2) +
                Math.cos(lat1*Math.PI/180) *
                Math.cos(lat2*Math.PI/180) *
                Math.sin(dLon/2) * Math.sin(dLon/2);

            let c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
            return (R*c).toFixed(2);
        }

        // use backend values only
        data = data.map(v => {

             let finalPrice = 0;

    // public venues
             if (v.price === "Not Available"){

                   finalPrice = 0;

             } else {

                  finalPrice = parseFloat(v.price || 0);
             }

             return {
                     ...v,
                     distance: parseFloat(v.distance || 0),
                     price: finalPrice
           };
            });

        // sort by best match
        data.sort((a, b) => {
            return (a.distance + a.price/100000) - (b.distance + b.price/100000);
        });

        // filter by budget
        if (userBudget > 0){
            data = data.filter(v => {

    // keep public venues
               if (v.price_type === "Public Venue"){
                  return true;
          }

               return Number(v.price) <= Number(userBudget);
                });
            }

        let html = "";

        if (markerGroup){
            markerGroup.clearLayers();
           }
        

        // ================= 🔥 DISPLAY =================
        console.log("DISPLAYING:", data);
        data.forEach((v, index) => {

            let badge = "";
if(index === 0){

    badge = `
    <div class="badge bg-warning text-dark mb-2">
        🏆 Best Match
    </div>
    `;
}

html += `

<div class="col-md-4 mb-3">

    <div class="card p-3 h-100">

        ${badge}

        ${v.image ? `
        <img src="/static/uploads/${v.image}"
             class="img-fluid rounded mb-2"
             style="height:200px;width:100%;object-fit:cover;">
        ` : ""}

        <h5>${v.name}</h5>

        <p>
        🏛 Venue Type:
        <b>${v.type || "Venue"}</b>
        </p>

        <p>
        💰 ${
            v.price_type === "Public Venue"
            ? "Price Not Available"
            : `₹${Number(v.price).toLocaleString()}`
        }
        (${v.price_type})
        </p>

        

        <p>
        📍 ${v.distance} km away
        </p>

        <p>
        ${
            v.price_type === "Public Venue"
            ? "🌍 Google Maps Venue"
            : "🏢 Owner Listed Venue"
        }
        </p>

        ${v.phone ? `
        <p>📞 ${v.phone}</p>
        ` : ""}
         ${v.email ? `
        <p>✉ ${v.email}</p>
        ` : ""}

        <p>

         ⭐ ${Number(v.rating || 0).toFixed(1)}/5

        </p>
        
        <button
             class="btn btn-warning mt-2"
             data-bs-toggle="modal"
             data-bs-target="#reviewModal"
             onclick="setVenueId(${v.id})">

                  Rate Venue
        
        </button>
       
        <p style="
              font-size:14px;
            opacity:0.9;
        ">

        💬 ${v.comment ? v.comment : "No reviews yet"}

        </p> 

        <a href="${v.link}"
           target="_blank"
           class="btn btn-primary mt-2">

           Open in Maps

        </a>

    </div>

</div>
`;


            // 🔥 MAP MARKER
            if (v.lat===null || v.lng===null){
                return;
                }
            let markerLat =
                  (v.lat !== null && v.lat !== 0)
                  ? v.lat
                  : selectedLat;

            let markerLng =
                 (v.lng !== null && v.lng !== 0)
                 ? v.lng
                 : selectedLng;

            L.marker([markerLat, markerLng]).addTo(markerGroup)
                .bindPopup(`
                    <b>${v.name}</b><br>
                    📍 ${v.distance} km<br>
                    💰 ${
                       v.price_type === "Public Venue"
                     ? "Price Not Available"
                     : `₹${v.price}`
                    }<br>
                    ⭐ ${v.rating}<br>
                    <a href="${v.link}" target="_blank">Open</a>
                `);
        });

        document.getElementById("list").innerHTML = html;
        console.log(html);

        if (markerGroup.getLayers().length > 0){
            map.fitBounds(markerGroup.getBounds());
        };
    })
    .catch(err => {
        console.error("Error:", err);
          });
    }


// ================= CHATBOT =================
function send(){


    let input = document.getElementById("msg");

    let msg = input.value.trim();

    if(!msg) return;

    let chatBox = document.getElementById("chatBox");

    // USER MESSAGE
    chatBox.innerHTML += `

    <div class="user-msg">

        <div class="user-bubble">
            ${msg}
        </div>

    </div>
    `;

    // AUTO SCROLL
    chatBox.scrollTop = chatBox.scrollHeight;

    // CLEAR INPUT
    input.value = "";

    // SHOW LOADING
    document.getElementById("chatLoading").style.display = "block";

    fetch("/chatbot", {

        method: "POST",

        headers:{
            "Content-Type":"application/json"
        },

        body: JSON.stringify({

            message: msg,
            lat: selectedLat,
            lng: selectedLng

        })
    })

    .then(res => res.json())

    .then(data => {

        // HIDE LOADING
        document.getElementById("chatLoading").style.display = "none";

        // BOT MESSAGE
        chatBox.innerHTML += `

        <div class="bot-msg">

            <div class="bot-bubble">

                ${data.reply}

            </div>

        </div>
        `;

        // AUTO SCROLL
        chatBox.scrollTop = chatBox.scrollHeight;

    })

    .catch(err => {

        console.log(err);

        document.getElementById("chatLoading").style.display = "none";

        chatBox.innerHTML += `

        <div class="bot-msg">

            <div class="bot-bubble">

                Chatbot failed.

            </div>

        </div>
        `;

    });
}

// ================= CLEAR CHAT =================
function clearChat(){

    let chatBox = document.getElementById("chatBox");

    chatBox.innerHTML = "";

}


// ================= BUTTON =================
document.addEventListener("DOMContentLoaded", function(){
    const btn = document.getElementById("venueBtn");

    if (btn){
        btn.addEventListener("click", function(){
            console.log("Button clicked");   // 🔥 debug
            getVenues();
        });
    }
});


// ================= ENTER KEY =================
document.addEventListener("DOMContentLoaded", function(){

    let input = document.getElementById("msg");

    if(input){

        input.addEventListener("keypress", function(e){

            if(e.key === "Enter"){

                e.preventDefault();

                send();

            }

        });

    }

});

function setVenueId(id){

    console.log("VENUE ID:", id);

    document.getElementById(
        "reviewVenueId"
    ).value = id;
}

async function submitReview(){

    let venue_id =
    document.getElementById(
        "reviewVenueId"
    ).value;

    let rating =
    document.getElementById(
        "ratingInput"
    ).value;

    let comment =
    document.getElementById(
        "commentInput"
    ).value;

    let res = await fetch(
        "/submit_review",
        {

            method:"POST",

            headers:{
                "Content-Type":"application/json"
            },

            body:JSON.stringify({

                venue_id,
                rating,
                comment
            })
        }
    );

    let data = await res.json();

    alert("Review Submitted!");

bootstrap.Modal
.getInstance(
document.getElementById(
"reviewModal"
)
).hide();

// reload venue cards properly
document.getElementById("list").innerHTML = "";

setTimeout(() => {

    getVenues();

}, 300);
}
