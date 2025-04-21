// src/services/api.js
import axios from 'axios';

// Укажи базовый URL твоего бэкенда FastAPI
// Если фронтенд и бэкенд запускаются на одной машине, это обычно http://localhost:ПОРТ_БЭКЕНДА
// FastAPI по умолчанию использует порт 8000
const API_URL = 'http://localhost:8000/api'; // Убедись, что префикс /api совпадает с твоим бэкендом

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавляем Interceptor для автоматического добавления токена в заголовки
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('hackathon_token'); // Получаем токен из localStorage
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Добавляем Interceptor для обработки ошибок (например, 401 Unauthorized)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Если токен истек или невалиден, удаляем его и перенаправляем на логин
      console.error("Unauthorized! Redirecting to login.");
      localStorage.removeItem('hackathon_token');
      // Используем window.location для простоты, или можно интегрировать с роутером
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);


export default {
  login(teamName, password) {
    return apiClient.post('/login', {
      team_name: teamName,
      password: password,
    });
  },
  getCurrentTask() {
    return apiClient.get('/task');
  },
  submitAnswer(answer) {
    return apiClient.post('/submit', { answer: answer });
  },
  getLeaderboard() {
    return apiClient.get('/leaderboard');
  },
  getAttempts() {
      return apiClient.get('/attempts');
  }
};