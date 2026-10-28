<template>
  <div class="p-6 max-w-4xl mx-auto space-y-6">
    <button @click="router.back()" class="text-blue-600 dark:text-blue-400 hover:underline mb-2 flex items-center gap-2">
      &larr; Wróć
    </button>

    <h1 class="text-3xl font-bold text-gray-800 dark:text-custom-light">Ustawienia Konta</h1>

    <div v-if="isLoadingData" class="text-center py-4 text-gray-500 dark:text-custom-muted">Ładowanie danych...</div>
    
    <div v-else class="space-y-6">
      
      <!-- Sekcja: Wygląd aplikacji (Suwak) -->
      <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border flex justify-between items-center">
        <div>
          <h2 class="text-xl font-bold text-gray-800 dark:text-custom-light">Motyw interfejsu</h2>
          <p class="text-sm text-gray-500 dark:text-custom-muted">Przełącz między jasną a ciemną paletą kolorów</p>
        </div>
        
        <label class="relative inline-flex items-center cursor-pointer">
          <input type="checkbox" v-model="isDarkMode" @change="toggleTheme" class="sr-only peer">
          <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
        </label>
      </div>

      <!-- Sekcja 1: Dane użytkownika -->
      <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border">
        <h2 class="text-xl font-bold mb-4 text-gray-800 dark:text-custom-light">Informacje o profilu</h2>
        <form @submit.prevent="updateProfile" class="space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <BaseInput label="Imię" v-model="userForm.name" required />
            <BaseInput label="Nazwisko" v-model="userForm.lastname" required />
            <BaseInput label="Nazwa użytkownika" v-model="userForm.username" required />
            <BaseInput label="Adres E-mail" type="email" v-model="userForm.email" required />
          </div>
          <p class="text-xs text-gray-500 dark:text-custom-muted">Konto utworzono: {{ formatDate(createdAt) }}</p>
          <div v-if="profileMessage" :class="profileSuccess ? 'text-green-600' : 'text-red-500'" class="text-sm font-medium">{{ profileMessage }}</div>
          <BaseButton type="submit" :isLoading="isSubmittingProfile">Zapisz zmiany</BaseButton>
        </form>
      </div>

      <!-- Sekcja 2: Zmiana hasła -->
      <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border">
        <h2 class="text-xl font-bold mb-4 text-center text-gray-800 dark:text-custom-light">Zmiana hasła</h2>
        <form @submit.prevent="changePassword" class="space-y-4 max-w-md mx-auto w-full">
          <BaseInput label="Obecne hasło" type="password" v-model="pwdForm.old_password" required />
          <BaseInput label="Nowe hasło" type="password" v-model="pwdForm.new_password" required pattern="^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).+$" minlength="12" title="Hasło musi mieć co najmniej 12 znaków i zawierać wielką literę, małą literę oraz cyfrę." />
          <BaseInput label="Potwierdź nowe hasło" type="password" v-model="pwdConfirm" required />
          <div v-if="pwdMessage" :class="pwdSuccess ? 'text-green-600' : 'text-red-500'" class="text-sm font-medium text-center">{{ pwdMessage }}</div>
          <BaseButton type="submit" :isLoading="isSubmittingPwd">Zaktualizuj hasło</BaseButton>
        </form>
      </div>

      <!-- Sekcja 3: Usuwanie konta -->
      <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-red-200 dark:border-red-900/50">
        <h2 class="text-xl font-bold text-red-600 dark:text-red-500 mb-4 text-center">Usuwanie konta</h2>
        <p class="text-sm text-gray-600 dark:text-custom-muted mb-4 text-center max-w-md mx-auto">Operacji tej nie można cofnąć. Aby potwierdzić usunięcie profilu, podaj swoje aktualne hasło.</p>
        <form @submit.prevent="deleteAccount" class="space-y-4 max-w-md mx-auto w-full">
          <BaseInput label="Hasło do konta" type="password" v-model="deletePassword" required />
          <div v-if="deleteMessage" class="text-red-500 text-sm font-medium text-center">{{ deleteMessage }}</div>
          <button type="submit" :disabled="isSubmittingDelete" class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 disabled:opacity-50 transition-colors w-full">{{ isSubmittingDelete ? 'Usuwanie...' : 'Usuń konto trwale' }}</button>
        </form>
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
const isLoadingData = ref(true)
const isDarkMode = ref(false)

