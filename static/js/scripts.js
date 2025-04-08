// Handle Calorie Calculation
document.getElementById('calorieForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Get form inputs
    const age = document.getElementById('age').value;
    const weight = document.getElementById('weight').value;
    const height = document.getElementById('height').value;
    const activity = document.getElementById('activityLevel').value;

    // Input validation
    if (!age || !weight || !height || !activity) {
        alert("Please fill out all fields.");
        return;
    }

    if (isNaN(age)) {
        alert("Age must be a number.");
        return;
    }

    if (isNaN(weight)) {
        alert("Weight must be a number.");
        return;
    }

    if (isNaN(height)) {
        alert("Height must be a number.");
        return;
    }

    // Show loading indicator
    const submitButton = document.querySelector('#calorieForm button[type="submit"]');
    submitButton.disabled = true;
    submitButton.innerText = "Calculating...";

    // Send data to the server
    fetch('/calculate_calories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ age: age, weight: weight, height: height, activity: activity })
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server responded with status ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Display the result
            document.getElementById('calorieResult').innerText = `You need ${data.calories} calories per day.`;
        })
        .catch(error => {
            console.error('Error:', error);
            alert("An error occurred while calculating calories. Please try again.");
        })
        .finally(() => {
            // Reset the button
            submitButton.disabled = false;
            submitButton.innerText = "Calculate";
        });
});