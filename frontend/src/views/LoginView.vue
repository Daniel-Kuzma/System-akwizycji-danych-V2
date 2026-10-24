<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
      <h1 class="text-2xl font-bold mb-6 text-center text-gray-800">Panel Logowania</h1>
      
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

        <div v-if="errorMessage" class="text-red-500 text-sm text-center mb-4">
          {{ errorMessage }}
        </div>

        <BaseButton type="submit" :isLoading="isLoading">
          Zaloguj się
        </BaseButton>
      </form>

      <div class="mt-4 text-center text-sm text-gray-600">
        Nie masz konta? 
        <router-link to="/rejestracja" class="text-blue-600 hover:underline">Utwórz konto</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { jwtDecode } from 'jwt-decode'
import { BASE_URL } from '../services/api'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const router = useRouter()
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

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
</script>