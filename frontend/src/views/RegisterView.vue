<template>
  <!-- Zmiana tła strony na adaptujące się do motywu -->
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-custom-dark py-10 transition-colors">
    <!-- Panel dopasowany do trybu ciemnego -->
    <div class="bg-white dark:bg-custom-card p-8 rounded-lg shadow-md w-full max-w-md border border-transparent dark:border-custom-border transition-colors">
      <h1 class="text-2xl font-bold mb-6 text-center text-gray-800 dark:text-custom-light">Utwórz konto</h1>

      <form @submit.prevent="handleRegister">
        <BaseInput label="Imię" v-model="name" required />
        <BaseInput label="Nazwisko" v-model="lastname" required />
        <BaseInput label="Nazwa użytkownika" v-model="username" required minlength="4" />
        <BaseInput label="Adres email" type="email" v-model="email" required />
        
        <BaseInput 
          label="Hasło" 
          type="password" 
          v-model="password" 
          required 
          :error="passwordError"
          @input="validatePassword"
        />

        <div v-if="errorMessage" class="text-red-500 dark:text-red-400 text-sm text-center mb-4">
          {{ errorMessage }}
        </div>
        <div v-if="successMessage" class="text-green-500 dark:text-green-400 text-sm text-center mb-4">
          {{ successMessage }}
        </div>

        <BaseButton type="submit" :isLoading="isLoading">
          Zarejestruj się
        </BaseButton>
      </form>

      <div class="mt-6 text-center text-sm text-gray-600 dark:text-custom-muted">
        Masz już konto? 
        <router-link to="/login" class="text-blue-600 dark:text-blue-400 hover:underline">Zaloguj się</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { BASE_URL } from '../services/api'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const router = useRouter()

const name = ref('')
const lastname = ref('')
const username = ref('')
const email = ref('')
const password = ref('')

const errorMessage = ref('')
const successMessage = ref('')
const passwordError = ref('')
const isLoading = ref(false)

const validatePassword = () => {
  const regex = /^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$/
  if (password.value.length < 12) {
    passwordError.value = 'Hasło musi mieć co najmniej 12 znaków.'
    return false
  }
  if (!regex.test(password.value)) {
    passwordError.value = 'Hasło musi zawierać małą/wielką literę oraz cyfrę.'
    return false
  }
  passwordError.value = ''
  return true
}

const handleRegister = async () => {
  if (!validatePassword()) return

  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const payload = {
    name: name.value,
    lastname: lastname.value,
    username: username.value,
    password: password.value,
    email: email.value
  }

  try {
    const response = await fetch(`${BASE_URL}/create-account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (!response.ok) {
      errorMessage.value = data.detail || 'Wystąpił błąd podczas rejestracji.'
      return
    }

    successMessage.value = 'Konto utworzone. Przekierowywanie do logowania...'
    setTimeout(() => {
      router.push('/login')
    }, 2000)

  } catch (error) {
    errorMessage.value = 'Brak połączenia z serwerem.'
  } finally {
    isLoading.value = false
  }
}

// Upewniamy się, że strona rejestracji wczytuje preferencję motywu z localStorage
onMounted(() => {
  if (localStorage.getItem('theme') === 'dark') {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
})
</script>