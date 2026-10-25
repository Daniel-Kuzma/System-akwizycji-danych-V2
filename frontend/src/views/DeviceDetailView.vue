<template>
  <div class="p-6 max-w-7xl mx-auto">
    <button @click="router.push('/urzadzenia')" class="text-blue-600 hover:underline mb-6 flex items-center gap-2">
      &larr; Wróć do listy urządzeń
    </button>

    <div v-if="isLoadingData" class="py-10 text-gray-500 font-medium">Ładowanie interfejsu urządzenia...</div>
    <div v-else-if="errorMessage" class="py-10 text-red-500 font-medium">{{ errorMessage }}</div>
    
    <div v-else>
      <!-- Nagłówek -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b border-gray-200 pb-4 gap-4">
        <div>
          <h1 class="text-3xl font-bold text-gray-800">{{ device.device_name }}</h1>
          <p class="text-gray-600 mt-1">Lokalizacja: {{ device.device_location }} | Uprawa: {{ device.name_of_cultivation }}</p>
        </div>
        
        <button 
          @click="router.push(`/urzadzenia/${deviceId}/ustawienia`)"
          class="bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded transition-colors"
        >
          ⚙️ Ustawienia urządzenia
        </button>
      </div>

      <!-- Karty analityczne (Procent optymalnych warunków) -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 font-medium mb-1">Optymalna temperatura</p>
            <p class="text-3xl font-bold text-red-500">{{ tempAnalysisPercentage }}%</p>
          </div>
          <div class="text-4xl">🌡️</div>
        </div>
        <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500 font-medium mb-1">Optymalna wilgotność</p>
            <p class="text-3xl font-bold text-blue-500">{{ humAnalysisPercentage }}%</p>
          </div>
          <div class="text-4xl">💧</div>
        </div>
      </div>

      <!-- Panel Telemetrii -->
      <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200 mb-8">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-gray-800">Historia pomiarów</h2>
          
          <select 
            v-model="selectedTimeRange" 
            @change="fetchTelemetry"
            class="border border-gray-300 rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="LAST_HOUR">Ostatnia godzina</option>
            <option value="LAST_HALF_DAY">Ostatnie 12 godzin</option>
            <option value="LAST_DAY">Ostatni dzień</option>
            <option value="LAST_WEEK">Ostatni tydzień</option>
            <option value="LAST_MONTH">Ostatni miesiąc</option>
          </select>
        </div>

        <div v-if="isFetchingTelemetry" class="flex justify-center items-center h-64 text-gray-400">
          Odświeżanie wykresu...
        </div>
        <div v-else-if="chartSeries[0].data.length === 0" class="flex justify-center items-center h-64 text-gray-400">
          Brak danych telemetrycznych w wybranym okresie.
        </div>
        <div v-else class="w-full">
          <VueApexCharts 
            type="area" 
            height="400" 
            :options="chartOptions" 
            :series="chartSeries" 
          />
        </div>
      </div>
      
      <!-- Akcje zarządzania analizą -->
      <div class="flex gap-4">
        <button 
          @click="startNewAnalysis"
          :disabled="isTogglingAnalysis"
          class="bg-green-600 text-white px-4 py-2 rounded font-semibold hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          Rozpocznij nową analizę
        </button>
        <button 
          @click="endCurrentAnalysis"
          :disabled="isTogglingAnalysis"
          class="bg-red-600 text-white px-4 py-2 rounded font-semibold hover:bg-red-700 transition-colors disabled:opacity-50"
        >
          Zakończ obecną analizę
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch } from '../services/api'
import VueApexCharts from 'vue3-apexcharts'

const route = useRoute()
const router = useRouter()
const deviceId = route.params.id

// Stan urządzenia
const device = ref(null)
const isLoadingData = ref(true)
const errorMessage = ref('')

// Stan analityki
const tempAnalysisPercentage = ref(0)
const humAnalysisPercentage = ref(0)
const isTogglingAnalysis = ref(false)

// Stan telemetrii i wykresu
const selectedTimeRange = ref('LAST_HOUR')
const isFetchingTelemetry = ref(false)
const chartSeries = ref([
  { name: 'Temperatura (°C)', data: [] },
  { name: 'Wilgotność (%)', data: [] }
])

