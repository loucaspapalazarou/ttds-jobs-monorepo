<script setup>
import {ref, watch} from 'vue'
import router from "@/router/index.js";
import {useRoute} from 'vue-router';
import {useSearchStore} from "@/stores/searchStore.js";
import {useSuggestStore} from "@/stores/suggestionsStore.js";

const route = useRoute()
const query = ref({})

const store = useSearchStore()
const suggestStore = useSuggestStore()

query.value = route.params.query ?? ''

const isInputFocused = ref(false) // Add this line
const isMouseOverSuggestions = ref(false);
const onBlur = () => {
    if (!isMouseOverSuggestions.value) {
        isInputFocused.value = false;
    }
};

const selectSuggestion = (suggestion) => {
    query.value = suggestion;
    search();
    // Optionally, you might want to clear the suggestions after selection or take other actions
    //suggestStore.results.value = []; // Clear suggestions if you store them in `results`
};

let search = () => {
    if (query.value != null && query.value !== "") {
        router.push({
            name: 'search',
            params: {query: query.value}
        })
        store.search(query.value)
    }
}

watch(query, () => {
    // Fetch new suggestions only if the query actually changes to a non-empty value
    suggest();
});

let suggest = () => {
    if (query.value != null) {
        suggestStore.suggest(query.value)
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
                   @focus="isInputFocused = true"
                   @blur="onBlur"
            >
            <ul class="border border-t-0 border-slate-300 dark:border-slate-400 bg-white text-black"
                v-if="isInputFocused && suggestStore.get_results"
                @mouseenter="isMouseOverSuggestions = true"
                @mouseleave="isMouseOverSuggestions = false">
                <li v-for="(suggestion, index) in suggestStore.get_results" :key="index"
                    class="hover:bg-slate-200 px-2 cursor-pointer" @click="selectSuggestion(suggestion)">
                    {{suggestion}}
                </li>
            </ul>
        </div>
    </div>
</template>


<style scoped></style>