import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import TaskView from '../views/TaskView.vue'

import StatisticsView from '../views/StatisticsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/login', name: 'login', component: LoginView },
    { path: '/task', name: 'task', component: TaskView, meta: { requiresAuth: true } },

    {
      path: '/statistics', // Новый путь
      name: 'statistics',
      component: StatisticsView
      // Если доступ к статистике тоже нужно защитить:
      // meta: { requiresAuth: true }
    },
    { path: '/', redirect: () => localStorage.getItem('hackathon_token') ? '/task' : '/login' },

  ]
})

// Navigation Guard (без изменений)
router.beforeEach((to, from, next) => {
  const loggedIn = !!localStorage.getItem('hackathon_token');
  if (to.meta.requiresAuth && !loggedIn) {
    next({ name: 'login' });
  } else if (to.name === 'login' && loggedIn) {
    next({ name: 'task' });
  } else {
    next();
  }
});

export default router