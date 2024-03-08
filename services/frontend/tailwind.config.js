/** @type {import('tailwindcss').Config} */

const colors = require('tailwindcss/colors')

export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx,vue}",
    ],
    theme: {
        extend: {
            colors: {
                accent: colors.sky
            }
        },
    },
    plugins: [],
}

