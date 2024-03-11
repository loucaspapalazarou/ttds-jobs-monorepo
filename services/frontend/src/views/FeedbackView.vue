<template>
  <div class="feedback-page">
    <router-link to="/" class="bg-blue-500 text-white px-10 py-2 rounded-md self-end" style="font-size: 1.5rem; margin-left: 10px;" title="Go to HomePage">
      <i class="fas fa-home mr-2"></i> Home
    </router-link>
    <div class="header">
      <h1>Your Feedback</h1>
      
    </div>
   
    <div v-if="!showThankYou" class="content">
      <h2>How likely are you to recommend our service to a friend or colleague?</h2>
      <Feedback :rating="rating" @setRating="setRating" />
      <div class="feedback-section">
        <label for="feedback">What feature can we add to improve? We'd love to hear your suggestions</label>
        <textarea id="feedback" v-model="feedback"></textarea>
      </div>
      <div class="email-section">
        <label for="email">Email (optional)</label>
        <input id="email" type="email" v-model="email" />
      </div>
      <button @click="submitFeedback">SEND FEEDBACK</button>
    </div>
    <div v-if="showThankYou" class="content">
      <div class="thank-you-container">
        <p class="thank-you-message">Thank you for your feedback!</p>
      </div>
    </div>
  </div>
</template>

<script>
import Feedback from "@/components/Feedback.vue";

export default {
  components: {
    Feedback,
  },
  data() {
    return {
      rating: 0,
      feedback: "",
      email: "",
      isSubmitting: false,
      showThankYou: false, // Add a loading state
    };
  },
  methods: {
    setRating(rating) {
      this.rating = rating;
    },
    submitFeedback() {
      if (this.rating === 0) {
        alert("Please provide a rating before submitting feedback.");
        return;
      }
    const currentDate = new Date().toLocaleDateString();
    const feedbackData = {
    rating: this.rating,
    feedback: this.feedback,
    email: this.email,
    date: currentDate,
  };

  console.log("Feedback submitted successfully11de");

  // Set the loading state to true during submission
  this.isSubmitting = true;

  // Send feedback data to the server
  const hostname = window.location.hostname;
  console.log(hostname);
  fetch(`http://${hostname}:5001/submitfeedback`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(feedbackData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Server response not ok");
      }
      return response.json();
    })
    .then((data) => {
      // Handle the submission response
      console.log("Feedback submitted successfully", data);
      // Reset the form and loading state
      this.rating = 0;
      this.feedback = "";
      this.email = "";
      this.showThankYou = true; // Display thank you message
    })
    .catch((error) => {
      // Handle submission error
      console.error("Error submitting feedback", error);
    })
    .finally(() => {
      // Set the loading state to false after submission (regardless of success or failure)
      this.isSubmitting = false;
    });
},
  },
};
</script>


<style scoped>
.feedback-page {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.header {
  width: 100%;
  padding: 20px 0;
  border-bottom: 1px solid #ddd;
  text-align: right;
}

.content {
  width: 100%;
  padding: 20px;
  
}

h1 {
  margin: 0;
  font-size: 50px;
  color: #333;
}

p {
  font-size: 25px;
}

h2 {
  color: #333;
  font-size: 28px;
  margin-bottom: 25px;
}

.feedback-section,
.email-section {
  margin-bottom: 20px;
  
}

label {
  display: block;
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
  font-size: 28px;
}

textarea,
input[type="email"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 5px;
  font-size: 25px;
  margin-top: 15px;
}

button {
  display: block;
  width: 100%;
  padding: 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 25px;
  cursor: pointer;
  margin-top: 50px;
  transition: background-color 0.3s ease;
}

button:hover {
  background-color: #007bff;
}

.thank-you-container {
  text-align: center; 
  max-width: 1000px; 
  margin: 0 auto; 
}

.thank-you-message {
  font-size: 36px; 
  color: #333;
  margin-left: 200px;
  margin-right: 200px;
  margin-top: 100px; }

</style>
