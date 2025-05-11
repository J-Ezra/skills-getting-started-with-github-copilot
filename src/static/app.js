document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      // Clear loading message
      activitiesList.innerHTML = "";

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft = details.max_participants - details.participants.length;

        // Add delete button for each participant
        const participantsList = details.participants.map(participant => {
          return `<li>${participant} <button class='delete-btn' data-activity='${name}' data-participant='${participant}'>❌</button></li>`;
        }).join("");

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants">
            <strong>Participants:</strong>
            <ul>${participantsList}</ul>
          </div>
        `;

        activitiesList.appendChild(activityCard);

        // Add option to select dropdown
        const option = document.createElement("option");
        option.value = name;
        option.textContent = name;
        activitySelect.appendChild(option);
      });
    } catch (error) {
      console.error("Error fetching activities:", error);
    }
  }

  // Handle signup form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = activitySelect.value;

    try {
      const response = await fetch(`/activities/${activity}/signup`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        messageDiv.textContent = `Successfully signed up for ${activity}!`;
        messageDiv.classList.remove("hidden");
        fetchActivities(); // Refresh activities list dynamically
      } else {
        const errorData = await response.json();
        messageDiv.textContent = `Error: ${errorData.detail}`;
        messageDiv.classList.remove("hidden");
      }
    } catch (error) {
      console.error("Error signing up:", error);
      messageDiv.textContent = "An error occurred. Please try again later.";
      messageDiv.classList.remove("hidden");
    }
  });

  // Event delegation for delete buttons
  document.addEventListener("click", async (event) => {
    if (event.target.classList.contains("delete-btn")) {
      const activity = event.target.dataset.activity;
      const participant = event.target.dataset.participant;

      try {
        const response = await fetch(`/activities/${encodeURIComponent(activity)}/unregister?email=${encodeURIComponent(participant)}`, {
          method: "DELETE",
        });

        if (response.ok) {
          alert("Participant unregistered successfully.");
          fetchActivities(); // Refresh activities
        } else {
          alert("Failed to unregister participant.");
        }
      } catch (error) {
        console.error("Error unregistering participant:", error);
      }
    }
  });

  // Initialize app
  fetchActivities();
});
