import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios';

import App from './App.vue'
import router from './router'

const app = createApp(App)

axios.defaults.withCredentials = true;
axios.defaults.baseURL = 'http://localhost:5001/';  // the FastAPI backend


app.use(createPinia())
app.use(router)

app.mount('#app')
