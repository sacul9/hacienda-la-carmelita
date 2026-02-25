<template>
  <div
    :class="[
      'bg-white rounded-2xl overflow-hidden',
      shadow ? 'shadow-sm' : '',
      bordered ? 'border border-gray-100' : '',
      hoverable ? 'hover:shadow-md transition-shadow duration-200 cursor-pointer' : '',
      padding ? 'p-6' : '',
    ]"
    v-bind="$attrs"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  shadow?: boolean
  bordered?: boolean
  hoverable?: boolean
  padding?: boolean
}

withDefaults(defineProps<Props>(), {
  shadow: true,
  bordered: true,
  hoverable: false,
  padding: false,
})
</script>
