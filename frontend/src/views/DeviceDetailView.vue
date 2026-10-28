<template>
  <div class="p-6 max-w-7xl mx-auto">
    <button @click="router.push('/urzadzenia')" class="text-blue-600 dark:text-blue-400 hover:underline mb-6 flex items-center gap-2 transition-colors">
      &larr; Wróć do listy urządzeń
    </button>

    <div v-if="isLoadingData" class="py-10 text-gray-500 dark:text-custom-muted font-medium text-center">Ładowanie interfejsu urządzenia...</div>
    <div v-else-if="errorMessage" class="py-10 text-red-500 font-medium text-center">{{ errorMessage }}</div>
    
    <div v-else>
      <!-- Nagłówek -->
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 border-b border-gray-200 dark:border-custom-border pb-4 gap-4 transition-colors">
        <div>
          <h1 class="text-3xl font-bold text-gray-800 dark:text-custom-light">{{ device.device_name }}</h1>
          <p class="text-gray-600 dark:text-custom-muted mt-1">Lokalizacja: {{ device.device_location }} | Uprawa: {{ device.name_of_cultivation }}</p>
        </div>
        
        <button 
          @click="router.push(`/urzadzenia/${deviceId}/ustawienia`)"
          class="bg-gray-100 dark:bg-custom-dark hover:bg-gray-200 dark:hover:bg-gray-800 text-gray-800 dark:text-custom-light border border-transparent dark:border-custom-border font-semibold py-2 px-4 rounded transition-colors"
        >
          ⚙️ Ustawienia urządzenia
        </button>
      </div>

      <!-- Karty analityczne (Procent optymalnych warunków) -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border flex items-center justify-between transition-colors">
          <div>
            <p class="text-sm text-gray-500 dark:text-custom-muted font-medium mb-1">Optymalna temperatura</p>
            <p class="text-3xl font-bold text-red-500">{{ tempAnalysisPercentage }}%</p>
          </div>
          <div class="text-4xl">🌡️</div>
        </div>
        <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border flex items-center justify-between transition-colors">
          <div>
            <p class="text-sm text-gray-500 dark:text-custom-muted font-medium mb-1">Optymalna wilgotność</p>
            <p class="text-3xl font-bold text-blue-500">{{ humAnalysisPercentage }}%</p>
          </div>
          <div class="text-4xl">💧</div>
        </div>
      </div>

      <!-- Panel Telemetrii -->
      <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border mb-8 transition-colors">
        <div class="flex justify-between items-center mb-6">
          <h2 class="text-xl font-bold text-gray-800 dark:text-custom-light">Historia pomiarów</h2>
          
          <select 
            v-model="selectedTimeRange" 
            @change="fetchTelemetry"
            class="border border-gray-300 dark:border-custom-border bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light rounded-md p-2 text-sm focus:ring-blue-500 focus:border-blue-500 transition-colors"
          >
            <option value="LAST_HOUR">Ostatnia godzina</option>
            <option value="LAST_HALF_DAY">Ostatnie 12 godzin</option>
            <option value="LAST_DAY">Ostatni dzień</option>
            <option value="LAST_WEEK">Ostatni tydzień</option>
            <option value="LAST_MONTH">Ostatni miesiąc</option>
          </select>
        </div>

        <div v-if="isFetchingTelemetry" class="flex justify-center items-center h-64 text-gray-400 dark:text-custom-muted">
          Odświeżanie wykresu...
        </div>
        <div v-else-if="chartSeries[0].data.length === 0" class="flex justify-center items-center h-64 text-gray-400 dark:text-custom-muted">
          Brak danych telemetrycznych w wybranym okresie.
        </div>
        <div v-else class="w-full">
          <!-- Wykres podpięty pod dynamiczne computedChartOptions -->
          <VueApexCharts 
            type="area" 
            height="400" 
            :options="computedChartOptions" 
            :series="chartSeries" 
          />
        </div>
      </div>
      
      <!-- Akcje zarządzania analizą -->
      <div class="flex gap-4">
        <button 
          @click="startNewAnalysis"
          :disabled="isTogglingAnalysis"
          class="bg-green-600 dark:bg-green-700 text-white px-4 py-2 rounded font-semibold hover:bg-green-700 dark:hover:bg-green-600 transition-colors disabled:opacity-50"
        >
          Rozpocznij nową analizę
        </button>
        <button 
          @click="endCurrentAnalysis"
          :disabled="isTogglingAnalysis"
          class="bg-red-600 dark:bg-red-700 text-white px-4 py-2 rounded font-semibold hover:bg-red-700 dark:hover:bg-red-600 transition-colors disabled:opacity-50"
        >
          Zakończ obecną analizę
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, onUnmounted } from 'vue'
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

// Obserwator motywu dla ApexCharts
const isDarkMode = ref(false)
let themeObserver = null

// Dynamiczne opcje wykresu (reagujące na isDarkMode)
const computedChartOptions = computed(() => {
  return {
    chart: { 
      type: 'area', 
      animations: { enabled: false },
      toolbar: { show: true },
      background: 'transparent' // Zapobiega nadpisywaniu tła
    },
    theme: {
      mode: isDarkMode.value ? 'dark' : 'light' // Wbudowany tryb ciemny ApexCharts
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
    colors: ['#EF4444', '#3B82F6'],
    fill: {
      type: 'gradient',
      gradient: { shadeIntensity: 1, opacityFrom: 0.3, opacityTo: 0.05, stops: [0, 100] }
    },
    tooltip: { 
      theme: isDarkMode.value ? 'dark' : 'light',
      x: { format: 'dd MMM yyyy HH:mm:ss' } 
    }
  }
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
  // Nasłuchiwanie zmian motywu z poziomu paska nawigacji / systemu
  isDarkMode.value = document.documentElement.classList.contains('dark')
  themeObserver = new MutationObserver(() => {
    isDarkMode.value = document.documentElement.classList.contains('dark')
  })
  themeObserver.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] })

  await fetchDeviceDetails()
  if (device.value) {
    fetchAnalyses()
    fetchTelemetry()
  }
  isLoadingData.value = false
})

onUnmounted(() => {
  if (themeObserver) themeObserver.disconnect()
})
</script>