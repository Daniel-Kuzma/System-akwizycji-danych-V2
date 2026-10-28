<template>
  <!-- Zmiana tła strony na adaptujące się do motywu -->
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-custom-dark transition-colors">
    <!-- Panel dopasowany do trybu ciemnego -->
    <div class="bg-white dark:bg-custom-card p-8 rounded-lg shadow-md w-full max-w-md border border-transparent dark:border-custom-border transition-colors">
      
      <!-- Panel Logowania -->
      <div v-if="!showResetForm">
        <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-custom-light">Panel Logowania</h1>
        
        <form @submit.prevent="handleLogin">
          <BaseInput 
            label="Nazwa użytkownika" 
            v-model="username" 
            required 
          />
          
          <BaseInput 
            label="Hasło" 
            type="password" 
            v-model="password" 
            required 
          />

          <div v-if="errorMessage" class="text-red-500 dark:text-red-400 text-sm text-center mb-4">
            {{ errorMessage }}
          </div>

          <BaseButton type="submit" :isLoading="isLoading">
            Zaloguj się
          </BaseButton>
        </form>

        <div class="mt-4 text-center text-sm text-gray-600 dark:text-custom-muted space-y-2">
          <div>
            <button @click="showResetForm = true" type="button" class="text-blue-600 dark:text-blue-400 hover:underline focus:outline-none">
              Zapomniałeś hasła?
            </button>
          </div>
          <div>
            Nie masz konta? 
            <router-link to="/rejestracja" class="text-blue-600 dark:text-blue-400 hover:underline">Utwórz konto</router-link>
          </div>
        </div>
      </div>

      <!-- Panel Resetowania Hasła -->
      <div v-else>
        <h1 class="text-2xl font-bold mb-4 text-center text-gray-800 dark:text-custom-light">Resetowanie hasła</h1>
        <p class="text-sm text-gray-600 dark:text-custom-muted text-center mb-6">
          Podaj adres e-mail powiązany z kontem. Wyślemy na niego nowe hasło.
        </p>

        <form @submit.prevent="handleResetPassword">
          <BaseInput 
            label="Adres e-mail" 
            type="email" 
            v-model="resetEmail" 
            required 
          />

          <div v-if="resetMessage" :class="resetSuccess ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'" class="text-sm text-center mb-4 font-medium">
            {{ resetMessage }}
          </div>

          <BaseButton type="submit" :isLoading="isResetting">
            Wyślij nowe hasło
          </BaseButton>
        </form>

        <div class="mt-4 text-center text-sm">
          <button @click="showResetForm = false; resetMessage = ''" type="button" class="text-gray-600 dark:text-custom-muted hover:text-gray-800 dark:hover:text-custom-light hover:underline focus:outline-none transition-colors">
            &larr; Wróć do ekranu logowania
          </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { jwtDecode } from 'jwt-decode'
import { BASE_URL } from '../services/api'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const router = useRouter()

// Stan logowania
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

// Stan resetowania hasła
const showResetForm = ref(false)
const resetEmail = ref('')
const isResetting = ref(false)
const resetMessage = ref('')
const resetSuccess = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  const formData = new URLSearchParams()
  formData.append('username', username.value)
  formData.append('password', password.value)

  try {
    const response = await fetch(`${BASE_URL}/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: formData
    })

    if (!response.ok) {
      errorMessage.value = 'Nieprawidłowa nazwa użytkownika lub hasło.'
      return
    }

    const data = await response.json()
    const token = data.access_token

    const decodedToken = jwtDecode(token)
    const userRole = decodedToken.role

    localStorage.setItem('token', token)
    localStorage.setItem('role', userRole)

    if (userRole === 'admin') {
      router.push('/admin')
    } else {
      router.push('/urzadzenia')
    }
  } catch (error) {
    errorMessage.value = 'Brak połączenia z serwerem.'
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}

const handleResetPassword = async () => {
  isResetting.value = true
  resetMessage.value = ''
  resetSuccess.value = false

  try {
    const response = await fetch(`${BASE_URL}/users/reset-user-password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ email: resetEmail.value })
    })

    if (response.ok) {
      resetSuccess.value = true
      resetMessage.value = 'Nowe hasło zostało wysłane na podany adres e-mail.'
      resetEmail.value = ''
    } else {
      const data = await response.json()
      resetMessage.value = data.detail || 'Nie udało się zresetować hasła.'
    }
  } catch (error) {
    resetMessage.value = 'Brak połączenia z serwerem.'
    console.error('Reset password error:', error)
  } finally {
    isResetting.value = false
  }
}

// Upewniamy się, że strona logowania wczytuje preferencję motywu z localStorage
onMounted(() => {
  if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})
</script>