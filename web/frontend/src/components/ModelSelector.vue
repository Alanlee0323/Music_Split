<script setup lang="ts">
const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const modelOptions = [
  {
    value: 'htdemucs_ft',
    label: 'htdemucs_ft',
    description: '推薦選項，音質與穩定度最佳。',
    badge: '推薦',
  },
  {
    value: 'htdemucs',
    label: 'htdemucs',
    description: '標準 Hybrid Transformer 模型。',
  },
  {
    value: 'htdemucs_6s',
    label: 'htdemucs_6s',
    description: '6 stems 輸出版本，適合更細緻分離。',
  },
  {
    value: 'hdemucs_mmi',
    label: 'hdemucs_mmi',
    description: '較舊但仍實用，適合相容性需求。',
  },
]
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-white">模型選擇</h3>
      <span class="text-xs text-gray-400">依需求平衡品質與速度</span>
    </div>

    <div class="grid gap-3 md:grid-cols-2">
      <button
        v-for="option in modelOptions"
        :key="option.value"
        type="button"
        class="rounded-2xl border p-4 text-left transition"
        :class="props.modelValue === option.value ? 'border-violet-400 bg-violet-500/15 shadow-lg shadow-violet-950/30' : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'"
        @click="emit('update:modelValue', option.value)"
      >
        <div class="flex items-center justify-between gap-3">
          <p class="font-medium text-white">{{ option.label }}</p>
          <span
            v-if="option.badge"
            class="rounded-full border border-violet-300/40 bg-violet-400/15 px-2 py-1 text-[11px] font-semibold text-violet-100"
          >
            {{ option.badge }}
          </span>
        </div>
        <p class="mt-2 text-sm text-gray-400">{{ option.description }}</p>
      </button>
    </div>
  </div>
</template>
