<template>
  <div class="space-y-8">
    <!-- Wyszukiwarka -->
    <div class="bg-white dark:bg-custom-card p-6 rounded-lg shadow-sm border border-gray-200 dark:border-custom-border transition-colors">
      <h2 class="text-xl font-bold mb-4 text-gray-800 dark:text-custom-light">Szukaj użytkownika</h2>
      <div class="flex flex-wrap md:flex-nowrap gap-4">
        <input v-model="searchQuery.email" type="text" placeholder="Email" class="border border-gray-300 dark:border-custom-border p-2 rounded w-full bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
        <input v-model="searchQuery.username" type="text" placeholder="Nazwa użytkownika" class="border border-gray-300 dark:border-custom-border p-2 rounded w-full bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
        <input v-model="searchQuery.public_id" type="text" placeholder="Public ID" class="border border-gray-300 dark:border-custom-border p-2 rounded w-full bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light transition-colors">
        <button @click="searchUser" class="bg-blue-600 dark:bg-blue-700 text-white px-4 py-2 rounded hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors w-full md:w-auto">Szukaj</button>
        <button @click="loadUsers" class="bg-gray-200 dark:bg-custom-dark text-gray-800 dark:text-custom-light border border-transparent dark:border-custom-border px-4 py-2 rounded hover:bg-gray-300 dark:hover:bg-gray-800 transition-colors w-full md:w-auto">Reset</button>
      </div>
    </div>

    <!-- Tabela użytkowników -->
    <div class="bg-white dark:bg-custom-card rounded-lg shadow-sm border border-gray-200 dark:border-custom-border overflow-hidden transition-colors">
      <div class="px-6 py-4 bg-gray-50 dark:bg-custom-dark border-b border-gray-200 dark:border-custom-border font-bold text-gray-700 dark:text-custom-light transition-colors">Konta użytkowników</div>
      <table class="min-w-full divide-y divide-gray-200 dark:divide-custom-border">
        <thead class="bg-gray-50 dark:bg-custom-dark text-xs text-gray-500 dark:text-custom-muted uppercase transition-colors">
          <tr>
            <th class="px-6 py-3 text-left">Dane / Email</th>
            <th class="px-6 py-3 text-left">Public ID</th>
            <th class="px-6 py-3 text-left">Status i Rola</th>
            <th class="px-6 py-3 text-right">Akcje</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 dark:divide-custom-border text-sm transition-colors">
          <tr v-for="u in displayedUsers" :key="u.public_id">
            <td class="px-6 py-4">
              <div class="font-bold text-gray-800 dark:text-custom-light">{{ u.name }} {{ u.lastname }}</div>
              <div class="text-gray-500 dark:text-custom-muted">{{ u.email }} | {{ u.username }}</div>
            </td>
            <td class="px-6 py-4 text-gray-500 dark:text-custom-muted font-mono text-xs">{{ u.public_id }}</td>
            <td class="px-6 py-4">
              <span :class="u.user_role === 'admin' ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300' : 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300'" class="px-2 py-1 rounded text-xs mr-2 transition-colors">{{ u.user_role }}</span>
              <span :class="u.is_active ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400' : 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400'" class="px-2 py-1 rounded text-xs transition-colors">{{ u.is_active ? 'Aktywny' : 'Blokada' }}</span>
            </td>
            <td class="px-6 py-4 text-right space-x-2">
              <button @click="toggleRole(u)" class="text-blue-600 dark:text-blue-400 hover:underline">Rola</button>
              <button @click="toggleStatus(u.public_id)" class="text-orange-600 dark:text-orange-400 hover:underline">Status</button>
              <button @click="resetPwd(u.public_id)" class="text-yellow-600 dark:text-yellow-500 hover:underline">Hasło</button>
              <button @click="delUser(u.public_id)" class="text-red-600 dark:text-red-400 hover:underline">Usuń</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Logi Audytowe -->
    <div class="bg-white dark:bg-custom-card rounded-lg shadow-sm border border-gray-200 dark:border-custom-border overflow-hidden transition-colors">
      <div class="px-6 py-4 bg-gray-50 dark:bg-custom-dark border-b border-gray-200 dark:border-custom-border flex justify-between items-center transition-colors">
        <span class="font-bold text-gray-700 dark:text-custom-light">Dziennik zdarzeń (Audit Logs)</span>
        <div class="flex gap-2">
          <input v-model="logFilter.user_id" placeholder="Filtruj wg User ID" class="border border-gray-300 dark:border-custom-border bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light p-1 text-sm rounded transition-colors">
          <input v-model="logFilter.device_id" placeholder="Filtruj wg Device ID" class="border border-gray-300 dark:border-custom-border bg-white dark:bg-custom-dark text-gray-900 dark:text-custom-light p-1 text-sm rounded transition-colors">
          <button @click="loadLogs" class="bg-gray-200 dark:bg-custom-dark text-gray-800 dark:text-custom-light border border-transparent dark:border-custom-border hover:bg-gray-300 dark:hover:bg-gray-800 text-sm px-3 py-1 rounded transition-colors">Odśwież</button>
        </div>
      </div>
      <div class="max-h-64 overflow-y-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-custom-border text-sm">
          <thead class="bg-gray-50 dark:bg-custom-dark text-xs text-gray-500 dark:text-custom-muted uppercase sticky top-0 transition-colors">
            <tr>
              <th class="px-6 py-2 text-left">Data</th>
              <th class="px-6 py-2 text-left">Akcja</th>
              <th class="px-6 py-2 text-left">Typ Encji</th>
              <th class="px-6 py-2 text-left">ID Encji</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-custom-border text-gray-800 dark:text-custom-light transition-colors">
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