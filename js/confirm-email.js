"use strict";

console.log("Confirm-email.js script loaded");

(() => {
    function confirmEmail(email, challenge) {
        let statusMsg = document.querySelector("#statusMsg");
            fetch("https://icy3wowlug.execute-api.eu-north-1.amazonaws.com/texnicie/confirm-email", {
            mode: 'cors',    
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'Access-Control-Allow-Origin': "*.amazonaws.com"
            },
            body: JSON.stringify({
                "email": email,
                "challenge": challenge
            })
        }).then(res => res.json())
        .then(msg => {
            console.log("Response:");
            console.log(msg);

            if ("error" in msg) {
                statusMsg.style.color = "red";
                statusMsg.textContent = `Error: ${msg["error"]}`;
                //emphasizeFallbackInstructions();
                return;
            }
            if (!("succes" in msg)) {
                statusMsg.style.color = "black";
                statusMsg.textContent = `Server antwoordde met ${JSON.stringify(msg, null, 4)}`;
                //emphasizeFallbackInstructions();
                return;
            }

            statusMsg.style.color = "green";
            if (msg["already_confirmed"])
                statusMsg.textContent = "Je e-mail was al bevestigd :)";
            else
                statusMsg.textContent = "Succes, je e-mail is bevestigd! Tot binnenkort!";
        }).catch(e => {
            statusMsg.style.color = "error";
            statusMsg.textContent = `Error bij het verzenden van gegevens: ${e}`;
            //emphasizeFallbackInstructions();
        });
    }

    function onDocumentLoaded() {
        console.log("Document loaded");
        let searchParams = new URLSearchParams(window.location.search);
        let email = searchParams.get("email");
        let challenge = searchParams.get("challenge");
        console.log(`Email: ${email}`);
        console.log(`Challenge: ${challenge}`);

        confirmEmail(email, challenge);
    }

    document.addEventListener("DOMContentLoaded", () => {
        onDocumentLoaded();
    });
})();
