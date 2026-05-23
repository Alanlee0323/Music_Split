<script setup lang="ts">
import axios from 'axios'
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createJob, uploadFile, uploadYoutube } from '../api/client'
import FileDropzone from '../components/FileDropzone.vue'
import ModelSelector from '../components/ModelSelector.vue'
import StemSelector from '../components/StemSelector.vue'

const router = useRouter()

const sourceTab = ref<'file' | 'youtube'>('file')
const selectedFile = ref<File | null>(null)
const youtubeUrl = ref('')
const stems = ref('vocals')
const model = ref('htdemucs_ft')
const isUploading = ref(false)
const isCreatingJob = ref(false)
const errorMessage = ref('')

const canSubmit = computed(() => {
  if (isUploading.value || isCreatingJob.value) {
    return false
  }

  return sourceTab.value === 'file'
    ? selectedFile.value !== null
    : youtubeUrl.value.trim().length > 0
})

const submitLabel = computed(() => {
  if (isUploading.value) {
    return sourceTab.value === 'file' ? '上傳音檔中...' : '處理 YouTube 來源中...'
  }

  if (isCreatingJob.value) {
    return '建立任務中...'
  }

  return '開始音源分離'
})

function selectSourceTab(tab: 'file' | 'youtube'): void {
  sourceTab.value = tab
  errorMessage.value = ''
}

function handleFileSelected(file: File): void {
  selectedFile.value = file
  errorMessage.value = ''
}

async function pasteFromClipboard(): Promise<void> {
  errorMessage.value = ''

  try {
    if (!navigator.clipboard) {
      throw new Error('目前瀏覽器不支援剪貼簿讀取。')
    }

    youtubeUrl.value = (await navigator.clipboard.readText()).trim()
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error, '無法從剪貼簿貼上內容。')
  }
}

async function submitJob(): Promise<void> {
  if (!canSubmit.value) {
    return
  }

  errorMessage.value = ''

  try {
    isUploading.value = true

    const uploadResult = sourceTab.value === 'file'
      ? await uploadFile(selectedFile.value as File)
      : await uploadYoutube(youtubeUrl.value.trim())

    isUploading.value = false
    isCreatingJob.value = true

    await createJob({
      file_id: uploadResult.file_id,
      model: model.value,
      stems: stems.value,
    })

    await router.push('/jobs')
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error, '建立任務失敗，請稍後再試。')
  } finally {
    isUploading.value = false
    isCreatingJob.value = false
  }
}

function resolveErrorMessage(error: unknown, fallback: string): string {
  if (axios.isAxiosError(error)) {
    return String(error.response?.data?.detail ?? error.message ?? fallback)
  }

  if (error instanceof Error) {
    return error.message
  }

  return fallback
}
</script>

