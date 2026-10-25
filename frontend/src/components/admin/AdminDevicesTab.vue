<template>
  <div class="space-y-8">
    <!-- Zarządzanie słownikiem upraw -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200">
      <div class="px-6 py-4 bg-gray-50 border-b flex justify-between items-center">
        <span class="font-bold text-gray-700">Słownik Typów Upraw</span>
      </div>
      <div class="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1 border-r pr-6">
          <h3 class="font-bold mb-4">{{ editCultivationMode ? 'Edytuj' : 'Dodaj' }} uprawę</h3>
          <form @submit.prevent="saveCultivation" class="space-y-3 text-sm">
            <input v-model="cultForm.name_of_cultivation" type="text" placeholder="Nazwa uprawy" required class="border p-2 w-full rounded">
            <div class="grid grid-cols-2 gap-2">
              <input v-model.number="cultForm.min_temperature" type="number" step="0.1" placeholder="Min Temp" required class="border p-2 rounded">
              <input v-model.number="cultForm.max_temperature" type="number" step="0.1" placeholder="Max Temp" required class="border p-2 rounded">
              <input v-model.number="cultForm.min_humidity" type="number" step="0.1" placeholder="Min Wilg." required class="border p-2 rounded">
              <input v-model.number="cultForm.max_humidity" type="number" step="0.1" placeholder="Max Wilg." required class="border p-2 rounded">
            </div>
            <div class="flex gap-2">
              <button type="submit" class="bg-green-600 text-white w-full py-2 rounded">Zapisz</button>
              <button v-if="editCultivationMode" @click="resetCultForm" type="button" class="bg-gray-300 px-4 rounded">Anuluj</button>
            </div>
          </form>
        </div>
        <div class="lg:col-span-2 overflow-y-auto max-h-64">
          <table class="min-w-full text-sm">
            <thead class="bg-gray-50 sticky top-0">
              <tr>
                <th class="px-4 py-2 text-left">Nazwa</th>
                <th class="px-4 py-2 text-left">Temp</th>
                <th class="px-4 py-2 text-left">Wilg</th>
                <th class="px-4 py-2 text-right">Akcje</th>
              </tr>
            </thead>
            <tbody class="divide-y">
              <tr v-for="c in cultivations" :key="c.name_of_cultivation">
                <td class="px-4 py-2 font-bold">{{ c.name_of_cultivation }}</td>
                <td class="px-4 py-2">{{ c.min_temperature }}° - {{ c.max_temperature }}°</td>
                <td class="px-4 py-2">{{ c.min_humidity }}% - {{ c.max_humidity }}%</td>
                <td class="px-4 py-2 text-right space-x-2">
                  <button @click="startEditCultivation(c)" class="text-blue-600">Edytuj</button>
                  <button @click="delCultivation(c.name_of_cultivation)" class="text-red-600">Usuń</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Rejestr wszystkich urządzeń -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b flex justify-between items-center">
        <span class="font-bold text-gray-700">Rejestr Urządzeń ESP32</span>
        <input v-model="deviceFilterOwner" placeholder="Filtruj wg Owner ID" class="border p-1 text-sm rounded">
      </div>
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
          <tr>
            <th class="px-6 py-3 text-left">Urządzenie</th>
            <th class="px-6 py-3 text-left">Uprawa</th>
            <th class="px-6 py-3 text-left">Właściciel</th>
            <th class="px-6 py-3 text-right">Akcje Admina</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="d in filteredDevices" :key="d.device_public_id">
            <td class="px-6 py-4">
              <div class="font-bold">{{ d.device_name }}</div>
              <div class="text-gray-500 text-xs">{{ d.device_location }} | ID: {{ d.device_public_id }}</div>
            </td>
            <td class="px-6 py-4">{{ d.name_of_cultivation }}</td>
            <td class="px-6 py-4 font-mono text-xs">{{ d.owner_public_id }}</td>
            <td class="px-6 py-4 text-right space-x-3">
              <button @click="openDeviceManager(d.device_public_id)" class="text-blue-600 font-bold">Zarządzaj</button>
              <button @click="delDevice(d.device_public_id)" class="text-red-600">Usuń</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal Urządzenia -->
    <div v-if="selectedDevice" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div class="bg-white rounded-lg shadow-xl w-full max-w-4xl p-6 space-y-6">
        <div class="flex justify-between items-center border-b pb-4">
          <h2 class="text-2xl font-bold">Zarządzanie urządzeniem: {{ selectedDevice }}</h2>
          <button @click="selectedDevice = null" class="text-gray-500 text-xl font-bold">&times;</button>
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div class="border p-4 rounded bg-gray-50">
            <h3 class="font-bold mb-2">Tokeny API</h3>
            <div class="max-h-32 overflow-y-auto text-xs bg-white border">
              <table class="min-w-full divide-y">
                <tbody class="divide-y">
                  <tr v-for="t in deviceTokens" :key="t.hashed_token">
                    <td class="p-2 break-all">{{ t.hashed_token }}</td>
                    <td class="p-2 text-center"><span :class="t.is_active ? 'text-green-600' : 'text-red-600'" class="font-bold">{{ t.is_active ? 'ON' : 'OFF' }}</span></td>
                  </tr>
                </tbody>
              </table>
            </div>
            <button @click="toggleToken(selectedDevice)" class="mt-2 bg-yellow-500 text-white px-3 py-1 rounded text-sm w-full">Zmień status obecnego tokena</button>
          </div>
          <div class="border p-4 rounded bg-gray-50">
             <h3 class="font-bold mb-2">Kontrola analizy</h3>
              <div class="flex gap-2 text-sm">
                <button @click="triggerAnalysis('start')" class="bg-green-600 text-white px-3 py-1 rounded w-full">Wymuś Start</button>
                <button @click="triggerAnalysis('end')" class="bg-red-600 text-white px-3 py-1 rounded w-full">Wymuś Stop</button>
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
const editCultivationMode = ref(false)
const originalCultivationName = ref('')
const cultForm = ref({ name_of_cultivation: '', min_temperature: null, max_temperature: null, min_humidity: null, max_humidity: null })

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
    const res = await apiFetch('/admin/show-all-cultivation')
    if (res.ok) cultivations.value = await res.json()
  } catch (e) { console.error(e) }
}

const resetCultForm = () => {
  cultForm.value = { name_of_cultivation: '', min_temperature: null, max_temperature: null, min_humidity: null, max_humidity: null }
  editCultivationMode.value = false
}

const startEditCultivation = (c) => {
  cultForm.value = { ...c }
  originalCultivationName.value = c.name_of_cultivation
  editCultivationMode.value = true
}

const saveCultivation = async () => {
  try {
    let res
    if (editCultivationMode.value) {
      res = await apiFetch(`/admin/change-cultivation/${originalCultivationName.value}`, { method: 'PUT', body: JSON.stringify(cultForm.value) })
    } else {
      res = await apiFetch('/admin/add-new-cultivation', { method: 'POST', body: JSON.stringify(cultForm.value) })
    }
    if (res.ok) { resetCultForm(); loadCultivations() }
  } catch (e) { console.error(e) }
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