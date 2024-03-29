"use strict";

function getURLLanguage() {
    let m = window.location.pathname.match(/^(\/(?<language>en))?(?<path>(\/.*)?)$/);
    if (m == null) {
        console.error("Could not determine language of url");
        return "nl";
    }
    let lang = m.groups.language || "nl";
    return lang;
}

function setLanguage(lang, urlParams=null) {
    if (!["nl", "en"].includes(lang))
            lang = "en";

    let m = window.location.pathname.match(/^(\/en)?(?<path>(\/.*)?)$/);
    if (m == null)
        console.error("Could not match pathname!");
    
    let langPrefix = `/${lang}`;
    if (lang == "nl")
        langPrefix = "";

    let nonLocalizedPath = m.groups.path || "/";
    let newPath = langPrefix + nonLocalizedPath;
    newPath = newPath.match(/^(?<path>\/.*)\/?$/).groups.path;

    // if (newPath.endsWith("/"))
    // 	newPath = newPath.substring(0, newPath.length - 1);
    let search = window.location.search;
    if (urlParams != null) {
        search = urlParams.toString();
        if (search.length > 0)
            search = `?${search}`;
    }
    
    let newLocation = newPath + search + (window.location.hash || "");
    console.log(`Redirecting ${window.location} -> ${newLocation}`);

    window.location.href = newLocation;
}

function languageRedirect() {
    let urlParams = new URLSearchParams(window.location.search);
    let lang = urlParams.get("setlanguage");
    if (lang != null) {
        urlParams.delete("setlanguage");

        setLanguage(lang, urlParams);
    }
}

function gotoEN() {
    setLanguage("en");
}
function gotoNL() {
    setLanguage("nl");
}

let registerCheckboxes;

