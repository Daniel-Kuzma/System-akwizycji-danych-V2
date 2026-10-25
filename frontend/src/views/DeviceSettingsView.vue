<template>
  <div class="p-6 max-w-3xl mx-auto">
    <button @click="router.push(`/urzadzenia/${deviceId}`)" class="text-blue-600 hover:underline mb-6 flex items-center gap-2">
      &larr; Wróć do szczegółów urządzenia
    </button>

    <div v-if="isLoadingData" class="py-10 text-gray-500">Pobieranie konfiguracji...</div>
    
    <div v-else>
      <h1 class="text-2xl font-bold text-gray-800 mb-6">Ustawienia: {{ deviceName }}</h1>

      <!-- Sekcja 1: Aktualizacja danych -->
      <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-4">Informacje podstawowe</h2>
        <form @submit.prevent="handleUpdateInfo">
          <BaseInput label="Nazwa urządzenia" v-model="formName" required />
          <BaseInput label="Lokalizacja" v-model="formLocation" required />
          
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-1">Typ uprawy</label>
            <select v-model="formCultivationId" class="block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500 bg-white" required>
              <option v-for="type in cultivationTypes" :key="type.id" :value="type.id">
                {{ type.name }}
              </option>
            </select>
          </div>

          <div class="mb-6 flex items-center">
            <input id="email-alerts" type="checkbox" v-model="formEmailAlerts" class="h-4 w-4 text-blue-600 border-gray-300 rounded">
            <label for="email-alerts" class="ml-2 block text-sm text-gray-700">Włącz powiadomienia e-mail</label>
          </div>

          <div v-if="updateMessage" :class="updateSuccess ? 'text-green-600' : 'text-red-500'" class="text-sm mb-4">
            {{ updateMessage }}
          </div>

          <BaseButton type="submit" :isLoading="isUpdating">Zapisz zmiany</BaseButton>
        </form>
      </div>

      <!-- Sekcja 2: Zarządzanie Tokenem API -->
      <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-6">
        <h2 class="text-lg font-semibold text-gray-800 mb-2">Klucz dostępu API</h2>
        <p class="text-sm text-gray-600 mb-4">
          Wygenerowanie nowego klucza natychmiast odetnie połączenie Twojego ESP32. Będziesz musiał wgrać nowy token do pamięci mikrokontrolera.
        </p>
        
        <div v-if="newToken" class="bg-gray-100 p-4 rounded-md font-mono text-sm break-all border border-gray-300 mb-4">
          Nowy token: <span class="font-bold">{{ newToken }}</span>
        </div>

        <button @click="handleGenerateKey" :disabled="isGeneratingKey" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50">
          {{ isGeneratingKey ? 'Generowanie...' : 'Wygeneruj nowy token' }}
        </button>
      </div>

      <!-- Sekcja 3: Niebezpieczna strefa (Usuwanie) -->
      <div class="bg-red-50 p-6 rounded-lg border border-red-200">
        <h2 class="text-lg font-semibold text-red-800 mb-2">Usuń urządzenie</h2>
        <p class="text-sm text-red-600 mb-4">
          Ta operacja trwale usunie urządzenie, powiązane z nim tokeny oraz historię analiz. Aby potwierdzić, wpisz nazwę urządzenia: <strong>{{ deviceName }}</strong>
        </p>

        <BaseInput v-model="deleteConfirmName" placeholder="Wpisz nazwę urządzenia" />
        <div v-if="deleteError" class="text-red-500 text-sm mb-4">{{ deleteError }}</div>

        <button @click="handleDelete" :disabled="isDeleting || deleteConfirmName !== deviceName" class="w-full bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded disabled:opacity-50 transition-colors">
          {{ isDeleting ? 'Usuwanie...' : 'Trwale usuń urządzenie' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../services/api'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const route = useRoute()
const router = useRouter()
const deviceId = route.params.id

// Stan dla danych urządzenia
const isLoadingData = ref(true)
const deviceName = ref('')

// Formularz aktualizacji
const formName = ref('')
const formLocation = ref('')
const formCultivationId = ref(1) // Domyślna wartość w przypadku braku słownika z API
const formEmailAlerts = ref(false)
const updateMessage = ref('')
const updateSuccess = ref(false)
const isUpdating = ref(false)

// Zastępczy słownik
const cultivationTypes = ref([
  { id: 1, name: 'Pomidory' },
  { id: 2, name: 'Ogórki' },
  { id: 3, name: 'Truskawki' }
])

// Sekcja tokena
const newToken = ref('')
const isGeneratingKey = ref(false)

// Sekcja usuwania
const deleteConfirmName = ref('')
const isDeleting = ref(false)
const deleteError = ref('')

// Pobranie obecnych danych do formularza
const fetchDeviceData = async () => {
  try {
    const response = await apiFetch(`/device/user-device/${deviceId}`)
    if (response.ok) {
      const data = await response.json()
      deviceName.value = data.device_name
      formName.value = data.device_name
      formLocation.value = data.device_location
      formEmailAlerts.value = data.is_email_alert_enable
      // Brakuje tu zwrotki z type_of_cultivation_id w Twoim USerDeviceResponse, więc zakładamy 1
    }
  } catch (error) {
    console.error(error)
  } finally {
    isLoadingData.value = false
  }
}

const handleUpdateInfo = async () => {
  isUpdating.value = true
  updateMessage.value = ''
  
  const payload = {
    type_of_cultivation_id: formCultivationId.value,
    device_name: formName.value,
    device_location: formLocation.value,
    is_email_alert_enable: formEmailAlerts.value
  }

  try {
    const response = await apiFetch(`/device/change-device-information/${deviceId}`, {
      method: 'PUT',
      body: JSON.stringify(payload)
    })
    
    if (response.ok) {
      updateSuccess.value = true
      updateMessage.value = 'Dane zaktualizowane pomyślnie.'
      deviceName.value = formName.value // Odświeżenie nazwy w interfejsie
    } else {
      updateSuccess.value = false
      const data = await response.json()
      updateMessage.value = data.detail || 'Błąd aktualizacji.'
    }
  } catch (error) {
    updateSuccess.value = false
    updateMessage.value = 'Błąd komunikacji z serwerem.'
  } finally {
    isUpdating.value = false
  }
}

const handleGenerateKey = async () => {
  if (!confirm('Na pewno chcesz wygenerować nowy klucz? Poprzedni przestanie działać.')) return
  
  isGeneratingKey.value = true
  newToken.value = ''
  
  try {
    const response = await apiFetch(`/device/generate-new-key-for-device/${deviceId}`, {
      method: 'PUT'
    })
    
    if (response.ok) {
      const data = await response.json()
      newToken.value = data.token
    } else {
      alert('Nie udało się wygenerować nowego klucza.')
    }
  } catch (error) {
    alert('Błąd sieci.')
  } finally {
    isGeneratingKey.value = false
  }
}

const handleDelete = async () => {
  isDeleting.value = true
  deleteError.value = ''

  try {
    const response = await apiFetch(`/device/delete-device/${deviceId}`, {
      method: 'DELETE',
      body: JSON.stringify({ device_name: deleteConfirmName.value })
    })

    if (response.ok) {
      router.push('/urzadzenia')
    } else {
      const data = await response.json()
      deleteError.value = data.detail || 'Nie udało się usunąć urządzenia.'
    }
  } catch (error) {
    deleteError.value = 'Błąd połączenia z serwerem.'
  } finally {
    isDeleting.value = false
  }
}

onMounted(() => {
  fetchDeviceData()
})
</script>