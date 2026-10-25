<template>
  <div class="p-6 max-w-3xl mx-auto">
    <button @click="router.push('/urzadzenia')" class="text-blue-600 hover:underline mb-6 flex items-center gap-2">
      &larr; Wróć do listy urządzeń
    </button>

    <div class="bg-white p-8 rounded-lg shadow-sm border border-gray-200">
      <h1 class="text-2xl font-bold mb-6 text-gray-800">Dodaj nowe urządzenie</h1>

      <!-- Formularz widoczny przed wygenerowaniem tokena -->
      <form v-if="!generatedToken" @submit.prevent="handleAddDevice">
        <BaseInput
          label="Nazwa urządzenia (np. Node-1)"
          v-model="deviceName"
          required
        />

        <BaseInput
          label="Lokalizacja (np. Szklarnia Północna)"
          v-model="deviceLocation"
          required
        />

        <!-- Wybór typu uprawy - docelowo do spięcia z API -->
        <div class="mb-4">
          <label class="block text-sm font-medium text-gray-700 mb-1">Typ uprawy</label>
          <select
            v-model="typeOfCultivation"
            class="block w-full border border-gray-300 rounded-md p-2 focus:ring-blue-500 focus:border-blue-500 bg-white"
            required
          >
            <option value="" disabled>Wybierz z listy...</option>
            <option v-for="type in cultivationTypes" :key="type.id" :value="type.id">
              {{ type.name }}
            </option>
          </select>
        </div>

        <div class="mb-6 flex items-center">
          <input
            id="email-alerts"
            type="checkbox"
            v-model="isEmailAlertEnable"
            class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          >
          <label for="email-alerts" class="ml-2 block text-sm text-gray-700">
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
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 text-green-500 mb-6">
          <span class="text-3xl">✓</span>
        </div>
        <h2 class="text-2xl font-bold text-gray-800 mb-2">Urządzenie dodane!</h2>
        <p class="text-gray-600 mb-6">
          Skopiuj poniższy token API. Będzie on potrzebny do połączenia sprzętu z serwerem. Ze względów bezpieczeństwa nie pokażemy go ponownie.
        </p>
        
        <div class="bg-gray-100 p-4 rounded-md font-mono text-lg break-all border border-gray-300 mb-8">
          {{ generatedToken }}
        </div>

        <button @click="router.push('/urzadzenia')" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded transition-colors">
          Przejdź do panelu urządzeń
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../services/api'
import BaseInput from '../components/BaseInput.vue'
import BaseButton from '../components/BaseButton.vue'

const router = useRouter()

const deviceName = ref('')
const deviceLocation = ref('')
const typeOfCultivation = ref('')
const isEmailAlertEnable = ref(false)

// Lista awaryjna (brak endpointu pobierającego typy upraw w FastAPI)
const cultivationTypes = ref([
  { id: 1, name: 'Pomidory' },
  { id: 2, name: 'Ogórki' },
  { id: 3, name: 'Truskawki' }
])

const isLoading = ref(false)
const errorMessage = ref('')
const generatedToken = ref('')

const handleAddDevice = async () => {
  isLoading.value = true
  errorMessage.value = ''

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
      // Wyciągnięcie wygenerowanego tokena ze zwracanego komunikatu backendu
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
</script>