const chartOptions = ref({
  chart: { 
    type: 'area', 
    animations: { enabled: false }, // Wyłączone dla wydajności przy dużej liczbie punktów
    toolbar: { show: true } 
  },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth', width: 2 },
  xaxis: { 
    type: 'datetime',
    tooltip: { enabled: false }
  },
  yaxis: [
    { 
      title: { text: 'Temperatura (°C)' }, 
      labels: { formatter: (val) => val.toFixed(1) },
      tickAmount: 5
    },
    { 
      opposite: true, 
      title: { text: 'Wilgotność (%)' }, 
      labels: { formatter: (val) => val.toFixed(1) },
      tickAmount: 5
    }
  ],
  colors: ['#EF4444', '#3B82F6'], // Czerwony dla temp, Niebieski dla wilgotności
  fill: {
    type: 'gradient',
    gradient: { shadeIntensity: 1, opacityFrom: 0.3, opacityTo: 0.05, stops: [0, 100] }
  },
  tooltip: { x: { format: 'dd MMM yyyy HH:mm:ss' } }
})

const fetchDeviceDetails = async () => {
  try {
    const response = await apiFetch(`/device/user-device/${deviceId}`)
    if (response.ok) {
      device.value = await response.json()
    } else {
      errorMessage.value = 'Nie udało się pobrać informacji o urządzeniu.'
    }
  } catch (error) {
    errorMessage.value = 'Brak połączenia z serwerem API.'
  }
}

const fetchAnalyses = async () => {
  try {
    const [tempRes, humRes] = await Promise.all([
      apiFetch(`/telemetry/get-cultivation-temperature-analyses/${deviceId}`),
      apiFetch(`/telemetry/get-cultivation-humidity-analyses/${deviceId}`)
    ])
    
    if (tempRes.ok) {
      const tempData = await tempRes.json()
      tempAnalysisPercentage.value = tempData.percentage
    }
    if (humRes.ok) {
      const humData = await humRes.json()
      humAnalysisPercentage.value = humData.percentage
    }
  } catch (error) {
    console.error('Błąd pobierania analiz:', error)
  }
}

const fetchTelemetry = async () => {
  isFetchingTelemetry.value = true
  try {
    const response = await apiFetch(`/telemetry/get-data-based-on-selected-time-period/${deviceId}?time=${selectedTimeRange.value}`)
    if (response.ok) {
      const data = await response.json()
      
      // Mapowanie danych z backendu do formatu wymaganego przez ApexCharts [timestamp, value]
      const tempData = data.map(item => [new Date(item.created_at).getTime(), item.temperature_reading])
      const humData = data.map(item => [new Date(item.created_at).getTime(), item.humidity_reading])
      
      chartSeries.value = [
        { name: 'Temperatura (°C)', data: tempData },
        { name: 'Wilgotność (%)', data: humData }
      ]
    }
  } catch (error) {
    console.error('Błąd pobierania telemetrii:', error)
  } finally {
    isFetchingTelemetry.value = false
  }
}

const startNewAnalysis = async () => {
  isTogglingAnalysis.value = true
  try {
    const response = await apiFetch(`/device/start-new-cultivation-analysis-by-user/${deviceId}`, { method: 'POST' })
    if (response.ok) {
      alert('Rozpoczęto nową analizę.')
      await fetchAnalyses()
    } else {
      const data = await response.json()
      alert(data.detail || 'Błąd rozpoczynania analizy.')
    }
  } finally {
    isTogglingAnalysis.value = false
  }
}

const endCurrentAnalysis = async () => {
  isTogglingAnalysis.value = true
  try {
    const response = await apiFetch(`/device/end-cultivation-analysis-by-user/${deviceId}`, { method: 'PUT' })
    if (response.ok) {
      alert('Zakończono obecną analizę.')
    } else {
      const data = await response.json()
      alert(data.detail || 'Błąd kończenia analizy.')
    }
  } finally {
    isTogglingAnalysis.value = false
  }
}

onMounted(async () => {
  await fetchDeviceDetails()
  if (device.value) {
    fetchAnalyses()
    fetchTelemetry()
  }
  isLoadingData.value = false
})
</script>