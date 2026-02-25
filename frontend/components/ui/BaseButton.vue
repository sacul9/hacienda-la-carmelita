<template>
  <component
    :is="to ? NuxtLink : 'button'"
    :to="to"
    :type="!to ? type : undefined"
    :disabled="disabled || loading"
    :class="[variantClasses, sizeClasses, 'transition-all duration-200 font-medium rounded-lg inline-flex items-center justify-center gap-2 focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed']"
    v-bind="$attrs"
  >
    <span v-if="loading" class="animate-spin h-4 w-4 border-2 border-current border-t-transparent rounded-full" />
    <slot />
  </component>
</template>

<script setup lang="ts">
import { NuxtLink } from '#components'

interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  type?: 'button' | 'submit' | 'reset'
  to?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  loading: false,
  disabled: false,
  type: 'button',
})

const variantClasses = computed(() => ({
  primary: 'bg-tierra-800 hover:bg-tierra-700 text-white focus-visible:ring-tierra-500',
  secondary: 'bg-dorado-500 hover:bg-dorado-600 text-white focus-visible:ring-dorado-400',
  outline: 'border-2 border-tierra-800 text-tierra-800 hover:bg-tierra-800 hover:text-white focus-visible:ring-tierra-500',
  ghost: 'text-tierra-800 hover:bg-tierra-50 focus-visible:ring-tierra-500',
  danger: 'bg-red-600 hover:bg-red-700 text-white focus-visible:ring-red-500',
}[props.variant]))

const sizeClasses = computed(() => ({
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-6 py-3 text-sm',
  lg: 'px-8 py-4 text-base',
}[props.size]))
</script>
