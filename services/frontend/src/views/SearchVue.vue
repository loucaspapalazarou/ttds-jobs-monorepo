<script setup>
import {computed} from 'vue';
import {useRoute} from "vue-router";

import SearchBar from "@/components/SearchBar.vue";
import SearchResult from "@/components/SearchResult.vue";
import {useSearchStore} from "@/stores/searchStore.js"

const route = useRoute();

const store = useSearchStore()
const results = computed(() => store.get_results)

store.search(route.params.query)
</script>

<template>
    <div class="flex flex-col gap-3 w-full">
        <div class="min-h-32 pt-12 flex border-b border-slate-300">
            <search-bar></search-bar>
        </div>
        <div class="flex grow justify-center mb-12">
            <ul v-if="results" class="flex flex-col w-10/12 px-3 divide-y-2 divide-slate-200
                        dark:divide-slate-600">
                <li v-for="result in results" :key="result.idx">
                    <a :href="result.link" target="_blank" rel="noopener noreferrer">
                        <search-result
                            :title="result.title"
                            :company="result.company"
                            :description="result.description"
                            :location="result.location"
                        ></search-result>
                    </a>
                </li>
            </ul>
            <ul v-else class="flex flex-col w-10/12 px-3 divide-y-2 divide-slate-200
                        dark:divide-slate-600 animate-pulse">
                <li><search-result placeholder></search-result></li>
                <li><search-result placeholder class="opacity-75"></search-result></li>
                <li><search-result placeholder class="opacity-50"></search-result></li>
            </ul>
        </div>
    </div>
</template>

<style scoped>

</style>