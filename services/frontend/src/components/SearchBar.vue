<script setup>
// import {ref} from 'vue'
// import router from "@/router/index.js";
// import {useRoute} from 'vue-router';
// import {useSearchStore} from "@/stores/searchStore.js";
// import {useSuggestStore} from "@/stores/suggestionsStore.js";
//
// const route = useRoute()
// const query = ref({})
//
// // const suggestions = ref([]);
//
// const store = useSearchStore()
// const suggestStore = useSuggestStore()
//
// query.value = route.params.query ?? ''
//
// const isInputFocused = ref(false) // Add this line
//
//
// let selectSuggestion = (suggestion) => {
//     query.value = suggestion;
//     search();
//     // Optionally, you might want to clear the suggestions after selection or take other actions
//     //suggestStore.results.value = []; // Clear suggestions if you store them in `results`
// };
//
// let search = () => {
//     if (query.value != null && query.value !== "") {
//         router.push({
//             name: 'search',
//             params: {query: query.value}
//         })
//         store.search(query.value)
//     }
// }
//
// let suggest = () => {
//     if (query.value != null && query.value !== "") {
//         suggestStore.suggest(query.value)
//     }
// }

import {ref} from 'vue'
import router from "@/router/index.js";
import {useRoute} from 'vue-router';
import {useSearchStore} from "@/stores/searchStore.js";

const route = useRoute()
const query = ref({})

const store = useSearchStore()

query.value = route.params.query ?? ''

let search = () => {
    if (query.value != null && query.value !== "") {
        router.push({
            name: 'search',
            params: {query: query.value}
        })
        store.search(query.value)
    }
}

</script>

<template>
    <div class="grow flex flex-col items-center justify-center text-left pb-14">
        <div class="h-12 w-10/12 relative mt-10">
            <p class="absolute -top-3/4 text-left text-lg">Search Jobs:</p>
            <input type="text"
                   class="h-full w-full focus:outline-accent-600 rounded-lg border border-slate-300 p-3"
                   v-model="query"
                   @keydown.enter="search"
                   @input="suggest"
                   @focus="isInputFocused = true"
                   @blur="isInputFocused = false"
            >
<!--            <ul class="" v-if="isInputFocused">-->
<!--                <li v-for="(suggestion, index) in suggestStore.get_results" :key="index"-->
<!--                    class="rounded-lg border w-full h-min-8 p-3 hover:bg-slate-50 dark:hover:bg-slate-600"-->
<!--                    @click="selectSuggestion(suggestion)">-->
<!--                    {{suggestion}}-->
<!--                </li>-->
<!--            </ul>-->
        </div>
    </div>
</template>


<style scoped></style>