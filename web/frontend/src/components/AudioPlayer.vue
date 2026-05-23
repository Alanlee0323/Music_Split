<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'

const props = defineProps<{
  src: string
  label: string
}>()

const audioRef = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)
const currentTime = ref(0)
const duration = ref(0)

function formatTime(time: number): string {
  if (!Number.isFinite(time) || time <= 0) {
    return '0:00'
  }

  const minutes = Math.floor(time / 60)
  const seconds = Math.floor(time % 60)
  return `${minutes}:${seconds.toString().padStart(2, '0')}`
}

const currentTimeText = computed(() => formatTime(currentTime.value))
const durationText = computed(() => formatTime(duration.value))
const progress = computed(() => (duration.value > 0 ? currentTime.value : 0))

async function togglePlayback(): Promise<void> {
  const audio = audioRef.value

  if (!audio) {
    return
  }

  if (audio.paused) {
    await audio.play()
    isPlaying.value = true
    return
  }

  audio.pause()
  isPlaying.value = false
}

function updateMetadata(): void {
  const audio = audioRef.value
  duration.value = audio?.duration ?? 0
}

function updateTime(): void {
  const audio = audioRef.value
  currentTime.value = audio?.currentTime ?? 0
}

function seek(event: Event): void {
  const audio = audioRef.value
  const value = Number((event.target as HTMLInputElement).value)

  if (!audio || !Number.isFinite(value)) {
    return
  }

  audio.currentTime = value
  currentTime.value = value
}

function handleEnded(): void {
  isPlaying.value = false
  currentTime.value = 0
}

watch(
  () => props.src,
  () => {
    const audio = audioRef.value

    if (!audio) {
      return
    }

    audio.pause()
    audio.load()
    isPlaying.value = false
    currentTime.value = 0
    duration.value = 0
  },
)

onBeforeUnmount(() => {
  audioRef.value?.pause()
})
</script>

<template>
  <div class="rounded-2xl border border-white/10 bg-gray-950/60 p-4 shadow-lg shadow-black/20">
    <audio
      ref="audioRef"
      :src="src"
      preload="metadata"
      class="hidden"
      @loadedmetadata="updateMetadata"
      @timeupdate="updateTime"
      @ended="handleEnded"
    />

    <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
      <div class="min-w-0 flex-1">
        <div class="mb-3 flex items-center justify-between gap-4">
          <p class="truncate font-medium text-white">{{ label }}</p>
          <div class="flex items-center gap-2 text-xs text-gray-400">
            <span>{{ currentTimeText }}</span>
            <span>/</span>
            <span>{{ durationText }}</span>
          </div>
        </div>

        <div class="flex items-center gap-3">
          <button
            type="button"
            class="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-indigo-500 text-white shadow-lg shadow-indigo-950/50 transition hover:bg-indigo-400"
            @click="togglePlayback"
          >
            {{ isPlaying ? '❚❚' : '▶' }}
          </button>

          <input
            class="h-2 w-full cursor-pointer accent-indigo-500"
            type="range"
            min="0"
            :max="duration || 0"
            :value="progress"
            @input="seek"
          />
        </div>
      </div>

      <a
        :href="src"
        :download="label"
        class="inline-flex items-center justify-center rounded-xl border border-indigo-400/30 bg-indigo-500/15 px-4 py-2 text-sm font-medium text-indigo-100 transition hover:bg-indigo-500/25"
      >
        下載音檔
      </a>
    </div>
  </div>
</template>
