<template>
  <button
    :disabled="isLoading || disabled"
    class="w-full bg-blue-600 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50 transition-colors flex justify-center items-center"
    v-bind="$attrs"
  >
    <span v-if="isLoading">Ładowanie...</span>
    <slot v-else></slot>
  </button>
</template>

<script setup>
defineProps({
  isLoading: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})
</script>