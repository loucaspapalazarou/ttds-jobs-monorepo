import {defineStore} from 'pinia'
import {computed, ref} from "vue";

export const useSearchStore = defineStore(
    'search',
    () => {
        const query = ref('');
        const results = ref([]);
        const page = ref(1);
        const isLoading = ref(false);
        const fetchedAllResults = ref(false);

        const get_query = computed(() => query.value);
        const get_results = computed(() => results.value ? results.value.results : null);
        const get_total_results = computed(() => results.value ? results.value.total_results : null)
        const get_loading_state = computed(( () => isLoading.value));
        const get_finished = computed(() => fetchedAllResults.value);


        let search = (q) => {
            query.value = q;
            page.value = 1; // Reset to the first page
            results.value = null; // Clear previous results
            isLoading.value = true;
            fetchedAllResults.value = false;

            // const hostname = window.location.hostname;
            // fetch(`http://${hostname}:5001/search/?query=${encodeURIComponent(query.value)}`)

            fetch(`/api/search/?query=${encodeURIComponent(query.value)}&page=${encodeURIComponent(page.value)}`)
                .then((response) => response.json())
                .then(data => {
                    if (data.data.results.length === 0) {
                        fetchedAllResults.value = true;
                    } else {
                        results.value = data.data;
                    }
                }).finally(() => isLoading.value = false);
        };

        const fetchMore = () => {
            if (isLoading.value || fetchedAllResults.value) return;

            isLoading.value = true;
            page.value++; // Increment the page for pagination in the jobs endpoint

            // const hostname = window.location.hostname;
            fetch(`/api/search/?query=${encodeURIComponent(query.value)}&page=${encodeURIComponent(page.value)}`)
                .then(response => response.json())
                .then(data => {
                        if (data.data.results.length === 0) {
                            fetchedAllResults.value = true;
                        } else {
                            results.value.results = [...results.value.results, ...data.data.results]; // Append new results
                        }
                    }
                ).finally(() => isLoading.value = false);
        }

        return {
            query,
            search,
            fetchMore,
            get_query,
            get_results,
            get_total_results,
            get_loading_state,
            get_finished
        };
    });
