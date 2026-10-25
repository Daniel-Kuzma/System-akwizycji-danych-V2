import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { 
    path: '/', 
    redirect: '/login' 
  },
  { 
    path: '/login', 
    component: () => import('../views/LoginView.vue') 
  },
  { 
    path: '/rejestracja', 
    component: () => import('../views/RegisterView.vue') 
  },
  { 
    path: '/urzadzenia', 
    component: () => import('../views/DevicesView.vue'),
    meta: { requiresAuth: true, requiresUser: true } 
  },
  { 
    path: '/urzadzenia/dodaj', 
    component: () => import('../views/AddDeviceView.vue'),
    meta: { requiresAuth: true, requiresUser: true } 
  },
  { 
    path: '/urzadzenia/:id', 
    component: () => import('../views/DeviceDetailView.vue'),
    meta: { requiresAuth: true, requiresUser: true } 
  },
  { 
    path: '/urzadzenia/:id/ustawienia', 
    component: () => import('../views/DeviceSettingsView.vue'),
    meta: { requiresAuth: true, requiresUser: true } 
  },
  { 
    path: '/admin', 
    component: () => import('../views/AdminView.vue'),
    meta: { requiresAuth: true, requiresAdmin: true } 
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }
  
  if (to.meta.requiresAdmin && role !== 'admin') {
    return next('/urzadzenia')
  }

  if (to.meta.requiresUser && role === 'admin') {
    return next('/admin')
  }

  next()
})

export default router