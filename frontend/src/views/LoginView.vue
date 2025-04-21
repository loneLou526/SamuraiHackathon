<template>
  <div class="login-container page-container">
    <h1>Вход для команды</h1>
    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="teamName">Название команды:</label>
        <input type="text" id="teamName" v-model="teamName" required>
      </div>
      <div class="form-group">
        <label for="password">Пароль:</label>
        <input type="password" id="password" v-model="password" required>
      </div>
      <button type="submit" :disabled="loading">
        {{ loading ? 'Вход...' : 'Войти' }}
      </button>
      <p v-if="error" class="error-message">{{ error }}</p>
    </form>
  </div>
</template>

<script setup>
// ... скрипт остается без изменений
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api';

const teamName = ref('');
const password = ref('');
const loading = ref(false);
const error = ref('');
const router = useRouter();

const handleLogin = async () => {
  loading.value = true;
  error.value = '';
  try {
    const response = await api.login(teamName.value, password.value);
    if (response.data.success && response.data.token) {
      localStorage.setItem('hackathon_token', response.data.token);
      router.push('/task');
    } else {
      error.value = 'Неожиданный ответ от сервера.';
    }
  } catch (err) {
    if (err.response && err.response.status === 401) {
      error.value = 'Неверное имя команды или пароль.';
    } else {
      error.value = 'Ошибка сети или сервера. Попробуйте позже.';
      console.error('Login error:', err);
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  max-width: 450px; /* Чуть шире */
  /* Остальные стили page-container применяются глобально */
}
h1 {
    margin-bottom: 1.5em; /* Больше отступ после заголовка */
}
.form-group {
  margin-bottom: 20px; /* Больше расстояние между полями */
  text-align: left;
}
label {
  display: block;
  margin-bottom: 8px;
  color: var(--samurai-text);
  font-weight: 600;
}

/* Инпуты и кнопки уже стилизованы глобально */

button[type="submit"] {
    width: 100%; /* Кнопка на всю ширину */
    margin-top: 10px; /* Отступ перед кнопкой */
}
</style>