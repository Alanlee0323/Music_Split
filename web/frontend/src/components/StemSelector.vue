<script setup lang="ts">
const props = defineProps<{
  modelValue: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const stemOptions = [
  {
    value: 'vocals',
    label: '人聲',
    description: '保留主唱與和聲軌道，適合做 Acapella。',
    icon: '🎤',
  },
  {
    value: 'drums',
    label: '鼓',
    description: '抽出鼓組節奏，方便重編與練習。',
    icon: '🥁',
  },
  {
    value: 'bass',
    label: '貝斯',
    description: '保留低頻律動線條，適合做分析與採樣。',
    icon: '🎸',
  },
  {
    value: 'all',
    label: '全部分離',
    description: '輸出完整 stems，包含 vocals、drums、bass 與其他樂器。',
    icon: '✨',
  },
]
</script>

<template>
  <div class="space-y-3">
    <div class="flex items-center justify-between">
      <h3 class="text-sm font-semibold text-white">分離目標</h3>
      <span class="text-xs text-gray-400">選擇你要保留的聲部</span>
    </div>

    <div class="grid gap-3 md:grid-cols-2">
      <button
        v-for="option in stemOptions"
        :key="option.value"
        type="button"
        class="rounded-2xl border p-4 text-left transition"
        :class="props.modelValue === option.value ? 'border-indigo-400 bg-indigo-500/15 shadow-lg shadow-indigo-950/30' : 'border-white/10 bg-white/5 hover:border-white/20 hover:bg-white/10'"
        @click="emit('update:modelValue', option.value)"
      >
        <div class="flex items-start justify-between gap-4">
          <div>
            <div class="flex items-center gap-2">
              <span class="text-xl">{{ option.icon }}</span>
              <span class="font-medium text-white">{{ option.label }}</span>
            </div>
            <p class="mt-2 text-sm text-gray-400">{{ option.description }}</p>
          </div>
          <span
            class="mt-1 inline-flex h-5 w-5 shrink-0 items-center justify-center rounded-full border text-[10px]"
            :class="props.modelValue === option.value ? 'border-indigo-300 bg-indigo-400 text-gray-950' : 'border-white/20 text-transparent'"
          >
            ✓
          </span>
        </div>
      </button>
    </div>
  </div>
</template>
