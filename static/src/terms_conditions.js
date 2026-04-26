function termsView() {
    const card = document.getElementById("terms");
    card.classList.remove("d-none");
    card.classList.add("d-block");

}

function ToggleAcceptedTerms() {
    const termsAndConditions = document.getElementById("digital_sig");
    console.log("termsAndConditions", termsAndConditions);
    console.log("termsAndConditions checked", termsAndConditions.checked);
    const payNow = document.getElementById("payNowButton");
    if (termsAndConditions.checked) {
        payNow.style.visibility = "visible";
    } else {
        payNow.style.visibility = "hidden";
    }

}

function closeCard() {
    const card = document.getElementById("terms");

    card.classList.remove("d-block");
    card.classList.add("d-none");

}