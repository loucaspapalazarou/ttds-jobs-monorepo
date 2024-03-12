import {defineStore} from "pinia";
import {computed, ref, watch} from "vue";

export const useSuggestStore = defineStore('suggestion',
    () => {
        const query = ref('');
        const results = ref(null);
        const get_query = computed(() => query.value);
        const get_results = computed(() => results.value)
        let suggest = (q) => {
            query.value = q
        }

        watch(query, async () => {
            results.value = null
            // const hostname = window.location.hostname;
            // fetch(`http://${hostname}:5001/suggest/?query=${encodeURIComponent(query.value)}`)
            fetch(`api/suggest/?query=${encodeURIComponent(query.value)}`)
                .then(response => response.json())
                .then(data => results.value = data);
        })
        // Replace `yourServerApiEndpoint` with the actual endpoint
        return {query, get_query, get_results, suggest}
    }
)