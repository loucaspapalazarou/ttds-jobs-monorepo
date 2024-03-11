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
            fetch(`http://${hostname}:5001/jobs/page=${currentPage.value}`)
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
            fetchMore};
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

            watch(query, async () => {
                results.value = null
                const hostname = window.location.hostname;
                fetch(`http://${hostname}:5001/suggest/?query=${encodeURIComponent(query.value)}`)
                    .then(response => response.json())
                    .then(data => results.value = data);
            })
            // Replace `yourServerApiEndpoint` with the actual endpoint
            return {query, get_query, get_results, suggest}
        }
)