<template>
  <section class="grid gap-8 lg:grid-cols-[1.15fr_0.85fr]">
    <div class="space-y-6">
      <div class="rounded-3xl border border-white/10 bg-gradient-to-br from-gray-900 via-gray-900 to-indigo-950/60 p-8 shadow-2xl shadow-black/20">
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-indigo-300/80">Demucs Source Separation</p>
        <h1 class="mt-4 text-4xl font-semibold tracking-tight text-white sm:text-5xl">
          用更直覺的方式處理音源分離
        </h1>
        <p class="mt-4 max-w-2xl text-base leading-7 text-gray-300 sm:text-lg">
          支援本地音檔上傳與 YouTube 音訊下載，一鍵建立 Demucs 分離任務，快速取得人聲、鼓、貝斯或完整 stems。
        </p>

        <div class="mt-8 grid gap-4 sm:grid-cols-3">
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-sm text-gray-400">支援來源</p>
            <p class="mt-2 font-medium text-white">音檔上傳 / YouTube</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-sm text-gray-400">推薦模型</p>
            <p class="mt-2 font-medium text-white">htdemucs_ft</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <p class="text-sm text-gray-400">輸出結果</p>
            <p class="mt-2 font-medium text-white">試聽、下載、管理</p>
          </div>
        </div>
      </div>

      <div class="rounded-3xl border border-white/10 bg-gray-900/80 p-6 shadow-xl shadow-black/20 sm:p-8">
        <div class="flex flex-wrap gap-3">
          <button
            type="button"
            class="rounded-full px-4 py-2 text-sm font-medium transition"
            :class="sourceTab === 'file' ? 'bg-white text-gray-950 shadow' : 'bg-white/5 text-gray-300 hover:bg-white/10 hover:text-white'"
            @click="selectSourceTab('file')"
          >
            上傳檔案
          </button>
          <button
            type="button"
            class="rounded-full px-4 py-2 text-sm font-medium transition"
            :class="sourceTab === 'youtube' ? 'bg-white text-gray-950 shadow' : 'bg-white/5 text-gray-300 hover:bg-white/10 hover:text-white'"
            @click="selectSourceTab('youtube')"
          >
            YouTube 下載
          </button>
        </div>

        <div class="mt-6 space-y-6">
          <FileDropzone v-if="sourceTab === 'file'" @file-selected="handleFileSelected" />

          <div v-else class="rounded-3xl border border-white/10 bg-white/5 p-6">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h2 class="text-lg font-semibold text-white">貼上 YouTube 連結</h2>
                <p class="mt-1 text-sm text-gray-400">支援 youtube.com、youtu.be 與 music.youtube.com 連結。</p>
              </div>
              <button
                type="button"
                class="rounded-xl border border-white/10 bg-white/10 px-4 py-2 text-sm text-gray-200 transition hover:bg-white/15"
                @click="pasteFromClipboard"
              >
                從剪貼簿貼上
              </button>
            </div>

            <label class="mt-5 block text-sm text-gray-300">
              YouTube URL
              <input
                v-model="youtubeUrl"
                type="url"
                placeholder="https://www.youtube.com/watch?v=..."
                class="mt-2 w-full rounded-2xl border border-white/10 bg-gray-950/80 px-4 py-3 text-white outline-none transition placeholder:text-gray-500 focus:border-indigo-400"
              />
            </label>
          </div>

          <StemSelector v-model="stems" />
          <ModelSelector v-model="model" />

          <div v-if="errorMessage" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            {{ errorMessage }}
          </div>

          <div class="flex flex-col gap-3 border-t border-white/10 pt-6 sm:flex-row sm:items-center sm:justify-between">
            <div class="text-sm text-gray-400">
              <p>選擇完成後會先上傳來源，再自動建立 Demucs 任務。</p>
              <p class="mt-1 text-gray-500">建立成功後將自動跳轉到任務列表。</p>
            </div>
            <button
              type="button"
              class="inline-flex items-center justify-center rounded-2xl bg-gradient-to-r from-indigo-500 to-violet-500 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-950/40 transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-50"
              :disabled="!canSubmit"
              @click="submitJob"
            >
              {{ submitLabel }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <aside class="space-y-6">
      <div class="rounded-3xl border border-white/10 bg-gray-900/80 p-6 shadow-xl shadow-black/20">
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-violet-300/80">Workflow</p>
        <ol class="mt-4 space-y-4 text-sm text-gray-300">
          <li class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <span class="font-medium text-white">1. 選擇來源</span>
            <p class="mt-1 text-gray-400">可直接上傳音檔，或讓後端先下載 YouTube 音訊。</p>
          </li>
          <li class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <span class="font-medium text-white">2. 設定分離條件</span>
            <p class="mt-1 text-gray-400">挑選 stems 與模型，建立最符合需求的任務。</p>
          </li>
          <li class="rounded-2xl border border-white/10 bg-white/5 p-4">
            <span class="font-medium text-white">3. 到任務列表追蹤</span>
            <p class="mt-1 text-gray-400">完成後可直接試聽輸出、下載檔案或刪除任務。</p>
          </li>
        </ol>
      </div>

      <div class="rounded-3xl border border-white/10 bg-gradient-to-br from-indigo-500/15 to-violet-500/10 p-6 shadow-xl shadow-black/20">
        <h2 class="text-lg font-semibold text-white">建議設定</h2>
        <p class="mt-3 text-sm leading-6 text-gray-300">
          如果你想要最佳的人聲品質，建議使用 <span class="font-semibold text-white">htdemucs_ft</span> 搭配
          <span class="font-semibold text-white">人聲</span> 模式。
        </p>
        <div class="mt-5 grid gap-3 text-sm text-gray-200">
          <div class="rounded-2xl border border-white/10 bg-black/10 px-4 py-3">
            <p class="font-medium text-white">快速試聽</p>
            <p class="mt-1 text-gray-300">先選單一 stem 可縮短處理時間。</p>
          </div>
          <div class="rounded-2xl border border-white/10 bg-black/10 px-4 py-3">
            <p class="font-medium text-white">完整後製</p>
            <p class="mt-1 text-gray-300">需要多軌時可選擇全部分離，取得完整輸出。</p>
          </div>
        </div>
      </div>
    </aside>
  </section>
</template>