function submitRegister() {
    let formEl = document.querySelector("#inschrijfSubmitForm");

    let statusMsg = document.querySelector("#statusMsg");

    statusMsg.style.color = "black";
    statusMsg.textContent = "Checken...";

    let inputEmailEl = document.querySelector("#inputEmail");

    let email = inputEmailEl.value;
    // console.log(`Email: ${email}`);

    // let m = email.match(/^\S+@\S+\.\S+$/);
    // if (m == null) {
    //     statusMsg.style.color = "red";
    //     statusMsg.textContent = "Incorrecte e-mail";
    //     inputEmailEl.setCustomValidity("Incorrecte e-mail");
    //     //inputEmailEl.reportValidity();
    //     // inputEmailEl.classList.add("was-validated");
    //     // formEl.reportValidity();
    //     // formEl.classList.add("was-validated");
    // } else {
    //     inputEmailEl.setCustomValidity("");
    // }

    //formEl.classList.add("was-validated");

    // formEl.classList.add("was-validated");
    // formEl.reportValidity();
    // inputEmailEl.classList.add("was-validated");

    //inputEmailEl.reportValidity();

    let firstName = document.querySelector("#inputFirstName").value;

    let sessions = [];
    for (let a of registerCheckboxes) {
        let [el, session_name] = a;
        if (el.checked)
            sessions.push(session_name);
    }

    // console.log("Sessions:")
    // console.log(sessions);

    //formEl.classList.add("was-validated");

    if (sessions.length < 1) {
        for (let a of registerCheckboxes) {
            let [el, session_name] = a;
            el.setCustomValidity("Selecteer welke sessies je verwacht deel te nemen.");
            //el.classList.add("was-validated");
        }

        //formEl.setCustomValidity("Geen sessies opgegeven");
        //formEl.reportValidity();
        //formEl.classList.add("was-validated");
        //return;
    } else {
        for (let a of registerCheckboxes) {
            let [el, session_name] = a;
            el.setCustomValidity("");
            //el.reportValidity();
            //el.classList.add("was-validated");
        }
    }

    let commentsCookie = document.querySelector("#imputFavoriteCookie").value;
    let commentsGeneric = document.querySelector("#inputComments").value;

    let comments = {};

    if (commentsCookie.trim().length > 0)
        comments["cookie_preference"] = commentsCookie.trim();
    
    if (commentsGeneric.trim().length > 0)
        comments["generic"] = commentsGeneric.trim();

    formEl.classList.add("was-validated");
    formEl.reportValidity();

    if (!formEl.checkValidity()) {
        statusMsg.style.color = "red";
        statusMsg.textContent = "Een of meer velden hebben ongeldige waarden. " +
        "Check voor typfouten en selecteer aan welke sessie je wil deelnemen.";
        return;
    }

    statusMsg.style.color = "darkorange";
    statusMsg.textContent = "Verzenden...";

    let data = {
        "email": email,
        "first_name": firstName,
        "scope": "2022-09-cursus",
        "register_sessions": sessions,
        "comments": comments
    };
    console.log("Data is");
    console.log(data);

    let fallbackInstructionsEl = document.querySelector("#formFallbackInstructions");

    function emphasizeFallbackInstructions() {
        fallbackInstructionsEl.style.fontSize = "1.5rem";
        fallbackInstructionsEl.style.fontWeight = "bold";
        fallbackInstructionsEl.style.color = "red";
    }

    fetch("https://icy3wowlug.execute-api.eu-north-1.amazonaws.com/texnicie/register", {
        mode: 'cors',    
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            'Access-Control-Allow-Origin': "*.amazonaws.com"
        },
        body: JSON.stringify(data)
    }).then(res => res.json())
    .then(msg => {
        console.log("Response:");
        console.log(msg);

        if ("error" in msg) {
            statusMsg.style.color = "red";
            statusMsg.textContent = `Error: ${msg["error"]}`;
            emphasizeFallbackInstructions();
            return;
        }
        if (!("success" in msg)) {
            statusMsg.style.color = "black";
            statusMsg.textContent = `Server antwoordde met ${JSON.stringify(msg, null, 4)}`;
            emphasizeFallbackInstructions();
            return;
        }

        statusMsg.style.color = "green";
        if (msg["confirmation_email"])
            statusMsg.innerHTML = (
                'Verzenden gelukt! Klik op de link die je ontvangt per e-mail om je inschrijving te bevestigen.<br/>' +
                '<span style="color:#333;font-weight:normal;font-size:85%;">' +
                'We blijven je enkel mailtjes sturen als je de link in de e-mail opent. Zo voorkomen we ' +
                'dat iemand je ongewenst op de mailinglijst kan zetten.<br/>' +
                // Deze link voorkomt dat iemand je ongewenst op de mailinglijst kan zetten, ' +
                // 'aangezien we stoppen met mailtjes sturen als het e-mailadres niet wordt bevestigd. ' +
                //"doordat iemand anders je op de mailin"
                 //"Bevestiging is nodig om te voorkomen dat je e-mailadres " +
                //"ongewenst door een ander op de mailinglijst wordt gezet. Lees hier meer: " +
                "Lees hier meer: " +
                '<a href="/waarom-bevestigen">texnicie.nl/waarom-bevestigen</a><br/>' +
                'Uitschrijven voor mails kan altijd door een "Unsubscribe"-link in de e-mails, of door ons een mailtje te sturen.</span>'
                +
                '<br/><br/>Om je privacy te beschermen vertelt dit bericht je niet of er al ' +
                'een bevestigingsmail is gestuurd. Je ontvangt geen tweede.'
            );
        else
            statusMsg.textContent = "Succes!";
    }).catch(e => {
        statusMsg.style.color = "error";
        statusMsg.textContent = `Error bij het verzenden van gegevens: ${e}`;
        emphasizeFallbackInstructions();
    });
}

let lastSubmit = 0;

