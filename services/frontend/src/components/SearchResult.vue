<script setup>
defineProps({
    title: String,
    company: String,
    description: String,
    url: String,
    location: String,
    placeholder: Boolean
})
</script>

<template>
    <a :ref="url"
       class="flex flex-col p-6 gap-3 group my-4
                hover:bg-slate-50 hover:cursor-pointer
                dark:hover:bg-slate-600 text-accent-600 dark:text-accent-400">
        <p class="text-xl font-extrabold group-hover:underline">
            {{title}}
        </p>
        <p v-if="placeholder" class="bg-accent-100 w-3/4 h-8"></p>
        <p class="italic">{{company}}</p>
        <p v-if="placeholder" class="bg-accent-100 w-2/3 h-5"></p>
        <p class="text-slate-600 dark:text-white line-clamp-2">
            {{description}}
        </p>
        <p v-if="placeholder" class="bg-slate-100 w-full h-12"></p>
        <div v-if="location" class="flex gap-3">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5"
                 stroke="currentColor" class="w-6 h-6">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z"/>
                <path stroke-linecap="round" stroke-linejoin="round"
                      d="M19.5 10.5c0 7.142-7.5 11.25-7.5 11.25S4.5 17.642 4.5 10.5a7.5 7.5 0 1 1 15 0Z"/>
            </svg>
            <p>{{location}}</p>
        </div>
        <p v-if="placeholder" class="bg-sky-100 w-1/4 h-5"></p>
    </a>
</template>

<style scoped>

</style>