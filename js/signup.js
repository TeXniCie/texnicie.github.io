"use strict";

console.log("signup.js script loaded");

(() => {
    function signupForMailinglist(user_id, target) {
        let statusMsg = document.querySelector("#statusMsg");
        
        if (user_id == null || typeof user_id !== "string" || user_id.length == 0
        || target == null || typeof target !== "string" || target.length == 0) {
            statusMsg.style.color = "red";
            statusMsg.textContent = `Parameters missen.`;
            return;
        }

        statusMsg.style.color = "darkorange";
        statusMsg.textContent = `Toevoegen aan maillijst...`;
        
        fetch("https://icy3wowlug.execute-api.eu-north-1.amazonaws.com/texnicie/confirm-email", {
            mode: 'cors',    
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                'Access-Control-Allow-Origin': "*.amazonaws.com"
            },
            body: JSON.stringify({
                "user_id": user_id,
                "target": target
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
            if (!("success" in msg)) {
                statusMsg.style.color = "black";
                statusMsg.textContent = `Server antwoordde met ${JSON.stringify(msg, null, 4)}`;
                //emphasizeFallbackInstructions();
                return;
            }

            statusMsg.style.color = "green";
            if (msg["already_signedup"])
                statusMsg.textContent = "Je stond al op de mailinglijst :)";
            else
                statusMsg.textContent = "Succes, je bent toegevoegd aan de mailinglijst!";
        }).catch(e => {
            statusMsg.style.color = "red";
            statusMsg.textContent = `Error bij het verzenden van gegevens: ${e}`;
            //emphasizeFallbackInstructions();
        });
    }

    function onDocumentLoaded() {
        console.log("Document loaded");
        let searchParams = new URLSearchParams(window.location.search);
        let user_id = searchParams.get("user_id");
        let target = searchParams.get("target");

        if (email != null && challenge != null)
            signupForMailinglist(email, challenge || user_id);
    }

    document.addEventListener("DOMContentLoaded", () => {
        onDocumentLoaded();
    });
})();
