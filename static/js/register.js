document.getElementById('register-form').addEventListener('submit', function(event) {
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const mobile = document.getElementById('mobile').value.trim();
    const password = document.getElementById('password').value.trim();

    if (username === "" || email === "" || mobile === "" || password === "") {
        event.preventDefault();
        alert("Please fill in all fields.");
    } else if (!email.includes("@")) {
        event.preventDefault();
        alert("Enter a valid email address.");
    } else if (mobile.length < 10 || isNaN(mobile)) {
        event.preventDefault();
        alert("Enter a valid mobile number.");
    }
});
