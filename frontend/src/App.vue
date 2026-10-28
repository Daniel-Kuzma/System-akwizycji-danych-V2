<template>
  <div class="min-h-screen bg-gray-50 dark:bg-custom-dark transition-colors duration-300">
    
    <nav v-if="!isAuthPage" class="bg-white dark:bg-custom-card border-b border-gray-200 dark:border-custom-border p-4 flex justify-between items-center transition-colors duration-300">
      
      <!-- Lewa strona: Powrót do urządzeń (ukryty dla admina) -->
      <div>
        <router-link 
          v-if="userRole !== 'admin'"
          to="/urzadzenia" 
          class="text-gray-800 dark:text-custom-light font-bold text-lg hover:text-blue-600 dark:hover:text-blue-400 transition-colors flex items-center gap-2"
        >
          Moje urządzenia
        </router-link>
      </div>

      <!-- Prawa strona: Reszta linków -->
      <div class="flex gap-4 items-center">
        <router-link 
          to="/ustawienia-konta" 
          class="text-blue-500 dark:text-custom-light hover:underline transition-colors"
        >
          Ustawienia konta
        </router-link>

        <button 
          @click="logout" 
          class="text-gray-600 dark:text-custom-muted hover:text-black dark:hover:text-custom-light transition-colors"
        >
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
import { computed, onMounted } from 'vue'
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

// Sprawdzenie i nałożenie motywu przy uruchomieniu aplikacji
onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'light'
  if (savedTheme === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})
</script>