<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'

const navItems = [
  { to: '/', label: '首頁' },
  { to: '/jobs', label: '任務列表' },
]
</script>

<template>
  <div class="min-h-screen bg-gray-950 text-white">
    <div class="absolute inset-x-0 top-0 -z-0 h-80 bg-[radial-gradient(circle_at_top,_rgba(99,102,241,0.18),_transparent_55%)]"></div>

    <div class="relative z-10 mx-auto flex min-h-screen max-w-7xl flex-col px-4 sm:px-6 lg:px-8">
      <header class="sticky top-0 z-20 border-b border-white/10 bg-gray-950/80 backdrop-blur">
        <div class="flex items-center justify-between py-4">
          <RouterLink to="/" class="flex items-center gap-3 text-lg font-semibold tracking-wide text-white">
            <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-500 text-sm font-bold shadow-lg shadow-indigo-950/50">
              DM
            </div>
            <div>
              <p>Demucs Web</p>
              <p class="text-xs font-normal text-gray-400">音源分離控制台</p>
            </div>
          </RouterLink>

          <nav class="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 p-1 text-sm text-gray-300">
            <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :to="item.to"
              v-slot="{ href, navigate, isActive }"
              custom
            >
              <a
                :href="href"
                class="rounded-full px-4 py-2 transition"
                :class="isActive ? 'bg-white text-gray-950 shadow' : 'hover:bg-white/10 hover:text-white'"
                @click="navigate"
              >
                {{ item.label }}
              </a>
            </RouterLink>
          </nav>
        </div>
      </header>

      <main class="flex-1 py-8 sm:py-10">
        <RouterView />
      </main>

      <footer class="border-t border-white/10 py-6 text-center text-sm text-gray-500">
        使用 Demucs 建立更直覺的音源分離工作流程。
      </footer>
    </div>
  </div>
</template>