const userForm = ref({ name: '', lastname: '', username: '', email: '' })
const createdAt = ref('')
const profileMessage = ref('')
const profileSuccess = ref(false)
const isSubmittingProfile = ref(false)

const pwdForm = ref({ old_password: '', new_password: '' })
const pwdConfirm = ref('')
const pwdMessage = ref('')
const pwdSuccess = ref(false)
const isSubmittingPwd = ref(false)

const deletePassword = ref('')
const deleteMessage = ref('')
const isSubmittingDelete = ref(false)

const getHeaders = () => ({
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${localStorage.getItem('token')}`
})

const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('pl-PL')
}

const toggleTheme = () => {
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

const loadUserData = async () => {
  try {
    const res = await fetch(`${BASE_URL}/users/get-user-information`, { headers: getHeaders() })
    if (res.ok) {
      const data = await res.json()
      userForm.value = { name: data.name, lastname: data.lastname, username: data.username, email: data.email }
      createdAt.value = data.created_at
    }
  } catch (error) {
    console.error('Błąd pobierania danych', error)
  } finally {
    isLoadingData.value = false
  }
}

const updateProfile = async () => {
  profileMessage.value = ''
  profileSuccess.value = false
  isSubmittingProfile.value = true
  try {
    const res = await fetch(`${BASE_URL}/users/change-user-information`, { method: 'PUT', headers: getHeaders(), body: JSON.stringify(userForm.value) })
    if (res.ok) {
      profileSuccess.value = true
      profileMessage.value = 'Dane profilu zostały zaktualizowane.'
    } else {
      const data = await res.json()
      profileMessage.value = data.detail || 'Błąd aktualizacji danych.'
    }
  } catch (error) { profileMessage.value = 'Błąd komunikacji z serwerem.' } finally { isSubmittingProfile.value = false }
}

const changePassword = async () => {
  pwdMessage.value = ''
  pwdSuccess.value = false
  if (pwdForm.value.new_password !== pwdConfirm.value) {
    pwdMessage.value = 'Nowe hasła nie są identyczne.'
    return
  }
  isSubmittingPwd.value = true
  try {
    const res = await fetch(`${BASE_URL}/users/change-user-password`, { method: 'PUT', headers: getHeaders(), body: JSON.stringify(pwdForm.value) })
    if (res.ok) {
      pwdSuccess.value = true
      pwdMessage.value = 'Hasło zostało zmienione.'
      pwdForm.value = { old_password: '', new_password: '' }
      pwdConfirm.value = ''
    } else {
      const data = await res.json()
      pwdMessage.value = data.detail || 'Błąd przy zmianie hasła.'
    }
  } catch (error) { pwdMessage.value = 'Błąd komunikacji z serwerem.' } finally { isSubmittingPwd.value = false }
}

const deleteAccount = async () => {
  if (!confirm('Czy na pewno chcesz bezpowrotnie usunąć swoje konto?')) return
  deleteMessage.value = ''
  isSubmittingDelete.value = true
  try {
    const res = await fetch(`${BASE_URL}/users/delete-user-account`, { method: 'DELETE', headers: getHeaders(), body: JSON.stringify({ password: deletePassword.value }) })
    if (res.ok) {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      router.push('/login')
    } else {
      const data = await res.json()
      deleteMessage.value = data.detail || 'Podano błędne hasło lub wystąpił błąd.'
    }
  } catch (error) { deleteMessage.value = 'Błąd komunikacji z serwerem.' } finally { isSubmittingDelete.value = false }
}

onMounted(() => {
  isDarkMode.value = document.documentElement.classList.contains('dark')
  loadUserData()
})
</script>