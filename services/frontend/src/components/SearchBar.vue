<script setup>
import {ref, watch} from 'vue'
import router from "@/router/index.js";
import {useRoute} from 'vue-router';
import {useSuggestStore} from "@/stores/suggestionsStore.js";

const route = useRoute()
const query = ref({})

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
};

let search = () => {
    if (query.value != null && query.value !== "") {
        router.push({
            name: 'search',
            params: {query: query.value}
        })
    }
}

watch(query, () => suggest());

let suggest = () => {
    if (query.value != null) {
        suggestStore.suggest(query.value)
    }
}
</script>

<template>
    <div class="grow flex flex-col items-center justify-center text-left">
        <div class="h-12 w-full px-5 md:w-10/12 md:px-0 relative">
            <p class="absolute -top-2/3 md:-top-3/4 text-left text-base md:text-lg pl-1">Search Jobs:</p>
            <input type="text"
                   class="h-full w-full focus:outline-accent-600 rounded-lg border border-slate-300 p-3"
                   v-model="query"
                   @keydown.enter="search"
                   @focus="isInputFocused = true"
                   @blur="onBlur"
            >
            <ul class="border border-t-0 border-slate-300 dark:border-slate-400 bg-white text-black z-50"
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
