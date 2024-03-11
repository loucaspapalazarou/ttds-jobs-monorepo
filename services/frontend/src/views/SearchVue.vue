<script setup>
import { computed,  onMounted, onUnmounted,ref, watch} from 'vue';
import { useRoute } from "vue-router";

import SearchBar from "@/components/SearchBar.vue";
import SearchResult from "@/components/SearchResult.vue";
import { useSearchStore } from "@/stores/searchStore.js";


const route = useRoute();

const store = useSearchStore();
const results = computed(() => store.get_results);

const downloadResults = () => {
  // Limiting to the first 15 results
  const limitedResults = results.value.slice(0, 15);

  // Convert the results to CSV format
  const csvContent = 
    "JobTitle,Company,Location,JobLink\n" +
    limitedResults.map(result =>
      [result.title, result.company, result.location,result.link].map(value => JSON.stringify(value)).join(',')
    ).join('\n');

  // Create a Blob and download link
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const resulturl = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = resulturl;
  a.download = 'search_results.csv';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(resulturl);
};

const handleScroll = async () => {
  const bottomOfPage = window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
  if (bottomOfPage && !store.isLoading && !store.isAllDataLoaded.value) {
    await store.fetchMore();
  }
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
  //loadMoreData(); // Initial data load
});

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll);
});

watch(() => route.params.query, (newQuery) => {
  if (newQuery) {
    store.search(newQuery);
    console.log(newQuery)
  }
}, { immediate: true });
</script>

<template>
 <div class="flex flex-col gap-3 w-full mt-5">
  <!-- Download button at the top -->
  <div class="flex justify-between mt-4">
    <!-- Home button -->
    <router-link to="/" class="bg-blue-500 text-white px-10 py-2 rounded-md self-end" style="font-size: 1.5rem; margin-left: 10px;" title="Go to HomePage">
      <i class="fas fa-home mr-2"></i> Home
    </router-link>
    <!-- Download and feedback buttons -->
    <div class="flex gap-2">
      <!-- Download button -->
      <button @click="downloadResults" class="bg-blue-500 text-white px-10 py-2 rounded-md" style="font-size: 1.5rem; margin-right: 10px;" title="Download the Top Results">
        Download
      </button>
      <!-- Feedback button -->
      <router-link to="/feedback" class="bg-blue-500 text-white px-10 py-2 rounded-md" style="font-size: 1.5rem; margin-right: 15px;" title="We'd love your feedback">
        Feedback
      </router-link>
    </div>



    
  </div>
    <div class="min-h-32 pt-12 flex border-b border-slate-300">
      <search-bar></search-bar>
    </div>
    <div class="flex grow justify-center mb-12">
      <!-- Your search results display -->
      <ul v-if="results" class="flex flex-col w-10/12 px-3 divide-y-2 divide-slate-200 dark:divide-slate-600">
        <li v-for="result in results" :key="result.idx">
          <a :href="result.link" target="_blank" rel="noopener noreferrer">
            <search-result
              :title="result.title"
              :company="result.company"
              :description="result.description"
              :location="result.location"
            ></search-result>
          </a>
        </li>
      </ul>
      <!-- Loading placeholder -->
      <ul v-else class="flex flex-col w-10/12 px-3 divide-y-2 divide-slate-200 dark:divide-slate-600 animate-pulse">
        <li><search-result placeholder></search-result></li>
        <li><search-result placeholder class="opacity-75"></search-result></li>
        <li><search-result placeholder class="opacity-50"></search-result></li>
      </ul>
    </div>
  </div>
</template>

<style scoped>
.avia-button {
    font-size: 10px; /* adjust as needed */
    border-radius: 50px; /* adjust as needed */
}
</style>