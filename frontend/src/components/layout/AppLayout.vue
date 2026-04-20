<script setup>
import AppHeader from './AppHeader.vue'
</script>

<template>
  <div class="flex flex-col h-screen bg-background overflow-hidden">
    <AppHeader />
    <main class="flex-1 overflow-y-auto p-6 bg-slate-50/50">
      <RouterView />
    </main>
  </div>
</template>
