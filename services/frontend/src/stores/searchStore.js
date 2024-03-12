import {defineStore} from 'pinia'
import {computed, ref, watch} from "vue";

export const useSearchStore = defineStore(
    'search',
    () => {
        const query = ref('');
        const results = ref([]);
        const get_query = computed(() => query.value);
        const currentPage = ref(0);
        const isLoading = ref(false);
        const isAllDataLoaded = ref(false);
        const get_results = computed(() => results.value);

        const search = (q) => {
            query.value = q;
            currentPage.value = 1; // Reset to the first page
            results.value = []; // Clear previous results
            isLoading.value = true;
            isAllDataLoaded.value = false;
            results.value = [];
            const hostname = window.location.hostname;
            fetch(`http://${hostname}:5001/search/?query=${encodeURIComponent(query.value)}`)
              .then((response) => response.json())
              .then(data => {
                if (data.length === 0) {
                    isAllDataLoaded.value = true;
                } else {
                    results.value = data;
                }
            }).finally(() => isLoading.value = false);
          };
          const fetchMore = () => {
            if (isLoading.value || isAllDataLoaded.value) return;
            
            isLoading.value = true;
            currentPage.value++; // Increment the page for pagination in the jobs endpoint
    
            const hostname = window.location.hostname;
            fetch(`http://${hostname}:5001/jobs/?page=${currentPage.value}`)
                .then(response => response.json())
                .then(data => {
                    if (data.length === 0) {
                        isAllDataLoaded.value = true;
                    } else {
                        results.value = [...results.value, ...data]; // Append new results
                    }
                }
                ).finally(() => isLoading.value = false);
          }

        return {query,
            results: computed(() => results.value),
            isLoading: computed(() => isLoading.value),
            isAllDataLoaded: computed(() => isAllDataLoaded.value),
            search,
            fetchMore,
            get_query,
            get_results};
});




export const useSuggestStore = defineStore( 'suggest' ,
        ()=> {
            const query = ref('');
            const results = ref(null);
            const get_query = computed(() => query.value);
            const get_results = computed(() => results.value)    
            let  suggest = (q)=> { 
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
            
                const hostname = window.location.hostname;
            
                try {
                    const response = await fetch(`http://${hostname}:5001/suggest/?query=${encodeURIComponent(newQuery)}`, { signal });
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