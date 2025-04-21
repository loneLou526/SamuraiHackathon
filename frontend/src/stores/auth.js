// src/stores/auth.js
import { defineStore } from 'pinia';
import api from '@/services/api.js';
import router from '@/router'; // Импортируем роутер для редиректов

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('authToken') || null, // Пытаемся загрузить токен из localStorage
    teamName: null, // Можно хранить имя команды
    error: null, // Для хранения ошибок логина
    loading: false, // Индикатор загрузки
  }),
  getters: {
    isAuthenticated: (state) => !!state.token, // Проверяем, есть ли токен
  },
  actions: {
    async login(credentials) {
      this.loading = true;
      this.error = null;
      try {
        // Отправляем POST-запрос на /login бэкенда
        const response = await api.post('/login', credentials);

        if (response.data && response.data.success && response.data.token) {
          this.token = response.data.token;
          // Сохраняем токен в localStorage для персистентности
          localStorage.setItem('authToken', this.token);
          // Можно сохранить имя команды, если оно вам нужно
          // this.teamName = credentials.team_name;

          // Успешный вход - перенаправляем на страницу задач
          await router.push('/task');
        } else {
          // Если бэкенд вернул success: false или не вернул токен
          throw new Error(response.data.detail || 'Ошибка входа: Неверные данные.');
        }
      } catch (err) {
        console.error('Login error:', err);
        this.error = err.response?.data?.detail || err.message || 'Произошла ошибка при входе.';
        this.token = null;
        localStorage.removeItem('authToken'); // Удаляем старый токен, если был
      } finally {
        this.loading = false;
      }
    },
    logout() {
      this.token = null;
      this.teamName = null;
      localStorage.removeItem('authToken');
      // Перенаправляем на страницу входа
      router.push('/login');
    },
    // Действие для проверки токена при загрузке приложения (опционально)
    checkAuth() {
      const token = localStorage.getItem('authToken');
      if (token) {
        this.token = token;
        // Здесь можно добавить запрос к бэкенду для проверки валидности токена,
        // если ваш API предоставляет такой эндпоинт (например, /api/me)
      } else {
        this.token = null;
      }
    }
  },
});