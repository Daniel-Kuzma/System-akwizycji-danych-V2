<template>
  <div class="p-6 max-w-3xl mx-auto">
    <button @click="router.push('/urzadzenia')" class="text-blue-600 dark:text-blue-400 hover:underline mb-6 flex items-center gap-2">
      &larr; Wróć do listy urządzeń
    </button>

    <div class="bg-white dark:bg-custom-card p-8 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border transition-colors">
      <h1 class="text-2xl font-bold mb-6 text-gray-800 dark:text-custom-light">Dodaj nowe urządzenie</h1>

      <!-- Formularz widoczny przed wygenerowaniem tokena -->
      <form v-if="!generatedToken" @submit.prevent="handleAddDevice">
        <BaseInput
          label="Nazwa urządzenia (np. Termometr 1)"
          v-model="deviceName"
          required
        />

        <BaseInput
          label="Lokalizacja (np. Szklarnia Północna)"
          v-model="deviceLocation"
          required
        />

        <!-- Nowe pole wyszukiwania typu uprawy -->
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
          <input
            id="email-alerts"
            type="checkbox"
            v-model="isEmailAlertEnable"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-custom-border rounded bg-white dark:bg-custom-dark dark:checked:bg-blue-600 dark:checked:border-blue-600 accent-blue-600 transition-colors"
          >
          <label for="email-alerts" class="ml-2 block text-sm text-gray-700 dark:text-custom-light">
            Włącz powiadomienia e-mail o alertach krytycznych
          </label>
        </div>

        <div v-if="errorMessage" class="text-red-500 text-sm mb-4">
          {{ errorMessage }}
        </div>

        <BaseButton type="submit" :isLoading="isLoading">
          Zarejestruj urządzenie
        </BaseButton>
      </form>

      <!-- Ekran sukcesu z tokenem MQTT/API -->
      <div v-else class="text-center py-8">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 dark:bg-green-900/30 text-green-500 dark:text-green-400 mb-6">
          <span class="text-3xl">✓</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 dark:text-custom-light mb-2">Urządzenie dodane!</h2>
        <p class="text-gray-600 dark:text-custom-muted mb-6">
          Skopiuj poniższy token API. Będzie on potrzebny do połączenia sprzętu z serwerem. Ze względów bezpieczeństwa nie pokażemy go ponownie.
        </p>
        
        <div class="bg-gray-100 dark:bg-custom-dark p-4 rounded-md font-mono text-lg break-all border border-gray-300 dark:border-custom-border mb-8 text-gray-900 dark:text-custom-light">
          {{ generatedToken }}
        </div>

        <button @click="router.push('/urzadzenia')" class="bg-blue-600 dark:bg-blue-700 hover:bg-blue-700 dark:hover:bg-blue-600 text-white font-bold py-2 px-6 rounded transition-colors">
          Przejdź do panelu urządzeń
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../services/api'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const router = useRouter()

const deviceName = ref('')
const deviceLocation = ref('')
const typeOfCultivation = ref('') // Przechowuje ID uprawy
const isEmailAlertEnable = ref(false)

// Pusta lista na start, zostanie wypełniona przez API
const cultivationTypes = ref([])

// Nowe stany wyszukiwarki
const searchQuery = ref('')
const isDropdownOpen = ref(false)

// Dynamiczne filtrowanie upraw
const filteredCultivations = computed(() => {
  if (!searchQuery.value) return cultivationTypes.value
  const lowerCaseQuery = searchQuery.value.toLowerCase()
  return cultivationTypes.value.filter(type => 
    type.name.toLowerCase().includes(lowerCaseQuery)
  )
})

// Wybór elementu z listy
const selectCultivation = (type) => {
  typeOfCultivation.value = type.id
  searchQuery.value = type.name
  isDropdownOpen.value = false
}

const isLoading = ref(false)
const errorMessage = ref('')
const generatedToken = ref('')

// Pobieranie typów upraw z nowego endpointu po załadowaniu widoku
const loadCultivations = async () => {
  try {
    const res = await apiFetch('/cultivation/all-cultivation')
    if (res.ok) {
      const data = await res.json()
      // Mapujemy name_of_cultivation zwrócone przez API na pole name, 
      // na którym operuje wyszukiwarka
      cultivationTypes.value = data.map(c => ({
        id: c.id,
        name: c.name_of_cultivation
      }))
    }
  } catch (error) {
    console.error('Błąd pobierania słownika upraw:', error)
  }
}

const handleAddDevice = async () => {
  isLoading.value = true
  errorMessage.value = ''

  // Weryfikacja czy wpisany tekst odpowiada jakiejś uprawie z listy
  const matchedType = cultivationTypes.value.find(
    c => c.name.toLowerCase() === searchQuery.value.toLowerCase()
  )
  
  if (matchedType) {
    typeOfCultivation.value = matchedType.id
  } else {
    errorMessage.value = 'Wybierz poprawny typ uprawy z podanej listy.'
    isLoading.value = false
    return
  }

  const payload = {
    type_of_cultivation: parseInt(typeOfCultivation.value),
    device_name: deviceName.value,
    device_location: deviceLocation.value,
    is_email_alert_enable: isEmailAlertEnable.value
  }

  try {
    const response = await apiFetch('/device/create-new-device', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    const data = await response.json()

    if (response.ok) {
      const tokenMatch = data.message.split('token: ')
      if (tokenMatch.length > 1) {
        generatedToken.value = tokenMatch[1]
      } else {
        generatedToken.value = 'Błąd odczytu. Wygeneruj nowy token w ustawieniach.'
      }
    } else {
      errorMessage.value = data.detail || 'Nie udało się dodać urządzenia.'
    }
  } catch (error) {
    errorMessage.value = 'Błąd komunikacji z serwerem.'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadCultivations()
})
</script>