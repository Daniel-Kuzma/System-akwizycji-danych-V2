<template>
  <div class="p-6 max-w-3xl mx-auto">
    <button @click="router.push(`/urzadzenia/${deviceId}`)" class="text-blue-600 dark:text-blue-400 hover:underline mb-6 flex items-center gap-2 transition-colors">
      &larr; Wróć do szczegółów urządzenia
    </button>

    <div v-if="isLoadingData" class="py-10 text-gray-500 dark:text-custom-muted">Pobieranie konfiguracji...</div>
    
    <div v-else>
      <h1 class="text-2xl font-bold text-gray-800 dark:text-custom-light mb-6 transition-colors">Ustawienia: {{ deviceName }}</h1>

      <!-- Sekcja 1: Aktualizacja danych -->
      <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border mb-6 transition-colors">
        <h2 class="text-lg font-semibold text-gray-800 dark:text-custom-light mb-4">Informacje podstawowe</h2>
        <form @submit.prevent="handleUpdateInfo">
          <BaseInput label="Nazwa urządzenia" v-model="formName" required />
          <BaseInput label="Lokalizacja" v-model="formLocation" required />
          
          <!-- Nowe pole wyszukiwania uprawy -->
          <div class="mb-4 relative">
            <label class="block text-sm font-medium text-gray-700 dark:text-custom-light mb-1">Typ uprawy</label>
            <input 
              type="text" 
              v-model="searchQuery" 
              @focus="isDropdownOpen = true"
              @blur="isDropdownOpen = false"
              placeholder="Wpisz, aby wyszukać uprawę..."
              class="block w-full border border-gray-300 dark:border-custom-border rounded-md p-2 focus:ring-blue-500 focus:border-blue-500 bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors" 
              required
            />
            
            <!-- Rozwijana lista wyników -->
            <ul 
              v-show="isDropdownOpen" 
              class="absolute z-10 w-full mt-1 bg-white dark:bg-custom-dark border border-gray-300 dark:border-custom-border rounded-md shadow-lg max-h-60 overflow-y-auto"
            >
              <li 
                v-for="type in filteredCultivations" 
                :key="type.id"
                @mousedown.prevent="selectCultivation(type)"
                class="cursor-pointer px-4 py-2 hover:bg-blue-50 dark:hover:bg-gray-800 text-gray-900 dark:text-custom-light transition-colors"
              >
                {{ type.name }}
              </li>
              <li v-if="filteredCultivations.length === 0" class="px-4 py-2 text-gray-500 dark:text-custom-muted italic">
                Brak wyników do wyświetlenia
              </li>
            </ul>
          </div>

          <div class="mb-6 flex items-center">
            <input id="email-alerts" type="checkbox" v-model="formEmailAlerts" class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-custom-border rounded bg-white dark:bg-custom-dark dark:checked:bg-blue-600 dark:checked:border-blue-600 accent-blue-600 transition-colors">
            <label for="email-alerts" class="ml-2 block text-sm text-gray-700 dark:text-custom-light">Włącz powiadomienia e-mail</label>
          </div>

          <div v-if="updateMessage" :class="updateSuccess ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'" class="text-sm mb-4">
            {{ updateMessage }}
          </div>

          <BaseButton type="submit" :isLoading="isUpdating">Zapisz zmiany</BaseButton>
        </form>
      </div>

      <!-- Sekcja 2: Zarządzanie Tokenem API -->
      <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border mb-6 transition-colors">
        <h2 class="text-lg font-semibold text-gray-800 dark:text-custom-light mb-2">Klucz dostępu API</h2>
        <p class="text-sm text-gray-600 dark:text-custom-muted mb-4">
          Wygenerowanie nowego klucza natychmiast odetnie połączenie Twojego ESP32. Będziesz musiał wgrać nowy token do pamięci mikrokontrolera.
        </p>
        
        <div v-if="newToken" class="bg-gray-100 dark:bg-custom-dark p-4 rounded-md font-mono text-sm break-all border border-gray-300 dark:border-custom-border text-gray-900 dark:text-custom-light mb-4 transition-colors">
          Nowy token: <span class="font-bold">{{ newToken }}</span>
        </div>

        <button @click="handleGenerateKey" :disabled="isGeneratingKey" class="bg-yellow-500 dark:bg-yellow-600 hover:bg-yellow-600 dark:hover:bg-yellow-500 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50">
          {{ isGeneratingKey ? 'Generowanie...' : 'Wygeneruj nowy token' }}
        </button>
      </div>

      <!-- Sekcja 3: Niebezpieczna strefa (Usuwanie) -->
      <div class="bg-red-50 dark:bg-red-900/20 p-6 rounded-lg border border-red-200 dark:border-red-900/50 transition-colors">
        <h2 class="text-lg font-semibold text-red-800 dark:text-red-500 mb-2">Usuń urządzenie</h2>
        <p class="text-sm text-red-600 dark:text-red-400/80 mb-4">
          Ta operacja trwale usunie urządzenie, powiązane z nim tokeny oraz historię analiz. Aby potwierdzić, wpisz nazwę urządzenia: <strong class="dark:text-red-400">{{ deviceName }}</strong>
        </p>

        <BaseInput v-model="deleteConfirmName" placeholder="Wpisz nazwę urządzenia" />
        <div v-if="deleteError" class="text-red-500 dark:text-red-400 text-sm mt-2 mb-4">{{ deleteError }}</div>

        <button @click="handleDelete" :disabled="isDeleting || deleteConfirmName !== deviceName" class="w-full bg-red-600 dark:bg-red-700 hover:bg-red-700 dark:hover:bg-red-600 text-white font-bold py-2 px-4 rounded mt-4 disabled:opacity-50 transition-colors">
          {{ isDeleting ? 'Usuwanie...' : 'Trwale usuń urządzenie' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../services/api'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const route = useRoute()
const router = useRouter()
const deviceId = route.params.id

const isLoadingData = ref(true)
const deviceName = ref('')

const formName = ref('')
const formLocation = ref('')
const formCultivationId = ref(null) // ID uprawy przypisanej do urządzenia
const formEmailAlerts = ref(false)
const updateMessage = ref('')
const updateSuccess = ref(false)
const isUpdating = ref(false)

// Zasilane z API
const cultivationTypes = ref([])

const searchQuery = ref('')
const isDropdownOpen = ref(false)

const filteredCultivations = computed(() => {
  if (!searchQuery.value) return cultivationTypes.value
  const lowerCaseQuery = searchQuery.value.toLowerCase()
  return cultivationTypes.value.filter(type => 
    type.name.toLowerCase().includes(lowerCaseQuery)
  )
})

const selectCultivation = (type) => {
  formCultivationId.value = type.id 
  searchQuery.value = type.name
  isDropdownOpen.value = false
}

const newToken = ref('')
const isGeneratingKey = ref(false)
const deleteConfirmName = ref('')
const isDeleting = ref(false)
const deleteError = ref('')

// Pobieranie obu zestawów danych równolegle
const loadInitialData = async () => {
  isLoadingData.value = true
  
  try {
    const [deviceRes, cultivationsRes] = await Promise.all([
      apiFetch(`/device/user-device/${deviceId}`),
      apiFetch('/cultivation/all-cultivation')
    ])

    if (cultivationsRes.ok) {
      const data = await cultivationsRes.json()
      cultivationTypes.value = data.map(c => ({
        id: c.id,
        name: c.name_of_cultivation
      }))
    }

    if (deviceRes.ok) {
      const data = await deviceRes.json()
      deviceName.value = data.device_name
      formName.value = data.device_name
      formLocation.value = data.device_location
      formEmailAlerts.value = data.is_email_alert_enable
      
      // Jeżeli endpoint nie zwraca type_of_cultivation_id, trzeba ustawić np. 1
      formCultivationId.value = data.type_of_cultivation_id || 1
      
      const currentCultivation = cultivationTypes.value.find(c => c.id === formCultivationId.value)
      if (currentCultivation) {
        searchQuery.value = currentCultivation.name
      }
    }
  } catch (error) {
    console.error('Błąd inicjalizacji ustawień:', error)
  } finally {
    isLoadingData.value = false
  }
}

const handleUpdateInfo = async () => {
  isUpdating.value = true
  updateMessage.value = ''
  
  const matchedType = cultivationTypes.value.find(
    c => c.name.toLowerCase() === searchQuery.value.toLowerCase()
  )
  if (matchedType) {
    formCultivationId.value = matchedType.id
  }

  const payload = {
    type_of_cultivation_id: formCultivationId.value, // Tylko ID
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
      deviceName.value = formName.value 
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
  isGeneratingKey.value = true; newToken.value = ''
  try {
    const response = await apiFetch(`/device/generate-new-key-for-device/${deviceId}`, { method: 'PUT' })
    if (response.ok) {
      const data = await response.json(); newToken.value = data.token
    } else alert('Nie udało się wygenerować nowego klucza.')
  } catch (error) { alert('Błąd sieci.') } finally { isGeneratingKey.value = false }
}

const handleDelete = async () => {
  isDeleting.value = true; deleteError.value = ''
  try {
    const response = await apiFetch(`/device/delete-device/${deviceId}`, {
      method: 'DELETE', body: JSON.stringify({ device_name: deleteConfirmName.value })
    })
    if (response.ok) router.push('/urzadzenia')
    else {
      const data = await response.json(); deleteError.value = data.detail || 'Nie udało się usunąć urządzenia.'
    }
  } catch (error) { deleteError.value = 'Błąd połączenia z serwerem.' } finally { isDeleting.value = false }
}

onMounted(() => {
  loadInitialData()
})
</script>