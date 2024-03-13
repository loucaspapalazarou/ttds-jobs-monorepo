import {computed, ref, watch} from "vue";
import {defineStore} from "pinia";

export const useSuggestStore = defineStore('suggest',
    () => {
        const query = ref('');
        const results = ref(null);
        const get_query = computed(() => query.value);
        const get_results = computed(() => results.value)
        let suggest = (q) => {
            query.value = q
        }

        const currentAbortController = ref(null);

        watch(query, async (newQuery) => {
            // If there's an ongoing fetch request, cancel it before starting a new one
            if (currentAbortController.value) {
                currentAbortController.value.abort();
            }

            results.value = null;

            // Check if the query is not empty
            if (newQuery.trim() === '') {
                results.value = []; // Or any other default state for empty query
                return;
            }

            // Initialize a new AbortController for the new request
            currentAbortController.value = new AbortController();
            const signal = currentAbortController.value.signal;

            // const hostname = window.location.hostname;

            try {
                const response = await fetch(`/api/suggest/?query=${encodeURIComponent(newQuery)}`, {signal});
                if (response.ok) {
                    const data = await response.json();
                    results.value = data;
                }
            } catch (error) {
                if (error.name === 'AbortError') {
                    // Fetch was cancelled, handle it if needed
                    console.log('Fetch aborted');
                }
            }
        })
        // Replace `yourServerApiEndpoint` with the actual endpoint
        return {query, get_query, get_results, suggest}
    }
)