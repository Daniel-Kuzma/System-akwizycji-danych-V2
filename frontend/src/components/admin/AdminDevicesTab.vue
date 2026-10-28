<template>
  <div class="space-y-8">
    <!-- Zarządzanie słownikiem upraw -->
    <div class="bg-white dark:bg-custom-card rounded-lg shadow-sm border border-gray-200 dark:border-custom-border transition-colors">
      <div class="px-6 py-4 bg-gray-50 dark:bg-custom-dark border-b border-gray-200 dark:border-custom-border flex justify-between items-center transition-colors">
        <span class="font-bold text-gray-700 dark:text-custom-light">Słownik Typów Upraw</span>
        <input 
          v-model="cultivationSearchQuery" 
          placeholder="Szukaj uprawy..." 
          class="border border-gray-300 dark:border-custom-border p-1 px-3 text-sm rounded bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors"
        >
      </div>
      <div class="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1 border-r border-gray-200 dark:border-custom-border pr-6 transition-colors">
          <h3 class="font-bold mb-4 text-gray-800 dark:text-custom-light">{{ editCultivationMode ? 'Edytuj' : 'Dodaj' }} uprawę</h3>
          
          <form @submit.prevent="saveCultivation" class="space-y-3 text-sm">
            <input v-model="cultForm.name_of_cultivation" type="text" placeholder="Nazwa uprawy" required class="border border-gray-300 dark:border-custom-border p-2 w-full rounded bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
            <div class="grid grid-cols-2 gap-2">
              <input v-model.number="cultForm.min_temperature" type="number" step="0.1" placeholder="Min Temp" required class="border border-gray-300 dark:border-custom-border p-2 rounded bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
              <input v-model.number="cultForm.max_temperature" type="number" step="0.1" placeholder="Max Temp" required class="border border-gray-300 dark:border-custom-border p-2 rounded bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
              <input v-model.number="cultForm.min_humidity" type="number" step="0.1" placeholder="Min Wilg. (%)" required class="border border-gray-300 dark:border-custom-border p-2 rounded bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
              <input v-model.number="cultForm.max_humidity" type="number" step="0.1" placeholder="Max Wilg. (%)" required class="border border-gray-300 dark:border-custom-border p-2 rounded bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
            </div>

            <!-- Komunikaty walidacji / serwera -->
            <div v-if="formMessage" :class="formMessage.isError ? 'text-red-500 dark:text-red-400' : 'text-green-600 dark:text-green-400'" class="text-xs font-semibold py-1">
              {{ formMessage.text }}
            </div>

            <div class="flex gap-2 pt-2">
              <button type="submit" class="bg-green-600 dark:bg-green-700 hover:bg-green-700 dark:hover:bg-green-600 text-white w-full py-2 rounded transition-colors">Zapisz</button>
              <button v-if="editCultivationMode" @click="resetCultForm" type="button" class="bg-gray-300 dark:bg-custom-dark text-gray-800 dark:text-custom-light border border-transparent dark:border-custom-border px-4 rounded transition-colors hover:bg-gray-400 dark:hover:bg-gray-800">Anuluj</button>
            </div>
          </form>
        </div>
        
        <div class="lg:col-span-2 overflow-y-auto max-h-64">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50 dark:bg-custom-dark sticky top-0 transition-colors">
              <tr class="text-gray-700 dark:text-custom-muted">
                <th class="px-4 py-2 text-left">Nazwa</th>
                <th class="px-4 py-2 text-left">Temp</th>
                <th class="px-4 py-2 text-left">Wilg</th>
                <th class="px-4 py-2 text-right">Akcje</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-custom-border text-gray-800 dark:text-custom-light transition-colors">
              <tr v-for="c in filteredCultivations" :key="c.name_of_cultivation">
                <td class="px-4 py-2 font-bold">{{ c.name_of_cultivation }}</td>
                <td class="px-4 py-2">{{ c.min_temperature }}° - {{ c.max_temperature }}°</td>
                <td class="px-4 py-2">{{ c.min_humidity }}% - {{ c.max_humidity }}%</td>
                <td class="px-4 py-2 text-right space-x-2">
                  <button @click="startEditCultivation(c)" class="text-blue-600 dark:text-blue-400 hover:underline">Edytuj</button>
                  <button @click="delCultivation(c.name_of_cultivation)" class="text-red-600 dark:text-red-400 hover:underline">Usuń</button>
                </td>
              </tr>
              <tr v-if="filteredCultivations.length === 0">
                <td colspan="4" class="px-4 py-4 text-center text-gray-500 dark:text-custom-muted italic">Brak upraw pasujących do wyszukiwania</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Rejestr wszystkich urządzeń -->
    <div class="bg-white dark:bg-custom-card rounded-lg shadow-sm border border-gray-200 dark:border-custom-border overflow-hidden transition-colors">
      <div class="px-6 py-4 bg-gray-50 dark:bg-custom-dark border-b border-gray-200 dark:border-custom-border flex justify-between items-center transition-colors">
        <span class="font-bold text-gray-700 dark:text-custom-light">Rejestr Urządzeń ESP32</span>
        <input v-model="deviceFilterOwner" placeholder="Filtruj wg Owner ID" class="border border-gray-300 dark:border-custom-border p-1 text-sm rounded bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
      </div>
      <table class="min-w-full divide-y divide-gray-200 dark:divide-custom-border">
        <thead class="bg-gray-50 dark:bg-custom-dark text-xs text-gray-500 dark:text-custom-muted uppercase transition-colors">
          <tr>
            <th class="px-6 py-3 text-left">Urządzenie</th>
            <th class="px-6 py-3 text-left">Uprawa</th>
            <th class="px-6 py-3 text-left">Właściciel</th>
            <th class="px-6 py-3 text-right">Akcje Admina</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-custom-border text-sm transition-colors">
          <tr v-for="d in filteredDevices" :key="d.device_public_id">
            <td class="px-6 py-4">
              <div class="font-bold text-gray-800 dark:text-custom-light">{{ d.device_name }}</div>
              <div class="text-gray-500 dark:text-custom-muted text-xs">{{ d.device_location }} | ID: {{ d.device_public_id }}</div>
            </td>
            <td class="px-6 py-4 text-gray-800 dark:text-custom-light">{{ d.name_of_cultivation }}</td>
            <td class="px-6 py-4 font-mono text-xs text-gray-800 dark:text-custom-light">{{ d.owner_public_id }}</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openDeviceManager(d.device_public_id)" class="text-blue-600 dark:text-blue-400 font-bold hover:underline">Zarządzaj</button>
              <button @click="delDevice(d.device_public_id)" class="text-red-600 dark:text-red-400 hover:underline">Usuń</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Urządzenia -->
    <div v-if="selectedDevice" class="fixed inset-0 bg-black bg-opacity-50 dark:bg-opacity-70 flex items-center justify-center p-4 z-50 transition-colors">
      <div class="bg-white dark:bg-custom-card rounded-lg shadow-xl w-full max-w-4xl p-6 space-y-6 border border-transparent dark:border-custom-border">
        <div class="flex justify-between items-center border-b border-gray-200 dark:border-custom-border pb-4">
          <h2 class="text-2xl font-bold text-gray-800 dark:text-custom-light">Zarządzanie urządzeniem: {{ selectedDevice }}</h2>
          <button @click="selectedDevice = null" class="text-gray-500 dark:text-custom-muted hover:text-gray-800 dark:hover:text-custom-light text-xl font-bold transition-colors">&times;</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="border border-gray-200 dark:border-custom-border p-4 rounded bg-gray-50 dark:bg-custom-dark transition-colors">
            <h3 class="font-bold mb-2 text-gray-800 dark:text-custom-light">Tokeny API</h3>
            <div class="max-h-32 overflow-y-auto text-xs bg-white dark:bg-custom-card border border-gray-200 dark:border-custom-border transition-colors">
              <table class="min-w-full divide-y divide-gray-200 dark:divide-custom-border text-gray-800 dark:text-custom-light">
                <tbody class="divide-y divide-gray-200 dark:divide-custom-border">
                  <tr v-for="t in deviceTokens" :key="t.hashed_token">
                    <td class="p-2 break-all">{{ t.hashed_token }}</td>
                    <td class="p-2 text-center"><span :class="t.is_active ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'" class="font-bold">{{ t.is_active ? 'ON' : 'OFF' }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <button @click="toggleToken(selectedDevice)" class="mt-2 bg-yellow-500 dark:bg-yellow-600 hover:bg-yellow-600 dark:hover:bg-yellow-500 text-white px-3 py-1 rounded text-sm w-full transition-colors">Zmień status obecnego tokena</button>
          </div>
          <div class="border border-gray-200 dark:border-custom-border p-4 rounded bg-gray-50 dark:bg-custom-dark transition-colors">
             <h3 class="font-bold mb-2 text-gray-800 dark:text-custom-light">Kontrola analizy</h3>
              <div class="flex gap-2 text-sm">
                <button @click="triggerAnalysis('start')" class="bg-green-600 dark:bg-green-700 hover:bg-green-700 dark:hover:bg-green-600 text-white px-3 py-1 rounded w-full transition-colors">Wymuś Start</button>
                <button @click="triggerAnalysis('end')" class="bg-red-600 dark:bg-red-700 hover:bg-red-700 dark:hover:bg-red-600 text-white px-3 py-1 rounded w-full transition-colors">Wymuś Stop</button>
              </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '../../services/api'

const cultivations = ref([])
const cultivationSearchQuery = ref('') 
const editCultivationMode = ref(false)
const originalCultivationName = ref('')
const cultForm = ref({ name_of_cultivation: '', min_temperature: null, max_temperature: null, min_humidity: null, max_humidity: null })

// Stan na komunikaty walidacji/serwera
const formMessage = ref(null) 

const filteredCultivations = computed(() => {
  if (!cultivationSearchQuery.value) return cultivations.value
  const q = cultivationSearchQuery.value.toLowerCase()
  return cultivations.value.filter(c => 
    c.name_of_cultivation.toLowerCase().includes(q)
  )
})

const devices = ref([])
const deviceFilterOwner = ref('')
const filteredDevices = computed(() => {
  if (!deviceFilterOwner.value) return devices.value
  return devices.value.filter(d => d.owner_public_id.includes(deviceFilterOwner.value))
})

const selectedDevice = ref(null)
const deviceTokens = ref([])

const loadCultivations = async () => {
  try {
    const res = await apiFetch('/cultivation/all-expended-cultivation')
    if (res.ok) cultivations.value = await res.json()
  } catch (e) { console.error(e) }
}

const resetCultForm = () => {
  cultForm.value = { name_of_cultivation: '', min_temperature: null, max_temperature: null, min_humidity: null, max_humidity: null }
  editCultivationMode.value = false
  formMessage.value = null
}

const startEditCultivation = (c) => {
  cultForm.value = { ...c }
  originalCultivationName.value = c.name_of_cultivation
  editCultivationMode.value = true
  formMessage.value = null
}

// Funkcja zapisywania z dodaną logiką walidacji i obsługi błędów
const saveCultivation = async () => {
  formMessage.value = null
  
  // Walidacja logiczna przed wysłaniem na serwer
  if (cultForm.value.min_temperature >= cultForm.value.max_temperature) {
    formMessage.value = { text: 'Temperatura minimalna musi być mniejsza od maksymalnej.', isError: true }
    return
  }
  if (cultForm.value.min_humidity >= cultForm.value.max_humidity) {
    formMessage.value = { text: 'Wilgotność minimalna musi być mniejsza od maksymalnej.', isError: true }
    return
  }
  if (cultForm.value.min_humidity < 0 || cultForm.value.max_humidity > 100) {
    formMessage.value = { text: 'Wilgotność musi mieścić się w przedziale od 0 do 100%.', isError: true }
    return
  }

  try {
    let res
    if (editCultivationMode.value) {
      res = await apiFetch(`/admin/change-cultivation/${originalCultivationName.value}`, { method: 'PUT', body: JSON.stringify(cultForm.value) })
    } else {
      res = await apiFetch('/admin/add-new-cultivation', { method: 'POST', body: JSON.stringify(cultForm.value) })
    }
    
    // Obsługa odpowiedzi serwera
    if (res.ok) {
      formMessage.value = { text: 'Uprawa zapisana pomyślnie!', isError: false }
      resetCultForm()
      loadCultivations()
      setTimeout(() => { formMessage.value = null }, 3000)
    } else {
      const data = await res.json()
      let errorText = 'Wystąpił błąd podczas zapisywania.'

      // Jeśli backend zwraca zwykły tekst
      if (typeof data.detail === 'string') {
        errorText = data.detail
      } 
      // Jeśli backend zwraca listę błędów walidacji Pydantic (FastAPI 422)
      else if (Array.isArray(data.detail)) {
        const fieldMap = {
          name_of_cultivation: 'Nazwa uprawy',
          min_temperature: 'Temperatura minimalna',
          max_temperature: 'Temperatura maksymalna',
          min_humidity: 'Wilgotność minimalna',
          max_humidity: 'Wilgotność maksymalna'
        }

        errorText = data.detail.map(err => {
          // Wyciągamy nazwę pola z "loc" (np. ["body", "max_temperature"])
          const field = err.loc && err.loc.length > 0 ? err.loc[err.loc.length - 1] : 'Pole'
          const plField = fieldMap[field] || field

          // Tłumaczenie surowych typów błędów na język ludzki
          if (err.type === 'less_than') return `${plField} musi być mniejsza niż ${err.ctx.lt}.`
          if (err.type === 'greater_than') return `${plField} musi być większa niż ${err.ctx.gt}.`
          if (err.type === 'less_than_equal') return `${plField} nie może przekraczać ${err.ctx.le}.`
          if (err.type === 'greater_than_equal') return `${plField} musi wynosić co najmniej ${err.ctx.ge}.`
          
          return `${plField}: wprowadzono nieprawidłowe dane.`
        }).join(' | ') // Łączymy błędy, jeśli jest ich więcej niż jeden
      }

      formMessage.value = { text: errorText, isError: true }
    }
  } catch (e) {
    formMessage.value = { text: 'Brak połączenia z serwerem API.', isError: true }
    console.error(e)
  }
}

const delCultivation = async (name) => {
  if (!confirm('Usunąć ten typ uprawy?')) return
  await apiFetch(`/admin/delete-cultivation/${name}`, { method: 'DELETE' })
  loadCultivations()
}

const loadDevices = async () => {
  try {
    const res = await apiFetch('/admin/get-all-register-device')
    if (res.ok) devices.value = await res.json()
  } catch (e) { console.error(e) }
}

const delDevice = async (id) => {
  if (!confirm('Usunąć urządzenie na zawsze?')) return
  await apiFetch(`/admin/delete-register-device/${id}`, { method: 'DELETE' })
  loadDevices()
}

const openDeviceManager = async (id) => {
  selectedDevice.value = id
  await fetchTokens(id)
}

const fetchTokens = async (id) => {
  const res = await apiFetch(`/admin/get-all-device-tokens/${id}`)
  if (res.ok) deviceTokens.value = await res.json()
}

const toggleToken = async (id) => {
  await apiFetch(`/admin/change-status-of-device-communication-token/${id}`, { method: 'PUT' })
  fetchTokens(id)
}

const triggerAnalysis = async (action) => {
  const url = action === 'start' ? `/admin/start-new-cultivation-analysis/${selectedDevice.value}` : `/admin/end-cultivation-analysis/${selectedDevice.value}`
  const method = action === 'start' ? 'POST' : 'PUT'
  const res = await apiFetch(url, { method })
  if (res.ok) alert(`Akcja analizy wykonana.`)
}

onMounted(() => {
  loadCultivations()
  loadDevices()
})
</script>