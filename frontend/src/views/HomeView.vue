<template>
  <div class="min-h-screen bg-samurai-dark p-4 sm:p-6 md:p-8">
    <div class="container mx-auto px-4">

      <header class="mb-8 text-center">
        <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-samurai-gold mb-2">Самурай Хакатон</h1>
        <p class="text-base sm:text-lg text-gray-400">Путь кода и чести</p>
         <router-link v-if="!authStore.isAuthenticated" to="/login" class="mt-4 inline-block bg-samurai-red hover:bg-red-700 text-white font-bold py-2 px-4 sm:px-6 rounded transition duration-300 text-sm sm:text-base">
           Войти как команда
         </router-link>
         <router-link v-else to="/task" class="mt-4 inline-block bg-terminal-green hover:bg-green-700 text-samurai-dark font-bold py-2 px-4 sm:px-6 rounded transition duration-300 text-sm sm:text-base">
           К заданиям
         </router-link>
      </header>

      <!-- Используем items-start для выравнивания колонок по верху -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 md:gap-8 items-start">

        <!-- Колонка для таблицы лидеров -->
        <div>
           <LeaderboardView :teams="leaderboard" :loading="leaderboardLoading" :error="leaderboardError" />
        </div>

        <!-- Колонка для графика попыток (БЕЗ фиксированной высоты у родительского div) -->
        <div>
          <AttemptsView :attempts-data="attempts" :loading="attemptsLoading" :error="attemptsError" />
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import api from '@/services/api.js';
import LeaderboardView from '@/views/LeaderboardView.vue';
import AttemptsView from '@/views/AttemptsView.vue';
import { useAuthStore } from '@/stores/auth';

const authStore = useAuthStore();
const leaderboard = ref([]);
const attempts = ref([]);
const leaderboardLoading = ref(true);
const attemptsLoading = ref(true);
const leaderboardError = ref(null);
const attemptsError = ref(null);
let intervalId = null;

const fetchData = async () => {
  leaderboardLoading.value = true;
  attemptsLoading.value = true;
  try {
    const [leaderboardResponse, attemptsResponse] = await Promise.all([
       api.get('/leaderboard'),
       api.get('/attempts')
    ]);
    leaderboard.value = leaderboardResponse.data.teams;
    leaderboardError.value = null;
    attempts.value = attemptsResponse.data.attempts.sort((a, b) => a.task - b.task);
    attemptsError.value = null;
  } catch (err) {
    console.error("Failed to fetch data:", err);
    leaderboardError.value = 'Ошибка загрузки данных лидерборда.';
    attemptsError.value = 'Ошибка загрузки данных графика.';
  } finally {
    leaderboardLoading.value = false;
    attemptsLoading.value = false;
  }
};

onMounted(() => {
  fetchData();
  intervalId = setInterval(fetchData, 5000);
});

onUnmounted(() => {
  if (intervalId) { clearInterval(intervalId); }
});
</script>

<style scoped>
/* Стили HomeView */
</style>