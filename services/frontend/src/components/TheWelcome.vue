<script setup>
import SearchBar from "@/components/SearchBar.vue";
import {useSuggestStore} from "@/stores/suggestionsStore.js";

let suggestStore = useSuggestStore();
suggestStore.reset();
</script>

<template>
    <div class="flex grow px-32">
        <search-bar></search-bar>
    </div>
</template>
