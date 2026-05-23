<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  'file-selected': [file: File]
}>()

const acceptedExtensions = ['.mp3', '.wav', '.flac', '.ogg', '.m4a', '.aac', '.wma', '.aiff']
const acceptedTypes = acceptedExtensions.join(',')

const isDragging = ref(false)
const selectedFile = ref<File | null>(null)
const errorMessage = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

function formatFileSize(size: number): string {
  if (size >= 1024 * 1024) {
    return `${(size / (1024 * 1024)).toFixed(2)} MB`
  }

  return `${(size / 1024).toFixed(1)} KB`
}

function isFileAllowed(file: File): boolean {
  const lowerName = file.name.toLowerCase()
  return acceptedExtensions.some((extension) => lowerName.endsWith(extension))
}

function selectFile(file: File | null): void {
  if (!file) {
    return
  }

  if (!isFileAllowed(file)) {
    errorMessage.value = '請選擇支援的音訊格式（mp3、wav、flac、ogg、m4a、aac、wma、aiff）。'
    return
  }

  errorMessage.value = ''
  selectedFile.value = file
  emit('file-selected', file)
}

function handleInputChange(event: Event): void {
  const target = event.target as HTMLInputElement
  selectFile(target.files?.[0] ?? null)
}

function handleDrop(event: DragEvent): void {
  isDragging.value = false
  selectFile(event.dataTransfer?.files?.[0] ?? null)
}

function openFilePicker(): void {
  fileInput.value?.click()
}
</script>

<template>
  <div class="space-y-3">
    <input
      ref="fileInput"
      class="hidden"
      type="file"
      :accept="acceptedTypes"
      @change="handleInputChange"
    />

    <button
      type="button"
      class="group flex w-full flex-col items-center justify-center rounded-3xl border-2 border-dashed px-6 py-12 text-center transition focus:outline-none focus:ring-2 focus:ring-indigo-400"
      :class="isDragging ? 'border-indigo-400 bg-indigo-500/10' : 'border-white/15 bg-white/5 hover:border-indigo-400/70 hover:bg-white/10'"
      @click="openFilePicker"
      @dragenter.prevent="isDragging = true"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="handleDrop"
    >
      <div class="mb-4 rounded-2xl bg-gray-900/80 p-4 text-3xl shadow-lg shadow-black/20">🎵</div>
      <p class="text-lg font-semibold text-white">拖曳音訊檔案到這裡，或點擊選擇檔案</p>
      <p class="mt-2 max-w-xl text-sm text-gray-400">
        支援 MP3、WAV、FLAC、OGG、M4A、AAC、WMA、AIFF。
      </p>
      <p class="mt-4 text-xs uppercase tracking-[0.3em] text-indigo-300/80">Drop · Browse · Separate</p>
    </button>

    <div v-if="selectedFile" class="rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-left text-sm text-emerald-100">
      <p class="font-medium">已選擇：{{ selectedFile.name }}</p>
      <p class="mt-1 text-emerald-200/80">檔案大小：{{ formatFileSize(selectedFile.size) }}</p>
    </div>

    <p v-if="errorMessage" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
      {{ errorMessage }}
    </p>
  </div>
</template>
