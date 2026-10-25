<template>
  <div class="p-6 max-w-7xl mx-auto">
    <div class="flex justify-between items-center mb-8">
      <h1 class="text-3xl font-bold text-gray-800">Twoje Urządzenia</h1>
      
      <!-- Przycisk dodawania na górnym pasku widoku -->
      <router-link
        to="/urzadzenia/dodaj"
        class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded transition-colors"
      >
        + Dodaj urządzenie
      </router-link>
    </div>

    <!-- Stan ładowania -->
    <div v-if="isLoading" class="flex justify-center items-center py-20">
      <span class="text-xl text-gray-500">Pobieranie urządzeń...</span>
    </div>

    <!-- Komunikat o błędzie -->
    <div v-else-if="errorMessage" class="text-center py-10 text-red-500 font-medium">
      {{ errorMessage }}
    </div>

    <!-- Główna siatka z urządzeniami -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      
      <!-- Wspomniany przez Ciebie "kwadrat z plusem" - pojawia się, gdy nie masz jeszcze urządzeń -->
      <router-link
        v-if="devices.length === 0"
        to="/urzadzenia/dodaj"
        class="flex flex-col items-center justify-center border-2 border-dashed border-gray-300 rounded-lg p-10 hover:border-blue-500 hover:bg-blue-50 transition-colors cursor-pointer min-h-[200px]"
      >
        <span class="text-5xl text-gray-400 mb-4">+</span>
        <span class="text-gray-600 font-medium text-lg">Dodaj pierwsze urządzenie</span>
      </router-link>

      <!-- Renderowanie właściwych kart urządzeń z API -->
      <div 
        v-for="device in devices" 
        :key="device.public_id"
        class="bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow p-5 flex flex-col"
      >
        <div class="flex justify-between items-start mb-4">
          <h2 class="text-xl font-bold text-gray-800">{{ device.device_name }}</h2>
          <!-- Kolor można potem uzależnić od statusu (np. czerwony dla awarii) -->
          <span class="text-xs font-semibold px-2 py-1 rounded-full bg-green-100 text-green-800">
            {{ device.device_status }}
          </span>
        </div>
        
        <div class="text-sm text-gray-600 space-y-2 mb-6 flex-grow">
          <p><strong>Lokalizacja:</strong> {{ device.device_location }}</p>
          <p><strong>Typ uprawy:</strong> {{ device.name_of_cultivation }}</p>
        </div>

        <button 
          @click="goToDevice(device.public_id)"
          class="w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded transition-colors"
        >
          Przejdź do analizy
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../services/api'

const router = useRouter()
const devices = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

// Pobieranie danych po załadowaniu komponentu
const fetchDevices = async () => {
  isLoading.value = true
  errorMessage.value = ''
  
  try {
    const response = await apiFetch('/device/all-user-device')
    
    if (response.ok) {
      devices.value = await response.json()
    } else {
      errorMessage.value = 'Wystąpił problem podczas pobierania listy urządzeń.'
    }
  } catch (error) {
    errorMessage.value = 'Brak połączenia z serwerem API.'
    console.error('Błąd pobierania urządzeń:', error)
  } finally {
    isLoading.value = false
  }
}

// Nawigacja do konkretnego urządzenia z użyciem jego public_id
const goToDevice = (publicId) => {
  router.push(`/urzadzenia/${publicId}`)
}

// Uruchomienie funkcji natychmiast po wejściu na stronę
onMounted(() => {
  fetchDevices()
})
</script>