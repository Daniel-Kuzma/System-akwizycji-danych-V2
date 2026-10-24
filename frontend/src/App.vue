<template>
  <div class="min-h-screen bg-gray-50">
    <nav v-if="!isAuthPage" class="bg-white shadow p-4 flex justify-between items-center">
      <div class="font-bold text-xl text-blue-600">IoT System</div>
      
      <div class="flex gap-4">
        <router-link 
          v-if="userRole === 'user'" 
          to="/urzadzenia/dodaj" 
          class="text-blue-500 hover:underline">
          Dodaj urządzenie
        </router-link>

        <router-link 
          v-if="userRole === 'admin'" 
          to="/admin" 
          class="text-red-500 hover:underline">
          Panel Admina
        </router-link>

        <button @click="logout" class="text-gray-600 hover:text-black">
          Wyloguj
        </button>
      </div>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/rejestracja'
})

const userRole = computed(() => localStorage.getItem('role'))

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push('/login')
}
</script>