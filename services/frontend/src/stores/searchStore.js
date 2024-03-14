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
        const error = ref({});

        const get_query = computed(() => query.value);
        const get_results = computed(() => results.value ? results.value.results : null);
        const get_total_results = computed(() => results.value ? results.value.total_results : null)
        const get_loading_state = computed((() => isLoading.value));
        const get_finished = computed(() => fetchedAllResults.value);
        const get_error = computed(() => error.value);


        let fetch_results = (process_func) => {
            fetch(`/api/search/?query=${encodeURIComponent(query.value)}&page=${encodeURIComponent(page.value)}`)
                .then((response) =>
                    !response.ok
                        ? Promise.reject(response)
                        : Promise.resolve(response.json())
                )
                .then(process_func)
                .catch(handle_errors)
                .finally(() => isLoading.value = false)
        }


        let handle_errors = (response) => {
            error.value = {
                status: response.status,
                message: 'Sorry, something happened when trying to search for the query',
                query: query.value
            }
            switch (response.status) {
                case 404:
                    error.value.message = `Sorry, no results were found for the query`
                    break;
                default:
                    break;
            }
        }


        let search = (q) => {
            query.value = q;
            page.value = 1; // Reset to the first page
            results.value = null; // Clear previous results
            isLoading.value = true;
            fetchedAllResults.value = false;
            error.value = null;

            fetch_results(data => {
                data.data.results.length === 0
                    ? fetchedAllResults.value = true
                    : results.value = data.data;
            })
        };


        let fetchMore = () => {
            if (isLoading.value || fetchedAllResults.value) return;

            isLoading.value = true;
            page.value++; // Increment the page for pagination in the jobs endpoint

            fetch_results(data => {
                data.data.results.length === 0
                    ? fetchedAllResults.value = true
                    : results.value.results = [...results.value.results, ...data.data.results]
            })
        }


        return {
            query,
            search,
            fetchMore,
            get_query,
            get_results,
            get_total_results,
            get_loading_state,
            get_finished,
            get_error
        };
    });