(() => {
    languageRedirect();

    function disableNonExistentLinks() {
        for (let el of document.querySelectorAll(".check-exists")) {
            let aEl = el.querySelector("a, button");

            if (aEl == null)
                continue;
            let url = aEl.href;

            // Technique based on https://stackoverflow.com/questions/68595209/js-fetch-check-if-file-present-without-downloading-content
            // Answer of https://stackoverflow.com/users/9074788/the-bic-pen
            fetch(url, {method: "HEAD"}).then((res) => {
                if (!res.ok) {
                    // el.innerHTML = "Nog niet beschikbaar";
                    el.innerHTML = (getURLLanguage() == "nl") ? "Nog niet beschikbaar" : "Not yet available";
                    //el.href = "#";
                }
            })
        }
    }

    function onDocumentLoaded() {
        addLanguageControls();
        registerCollapsers();
        disableNonExistentLinks();

        let formEl = document.querySelector("#inschrijfSubmitForm");

        registerCheckboxes = [
            [document.querySelector("#checkSessie1"), "2022-09-cursus-1"],
            [document.querySelector("#checkSessie2"), "2022-09-cursus-2"],
            [document.querySelector("#checkSessie3"), "2022-09-cursus-3"]
        ];
    
        for (let a of registerCheckboxes) {
            let [el, sessionName] = a;
            if (el == null)
                continue;
            el.addEventListener("input", e => {
                for (let b of registerCheckboxes) {
                    b[0].setCustomValidity("");
                }
                formEl.classList.remove("was-validated");
                // console.log("Checkbox input");
                // el.setCustomValidity("");
                // el.classList.remove("was-validated");
            });
        }
        
        let inschrijfSubmit = document.querySelector("#inschrijfSubmit");
        if (inschrijfSubmit != null) {
            inschrijfSubmit.addEventListener("click", e => {
                window.setTimeout(() => {
                    if (lastSubmit >= Date.now() - 2000)
                        return;
                    lastSubmit = Date.now();
                    console.log("Clicked submit button")

                    submitRegister();
                }, 200);
            });

            let inschrijfSubmitForm = document.querySelector("#inschrijfSubmitForm");
            inschrijfSubmitForm.addEventListener("submit", e => {
                e.preventDefault();
                if (lastSubmit >= Date.now() - 800)
                    return;
                lastSubmit = Date.now();
                console.log("Submit form triggered");

                submitRegister();
            });
        }
    }

    function registerCollapsers() {
        for (let el of document.querySelectorAll(".collapse-control")) {
            el.addEventListener("click", e => {
                let targetName = el.getAttribute("data-target");
                let target = document.querySelector(`#${targetName}`);
                if (target == null) {
                    console.warn(`Collapse target ${targetName} not found.`);
                    return;
                }
                let collapse = !target.classList.contains("collapsed");

                if (collapse) {
                    target.classList.add("collapsed");
                    el.textContent = el.getAttribute("data-text-collapsed") ?? "Expand";
                } else {
                    target.classList.remove("collapsed");
                    el.textContent = el.getAttribute("data-text-uncollapsed") ?? "Collapse";
                }
            })
        }

        //"2022-09-cursus-beschrijving"
    }

    function addLanguageControls() {
        let el = document.querySelector("ul.nav.nav-tabs.nav-centered");
        console.log("Top bar:");
        console.log(el);
        if (el != null) {
            let urlLanguage = getURLLanguage();
            console.log(`URL language is ${urlLanguage}`);

            let spacer = document.createElement("li");
            spacer.style.float = "none";
            spacer.style.display = "inline-block";
            spacer.style.width = "30px";
            el.appendChild(spacer);

            let languages = ["nl", "en"];
            for (let lang of languages) {
                let template = document.createElement("template");
                // let fragment = new DocumentFragment();
                template.innerHTML =
                `<li style="float:none;display:inline-block;">
                    <a href="javascript:setLanguage(&quot;${lang}&quot;)">${lang.toUpperCase()}</a>
                </li>`;
                if (lang == urlLanguage)
                    template.content.firstElementChild.classList.add("active");

                console.log(`Appending child`);
                console.log(template.content);
                el.appendChild(template.content);
                console.log(`Top bar now has ${el.children.length} elements children`);
            }
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        onDocumentLoaded();
    });
})();
