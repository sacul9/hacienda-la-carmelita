<template>
  <Teleport to="body">
    <Transition enter-active-class="duration-200 ease-out" leave-active-class="duration-150 ease-in">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <!-- Overlay -->
        <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="$emit('update:modelValue', false)" />
        <!-- Modal -->
        <div
          :class="[
            'relative bg-white rounded-2xl shadow-xl w-full overflow-hidden',
            sizeClasses,
          ]"
        >
          <!-- Header -->
          <div v-if="title" class="flex items-center justify-between p-6 border-b border-gray-100">
            <h3 class="text-lg font-semibold font-display text-gray-900">{{ title }}</h3>
            <button
              class="text-gray-400 hover:text-gray-600 transition-colors"
              @click="$emit('update:modelValue', false)"
            >
              <span class="sr-only">Cerrar</span>
              ✕
            </button>
          </div>
          <!-- Body -->
          <div class="p-6">
            <slot />
          </div>
          <!-- Footer -->
          <div v-if="$slots.footer" class="px-6 py-4 bg-gray-50 border-t border-gray-100">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
interface Props {
  modelValue: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md',
})

defineEmits<{ 'update:modelValue': [value: boolean] }>()

const sizeClasses = computed(() => ({
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-2xl',
}[props.size]))
</script>
