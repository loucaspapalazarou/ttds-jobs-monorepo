<template>
    <div class="flex justify-center py-5 w-full">
        <div class="flex flex-col w-2/3">
            <div class="flex justify-center w-full">
                <div class="flex w-full justify-end gap-5">
                    <router-link to="/" class="nav-link" title="Go to HomePage">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                             stroke="currentColor" class="w-5 h-5 mr-1.5">
                            <path stroke-linecap="round" stroke-linejoin="round"
                                  d="M8.25 21v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21m0 0h4.5V3.545M12.75 21h7.5V10.75M2.25 21h1.5m18 0h-18M2.25 9l4.5-1.636M18.75 3l-1.5.545m0 6.205 3 1m1.5.5-1.5-.5M6.75 7.364V3h-3v18m3-13.636 10.5-3.819"/>
                        </svg>
                        Home
                    </router-link>
                </div>
            </div>
            <h1 class="text-4xl my-6">Your Feedback</h1>
            <div v-if="!showThankYou" class="flex flex-col gap-3">
                <h2 class="pb-3">How likely are you to recommend our service to a friend or colleague?</h2>
                <Feedback :rating="rating" @setRating="setRating"/>
                <label for="feedback" class="mt-4">Please share your opinion with us and which features can we add to
                    improve. We'd
                    love to hear your suggestions.</label>
                <textarea id="feedback" v-model="feedback" class="text-black p-2"></textarea>
                <!--                <label for="email">Email (optional)</label>-->
                <!--                <input id="email" type="email" v-model="email"/>-->
                <div class="flex justify-end mt-6">
                    <button @click="submitFeedback"
                            class="p-4 bg-accent-300 text-black dark:bg-accent-600 dark:text-white">Submit
                    </button>
                </div>
            </div>
            <div v-if="showThankYou">
                <div class="flex p-24 justify-center">
                    <p class="font-bold text-2xl">Thank you for your feedback!</p>
                </div>
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
  fetch(`http://${hostname}:5001/submit_feedback`, {
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
.nav-link {
    @apply flex text-slate-400 dark:text-slate-300 hover:underline
}


</style>
