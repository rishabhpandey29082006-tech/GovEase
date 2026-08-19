document.addEventListener("DOMContentLoaded", () => {

    const loginForm = document.getElementById("loginForm");

    if (!loginForm) return;

    loginForm.addEventListener("submit", (event) => {

        event.preventDefault();

        const name = document.getElementById("userName").value.trim();
        const password = document.getElementById("userPassword").value;

        if (!name || !password) {
            alert("Please enter your name and password.");
            return;
        }

        // Save user information for the next pages
        localStorage.setItem("govEaseName", name);
        localStorage.setItem("govEasePassword", password);

        // Go to Page 2
        window.location.href = "details.html";
    });

});