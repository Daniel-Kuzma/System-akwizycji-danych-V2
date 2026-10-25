<template>
  <div class="p-6 max-w-7xl mx-auto space-y-6">
    <h1 class="text-3xl font-bold text-gray-800">Główny Panel Administratora</h1>

    <div class="flex space-x-4 border-b border-gray-200">
      <button 
        @click="activeTab = 'users'"
        :class="activeTab === 'users' ? 'border-b-2 border-blue-600 text-blue-800 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="py-2 px-4 transition-colors text-lg"
      >
        Operacje na użytkownikach
      </button>
      <button 
        @click="activeTab = 'devices'"
        :class="activeTab === 'devices' ? 'border-b-2 border-blue-600 text-blue-800 font-bold' : 'text-gray-500 hover:text-gray-700'"
        class="py-2 px-4 transition-colors text-lg"
      >
        Urządzenia i System Upraw
      </button>
    </div>

    <!-- Renderowanie wybranych komponentów -->
    <AdminUsersTab v-if="activeTab === 'users'" />
    <AdminDevicesTab v-if="activeTab === 'devices'" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AdminUsersTab from '../components/admin/AdminUsersTab.vue'
import AdminDevicesTab from '../components/admin/AdminDevicesTab.vue'

const activeTab = ref('users')
</script>