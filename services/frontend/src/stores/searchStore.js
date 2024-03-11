import {defineStore} from 'pinia'
import {computed, ref, watch} from "vue";

export const useSearchStore = defineStore(
    'search',
    () => {
        const query = ref('');
        const results = ref(null);
        const get_query = computed(() => query.value);
        const get_results = computed(() => results.value)

        let search = (q) => {
            query.value = q
        }

        watch(query, async () => {
            results.value = null
            fetch('http://localhost:5001/search/?query=' + query.value)
                .then(response => response.json())
                .then(data => results.value = data);
        })

        return {query, get_query, get_results, search}
    })


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
                fetch('http://localhost:5001/suggest/?query=' + query.value)
                    .then(response => response.json())
                    .then(data => results.value = data);
            })
            // Replace `yourServerApiEndpoint` with the actual endpoint
            return {query, get_query, get_results, suggest}
        }
)