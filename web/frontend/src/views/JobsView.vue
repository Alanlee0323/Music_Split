<script setup lang="ts">
import axios from 'axios'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { deleteJob, getDownloadUrl, listJobs } from '../api/client'
import AudioPlayer from '../components/AudioPlayer.vue'
import type { Job } from '../types'

const jobs = ref<Job[]>([])
const isLoading = ref(true)
const isDeletingId = ref<string | null>(null)
const errorMessage = ref('')

const statusMeta: Record<Job['status'], { label: string; className: string }> = {
  pending: {
    label: '等待中',
    className: 'border-gray-500/30 bg-gray-500/15 text-gray-200',
  },
  downloading: {
    label: '下載中',
    className: 'border-blue-500/30 bg-blue-500/15 text-blue-200',
  },
  processing: {
    label: '處理中',
    className: 'border-amber-500/30 bg-amber-500/15 text-amber-200',
  },
  completed: {
    label: '已完成',
    className: 'border-emerald-500/30 bg-emerald-500/15 text-emerald-200',
  },
  failed: {
    label: '失敗',
    className: 'border-red-500/30 bg-red-500/15 text-red-200',
  },
}

const stemLabels: Record<string, string> = {
  vocals: '人聲',
  drums: '鼓',
  bass: '貝斯',
  all: '全部分離',
  no_vocals: '伴奏',
  other: '其他樂器',
}

const sortedJobs = computed(() =>
  [...jobs.value].sort((left, right) => new Date(right.created_at).getTime() - new Date(left.created_at).getTime()),
)

const hasActiveJobs = computed(() =>
  jobs.value.some((job) => ['pending', 'downloading', 'processing'].includes(job.status)),
)

let pollTimer: number | null = null

