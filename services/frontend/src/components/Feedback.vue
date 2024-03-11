<template>
  <div class="rating">
    <span v-for="i in 10" :key="i" @click="setRating(i)">
      <i :class="{ 'fas': i <= rating, 'far': i > rating }">&#9733;</i>
    </span>
  </div>
</template>

<script>
export default {
  props: {
    rating: {
      type: Number,
      default: 0,
    },
  },
  methods: {
    setRating(rating) {
      this.$emit("setRating", rating);
    },
  },
};
</script>

<style scoped>
.rating {
  display: flex;
  justify-content: space-between;
  margin-bottom: 30px;
}

.rating span {
  cursor: pointer;
}

.rating i {
  font-size: 30px;
  color: #ffd700; /* Yellow color for filled stars */
}

.rating .far {
  color: #ccc; /* Grey color for unfilled stars */
}

</style>