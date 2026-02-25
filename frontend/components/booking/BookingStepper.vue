<template>
  <div class="hidden sm:flex items-center gap-1">
    <div
      v-for="(step, index) in steps"
      :key="index"
      class="flex items-center"
    >
      <div
        :class="[
          'flex items-center justify-center w-8 h-8 rounded-full text-xs font-semibold transition-colors',
          index + 1 < currentStep ? 'bg-tierra-800 text-white' :
          index + 1 === currentStep ? 'bg-tierra-800 text-white ring-4 ring-tierra-100' :
          'bg-gray-200 text-gray-500'
        ]"
      >
        <span v-if="index + 1 < currentStep">✓</span>
        <span v-else>{{ index + 1 }}</span>
      </div>
      <span
        :class="[
          'ml-1.5 text-xs font-medium hidden lg:block',
          index + 1 === currentStep ? 'text-tierra-800' : 'text-gray-400'
        ]"
      >
        {{ step }}
      </span>
      <div v-if="index < steps.length - 1" class="w-8 h-px bg-gray-200 mx-2" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentStep: number
}

defineProps<Props>()

const steps = ['Fechas', 'Experiencias', 'Datos', 'Verificar', 'Pago', 'Confirmación']
</script>