function formatDate(value: string | null): string {
  if (!value) {
    return '—'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function formatStems(stem: string): string {
  return stemLabels[stem] ?? stem
}

function normalizeFileName(filename: string): string {
  const normalized = filename.split('/').pop()?.split('\\').pop()
  return normalized ?? filename
}

function formatOutputLabel(filename: string): string {
  const name = normalizeFileName(filename)
  const stem = name.replace(/\.[^.]+$/, '')
  return stemLabels[stem] ?? name
}

function resolveAudioUrl(jobId: string, filename: string): string {
  return getDownloadUrl(jobId, normalizeFileName(filename))
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

async function loadJobs(showLoading = false): Promise<void> {
  if (showLoading) {
    isLoading.value = true
  }

  try {
    jobs.value = await listJobs()
    errorMessage.value = ''
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error, '無法取得任務列表。')
  } finally {
    if (showLoading) {
      isLoading.value = false
    }
  }
}

function startPolling(): void {
  if (pollTimer !== null) {
    return
  }

  pollTimer = window.setInterval(() => {
    void loadJobs(false)
  }, 3000)
}

function stopPolling(): void {
  if (pollTimer === null) {
    return
  }

  window.clearInterval(pollTimer)
  pollTimer = null
}

async function handleDelete(job: Job): Promise<void> {
  const confirmed = window.confirm(`確定要刪除任務「${job.filename}」嗎？`)

  if (!confirmed) {
    return
  }

  isDeletingId.value = job.id

  try {
    await deleteJob(job.id)
    jobs.value = jobs.value.filter((item) => item.id !== job.id)
  } catch (error) {
    errorMessage.value = resolveErrorMessage(error, '刪除任務失敗。')
  } finally {
    isDeletingId.value = null
  }
}

watch(
  hasActiveJobs,
  (active) => {
    if (active) {
      startPolling()
      return
    }

    stopPolling()
  },
  { immediate: true },
)

onMounted(async () => {
  await loadJobs(true)
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<template>
  <section class="space-y-6">
    <div class="flex flex-col gap-4 rounded-3xl border border-white/10 bg-gray-900/80 p-6 shadow-xl shadow-black/20 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <p class="text-sm font-semibold uppercase tracking-[0.3em] text-indigo-300/80">Jobs</p>
        <h1 class="mt-2 text-3xl font-semibold text-white">任務列表</h1>
        <p class="mt-2 text-sm text-gray-400">
          追蹤目前任務狀態，完成後可直接試聽與下載分離結果。
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <span
          class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium"
          :class="hasActiveJobs ? 'border-amber-500/30 bg-amber-500/15 text-amber-200' : 'border-emerald-500/30 bg-emerald-500/15 text-emerald-200'"
        >
          {{ hasActiveJobs ? '自動更新中（3 秒）' : '目前無進行中任務' }}
        </span>
        <button
          type="button"
          class="rounded-xl border border-white/10 bg-white/10 px-4 py-2 text-sm text-gray-200 transition hover:bg-white/15"
          @click="loadJobs(true)"
        >
          立即刷新
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-3 text-sm text-red-200">
      {{ errorMessage }}
    </div>

    <div v-if="isLoading" class="rounded-3xl border border-white/10 bg-gray-900/70 p-10 text-center text-gray-400 shadow-xl shadow-black/20">
      正在載入任務列表...
    </div>

    <div v-else-if="sortedJobs.length === 0" class="rounded-3xl border border-dashed border-white/10 bg-gray-900/60 p-10 text-center shadow-xl shadow-black/20">
      <div class="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-indigo-500/10 text-3xl">🎼</div>
      <h2 class="mt-5 text-xl font-semibold text-white">目前沒有任何任務</h2>
      <p class="mt-2 text-sm text-gray-400">回到首頁上傳音檔或貼上 YouTube 連結，開始第一個分離工作。</p>
    </div>

    <div v-else class="space-y-4">
      <article
        v-for="job in sortedJobs"
        :key="job.id"
        class="rounded-3xl border border-white/10 bg-gray-900/80 p-6 shadow-xl shadow-black/20"
      >
        <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div class="space-y-3">
            <div class="flex flex-wrap items-center gap-3">
              <h2 class="text-xl font-semibold text-white">{{ job.filename }}</h2>
              <span class="inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium" :class="statusMeta[job.status].className">
                {{ statusMeta[job.status].label }}
              </span>
            </div>

            <div class="grid gap-3 text-sm text-gray-400 sm:grid-cols-2 xl:grid-cols-4">
              <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <p class="text-xs uppercase tracking-[0.2em] text-gray-500">模型</p>
                <p class="mt-1 font-medium text-gray-100">{{ job.model }}</p>
              </div>
              <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <p class="text-xs uppercase tracking-[0.2em] text-gray-500">輸出</p>
                <p class="mt-1 font-medium text-gray-100">{{ formatStems(job.stems) }}</p>
              </div>
              <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <p class="text-xs uppercase tracking-[0.2em] text-gray-500">建立時間</p>
                <p class="mt-1 font-medium text-gray-100">{{ formatDate(job.created_at) }}</p>
              </div>
              <div class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3">
                <p class="text-xs uppercase tracking-[0.2em] text-gray-500">完成時間</p>
                <p class="mt-1 font-medium text-gray-100">{{ formatDate(job.completed_at) }}</p>
              </div>
            </div>
          </div>

          <button
            v-if="job.status === 'completed' || job.status === 'failed'"
            type="button"
            class="inline-flex items-center justify-center rounded-xl border border-red-500/20 bg-red-500/10 px-4 py-2 text-sm font-medium text-red-200 transition hover:bg-red-500/20 disabled:cursor-not-allowed disabled:opacity-50"
            :disabled="isDeletingId === job.id"
            @click="handleDelete(job)"
          >
            {{ isDeletingId === job.id ? '刪除中...' : '刪除任務' }}
          </button>
        </div>

        <div v-if="job.status === 'completed'" class="mt-6 space-y-3 border-t border-white/10 pt-6">
          <h3 class="text-sm font-semibold uppercase tracking-[0.25em] text-emerald-300/80">輸出檔案</h3>
          <AudioPlayer
            v-for="outputFile in job.output_files"
            :key="outputFile"
            :label="formatOutputLabel(outputFile)"
            :src="resolveAudioUrl(job.id, outputFile)"
          />
        </div>

        <div v-else-if="job.status === 'failed'" class="mt-6 rounded-2xl border border-red-500/20 bg-red-500/10 px-4 py-4 text-sm text-red-200">
          <p class="font-medium">任務處理失敗</p>
          <p class="mt-2 text-red-100/90">{{ job.error || '後端未提供錯誤訊息。' }}</p>
        </div>

        <div v-else class="mt-6 rounded-2xl border border-white/10 bg-white/5 px-4 py-4 text-sm text-gray-300">
          任務目前{{ statusMeta[job.status].label }}，若仍在進行中，頁面會每 3 秒自動更新一次。
        </div>
      </article>
    </div>
  </section>
</template>
