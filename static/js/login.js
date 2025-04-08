document.getElementById('login-form').addEventListener('submit', function(event) {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value.trim();

    if (username === "" || password === "") {
        event.preventDefault();
        alert("Please fill in all fields.");
    }
});
