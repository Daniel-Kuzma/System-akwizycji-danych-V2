<template>
  <div class="space-y-8">
    <!-- Wyszukiwarka -->
    <div class="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 class="text-xl font-bold mb-4">Szukaj użytkownika</h2>
      <div class="flex gap-4">
        <input v-model="searchQuery.email" type="text" placeholder="Email" class="border p-2 rounded w-full">
        <input v-model="searchQuery.username" type="text" placeholder="Nazwa użytkownika" class="border p-2 rounded w-full">
        <input v-model="searchQuery.public_id" type="text" placeholder="Public ID" class="border p-2 rounded w-full">
        <button @click="searchUser" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">Szukaj</button>
        <button @click="loadUsers" class="bg-gray-200 text-gray-800 px-4 py-2 rounded hover:bg-gray-300">Reset</button>
      </div>
    </div>

    <!-- Tabela użytkowników -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b font-bold text-gray-700">Konta użytkowników</div>
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50 text-xs text-gray-500 uppercase">
          <tr>
            <th class="px-6 py-3 text-left">Dane / Email</th>
            <th class="px-6 py-3 text-left">Public ID</th>
            <th class="px-6 py-3 text-left">Status i Rola</th>
            <th class="px-6 py-3 text-right">Akcje</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 text-sm">
          <tr v-for="u in displayedUsers" :key="u.public_id">
            <td class="px-6 py-4">
              <div class="font-bold">{{ u.name }} {{ u.lastname }}</div>
              <div class="text-gray-500">{{ u.email }} | @{{ u.username }}</div>
            </td>
            <td class="px-6 py-4 text-gray-500 font-mono text-xs">{{ u.public_id }}</td>
            <td class="px-6 py-4">
              <span :class="u.user_role === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-gray-100'" class="px-2 py-1 rounded text-xs mr-2">{{ u.user_role }}</span>
              <span :class="u.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-2 py-1 rounded text-xs">{{ u.is_active ? 'Aktywny' : 'Blokada' }}</span>
            </td>
            <td class="px-6 py-4 text-right space-x-2">
              <button @click="toggleRole(u)" class="text-blue-600 hover:underline">Rola</button>
              <button @click="toggleStatus(u.public_id)" class="text-orange-600 hover:underline">Status</button>
              <button @click="resetPwd(u.public_id)" class="text-yellow-600 hover:underline">Hasło</button>
              <button @click="delUser(u.public_id)" class="text-red-600 hover:underline">Usuń</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Logi Audytowe -->
    <div class="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      <div class="px-6 py-4 bg-gray-50 border-b flex justify-between items-center">
        <span class="font-bold text-gray-700">Dziennik zdarzeń (Audit Logs)</span>
        <div class="flex gap-2">
          <input v-model="logFilter.user_id" placeholder="Filtruj wg User ID" class="border p-1 text-sm rounded">
          <input v-model="logFilter.device_id" placeholder="Filtruj wg Device ID" class="border p-1 text-sm rounded">
          <button @click="loadLogs" class="bg-gray-200 text-sm px-3 py-1 rounded">Odśwież</button>
        </div>
      </div>
      <div class="max-h-64 overflow-y-auto">
        <table class="min-w-full divide-y divide-gray-200 text-sm">
          <thead class="bg-gray-50 text-xs text-gray-500 uppercase sticky top-0">
            <tr>
              <th class="px-6 py-2 text-left">Data</th>
              <th class="px-6 py-2 text-left">Akcja</th>
              <th class="px-6 py-2 text-left">Typ Encji</th>
              <th class="px-6 py-2 text-left">ID Encji</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200">
            <tr v-for="log in logs" :key="log.created_at">
              <td class="px-6 py-2">{{ new Date(log.created_at).toLocaleString() }}</td>
              <td class="px-6 py-2 font-bold">{{ log.action }}</td>
              <td class="px-6 py-2">{{ log.entity_type }}</td>
              <td class="px-6 py-2 font-mono text-xs">{{ log.entity_id }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../../services/api'

const users = ref([])
const displayedUsers = ref([])
const logs = ref([])
const logFilter = ref({ user_id: '', device_id: '' })
const searchQuery = ref({ email: '', username: '', public_id: '' })

const loadUsers = async () => {
  try {
    const res = await apiFetch('/admin/all-users')
    if (res.ok) {
      users.value = await res.json()
      displayedUsers.value = users.value
    }
  } catch (e) { console.error(e) }
}

const searchUser = async () => {
  const { public_id, username, email } = searchQuery.value
  const queryParams = new URLSearchParams()
  if (public_id) queryParams.append('public_id', public_id)
  if (username) queryParams.append('username', username)
  if (email) queryParams.append('email', email)
  
  try {
    const res = await apiFetch(`/admin/user-information?${queryParams.toString()}`)
    if (res.ok) displayedUsers.value = [await res.json()]
    else alert('Nie znaleziono użytkownika.')
  } catch (e) { console.error(e) }
}

const toggleStatus = async (id) => {
  await apiFetch(`/admin/change-user-status/${id}`, { method: 'PUT' })
  loadUsers()
}

const toggleRole = async (user) => {
  const newRole = user.user_role === 'admin' ? 'user' : 'admin'
  await apiFetch(`/admin/change-user-role/${user.public_id}`, { method: 'PUT', body: JSON.stringify({ role: newRole }) })
  loadUsers()
}

const resetPwd = async (id) => {
  const res = await apiFetch(`/admin/reset-user-password/${id}`, { method: 'PUT' })
  if (res.ok) {
    const data = await res.json()
    alert(`Sukces: ${data.message}`)
  }
}

const delUser = async (id) => {
  if (!confirm('Usunąć konto trwale?')) return
  await apiFetch(`/admin/delete-user/${id}`, { method: 'DELETE' })
  loadUsers()
}

const loadLogs = async () => {
  const { user_id, device_id } = logFilter.value
  let url = '/admin/audit-logs'
  const params = new URLSearchParams()
  if (user_id) params.append('user_id_for_logs', user_id)
  if (device_id) params.append('device_public_id', device_id)
  if (params.toString()) url += `?${params.toString()}`

  try {
    const res = await apiFetch(url)
    if (res.ok) logs.value = await res.json()
  } catch (e) { console.error(e) }
}

onMounted(() => {
  loadUsers()
  loadLogs()
})
</script>