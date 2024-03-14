<script setup>
import {computed, onMounted, onUnmounted, watch} from 'vue';
import {useRoute} from "vue-router";

import SearchBar from "@/components/SearchBar.vue";
import SearchResult from "@/components/SearchResult.vue";
import {useSearchStore} from "@/stores/searchStore.js";


const route = useRoute();

const store = useSearchStore();
const results = computed(() => store.get_results);
const total_results = computed(() => store.get_total_results);
const error = computed(() => store.get_error);

const downloadResults = () => {
    // Limiting to the first 15 results
    const limitedResults = results.value;

    // Convert the results to CSV format
    const csvContent =
        "JobTitle,Company,Location,JobLink\n" +
        limitedResults.map(result =>
            [result.title, result.company, result.location, result.link].map(value => JSON.stringify(value)).join(',')
        ).join('\n');

    // Create a Blob and download link
    const blob = new Blob([csvContent], {type: 'text/csv'});
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

    if (bottomOfPage && !store.get_loading_state && !store.get_finished) {
        await store.fetchMore();
    }
};

onMounted(() => {
    window.addEventListener('scroll', handleScroll);
});

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll);
});

watch(() => route.params.query, (newQuery) => {
    if (newQuery) {
        store.search(newQuery);
    }
}, {immediate: true});
</script>

<template>
    <div class="flex flex-col w-full max-w-full my-3">
        <!-- Download button at the top -->
        <div class="flex justify-center w-full">
            <div class="flex w-full justify-center items-center px-3 py-3 md:w-10/12 md:justify-end md:px-0 md:pb-3 md:gap-5">
                <router-link to="/" class="nav-link" title="Go to HomePage">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                         stroke="currentColor" class="w-5 h-5 mr-1.5">
                        <path stroke-linecap="round" stroke-linejoin="round"
                              d="M8.25 21v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21m0 0h4.5V3.545M12.75 21h7.5V10.75M2.25 21h1.5m18 0h-18M2.25 9l4.5-1.636M18.75 3l-1.5.545m0 6.205 3 1m1.5.5-1.5-.5M6.75 7.364V3h-3v18m3-13.636 10.5-3.819"/>
                    </svg>
                    Home
                </router-link>
                <button @click="downloadResults" class="nav-link" title="Download the Top Results">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                         stroke="currentColor" class="w-5 h-5 mr-1.5">
                        <path stroke-linecap="round" stroke-linejoin="round"
                              d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3"/>
                    </svg>
                    Download
                </button>
                <router-link to="/feedback" class="nav-link" title="We'd love your feedback">
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                         stroke="currentColor" class="w-5 h-5 mr-1.5">
                        <path stroke-linecap="round" stroke-linejoin="round"
                              d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 0 1 .865-.501 48.172 48.172 0 0 0 3.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0 0 12 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018Z"/>
                    </svg>
                    Feedback
                </router-link>
            </div>
        </div>
        <div class="pt-2 pb-5 flex border-b border-slate-100 dark:border-slate-600 w-full mt-7">
            <search-bar></search-bar>
        </div>
        <div v-if="results" class="flex justify-center w-full">
            <div class="flex md:w-10/12 pt-3 md:pb-3 px-7 md:px-2 justify-end text-sm w-full">
                <p class="italic text-slate-400 dark:text-slate-400">Found {{total_results}} results</p>
            </div>
        </div>
        <div v-if="error" class="flex w-full py-5 justify-center items-center">
            <div class="flex flex-col w-full max-w-full px-6 md:px-2 md:w-10/12 md:gap-3 md:max-w-10/12 text-start text-slate-600 dark:text-slate-400">
                <p v-if="error.status === 404">
                    {{error.message}}
                    <i class="text-accent-600 dark:text-accent-400">{{error.query}}</i>
                </p>
                <p v-else>
                    {{error.message}}
                    <i class="text-accent-600 dark:text-accent-400">{{error.query}}</i>
                </p>
            </div>
        </div>
        <div class="flex grow justify-center mb-12 w-full max-w-full">
            <!-- Your search results display -->
            <ul class="flex flex-col w-full max-w-full md:w-10/12 md:gap-3 md:max-w-10/12">
                <li v-for="result in results" :key="result.id">
                    <a :href="result.link" target="_blank" rel="noopener noreferrer">
                        <search-result
                            :title="result.title"
                            :company="result.company"
                            :description="result.description"
                            :location="result.location"
                        ></search-result>
                    </a>
                </li>
                <!-- Loading placeholder -->
                <li v-if="store.get_loading_state">
                    <search-result placeholder class="animate-pulse opacity-80"></search-result>
                </li>
                <li v-if="store.get_loading_state">
                    <search-result placeholder class="animate-pulse opacity-60"></search-result>
                </li>
                <li v-if="store.get_loading_state">
                    <search-result placeholder class="animate-pulse opacity-40"></search-result>
                </li>
            </ul>
        </div>
    </div>
</template>

<style scoped>
.nav-link {
    @apply flex flex-auto md:flex-none text-slate-400 dark:text-slate-300 hover:underline justify-center items-center
}
</style>