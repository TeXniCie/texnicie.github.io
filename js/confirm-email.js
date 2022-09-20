"use strict";

console.log("Confirm-email.js script loaded");



(() => {
    function onDocumentLoaded() {
        console.log("Document loaded");
        let searchParams = new URLSearchParams(window.location.search);
        let email = searchParams.get("email");
        let challenge = searchParams.get("challenge");
        console.log(`Email: ${email}`);
        console.log(`Challenge: ${challenge}`);
    }

    document.addEventListener("DOMContentLoaded", () => {
        onDocumentLoaded();
    });
})();
