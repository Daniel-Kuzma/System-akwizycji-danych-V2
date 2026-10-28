<template>
  <div class="mb-4">
    <label v-if="label" class="block text-sm font-medium text-gray-700 dark:text-custom-light mb-1 transition-colors">
      {{ label }}
    </label>
    <input
      :type="type"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      class="block w-full border border-gray-300 dark:border-custom-border rounded-md p-2 bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light focus:ring-blue-500 focus:border-blue-500 transition-colors"
      v-bind="$attrs"
    >
    <span v-if="error" class="text-red-500 text-xs mt-1 block">{{ error }}</span>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  error: {
    type: String,
    default: ''
  }
})
defineEmits(['update:modelValue'])
</script>