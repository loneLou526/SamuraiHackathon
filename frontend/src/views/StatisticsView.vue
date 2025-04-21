<template>
  <div class="statistics-view page-container">
    <h1>Общая Статистика</h1>

    <section class="leaderboard-section">
      <h2>Таблица лидеров</h2>
      <div v-if="loadingTeams && !teams.length" class="loading">Загрузка таблицы...</div>
      <div v-if="errorTeams" class="error-message">{{ errorTeams }}</div>
      <div v-if="!loadingTeams || teams.length" class="table-wrapper">
        <table :key="tableKey">
          <thead>
            <tr>
              <th class="place">Место</th>
              <th class="team-name">Команда</th>
              <th class="score">Решено задач</th>
              <th class="status">Статус</th>
            </tr>
          </thead>
          <tbody>
            <template v-if="winnerTeamName === null && teams.length > 0">
              {{ findWinner() }}
            </template>
            <tr v-for="(team, index) in teams" :key="team.team_name" :class="getRankClass(index)">
              <td class="place">{{ index + 1 }}</td>
              <td class="team-name">
                {{ team.team_name }}
                <span v-if="team.team_name === winnerTeamName" class="winner-flag" title="Первые финишировали!">🏆</span>
              </td>
              <td class="score">{{ team.solved_tasks }}</td>
              <td class="status">
                <span v-if="team.finished_at">Завершил</span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!loadingTeams && !teams.length && !errorTeams" class="no-data">Пока нет данных о командах.</p>
      </div>
    </section>

    <section class="attempts-section">
      <h2>Статистика Попыток (Всего)</h2>
      <div v-if="loadingAttempts && !chartData.datasets[0].data.length" class="loading">Загрузка графика...</div>
      <div v-if="errorAttempts" class="error-message">{{ errorAttempts }}</div>
      <div v-if="!loadingAttempts || chartData.datasets[0].data.length" class="chart-wrapper">
        <Bar
          v-if="chartData.labels.length > 0"
          :data="chartData"
          :options="chartOptions"
          :key="JSON.stringify(chartData.datasets[0].data)"
          :style="{ maxHeight: '450px' }"
        />
         <p v-else-if="!loadingAttempts && !chartData.labels.length && !errorAttempts" class="no-data">Пока нет данных о попытках.</p>
      </div>
    </section>

  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import api from '@/services/api';

// --- Регистрация Chart.js ---
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

// --- Общие Настройки ---
const POLLING_RATE_MS = 10000; // 10 секунд

// --- Состояние для Таблицы Лидеров ---
const teams = ref([]);
const loadingTeams = ref(true);
const errorTeams = ref('');
const pollingIntervalIdTeams = ref(null);
const tableKey = ref(0);
const winnerTeamName = ref(null);

// --- Состояние для Графика Попыток ---
const loadingAttempts = ref(true);
const errorAttempts = ref('');
const pollingIntervalIdAttempts = ref(null);
const attemptsData = ref([]); // Не используется напрямую в шаблоне, но нужно для обработки
const chartData = reactive({ // Данные для графика
  labels: [],
  datasets: [ {
      label: 'Всего попыток',
      backgroundColor: 'rgba(54, 162, 235, 0.7)', // Синий
      borderColor: 'rgba(54, 162, 235, 1)',
      borderWidth: 1,
      data: [],
      barThickness: 'flex',
      maxBarThickness: 50,
    } ]
});
const chartOptions = reactive({ // Опции графика
  responsive: true, maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    title: { display: true, text: 'Общее количество попыток по задачам', color: '#e0e0e0', font: { size: 16, family: "'Montserrat', sans-serif" }},
    tooltip: { backgroundColor: 'rgba(0, 0, 0, 0.8)', titleFont: { family: "'Montserrat', sans-serif" }, bodyFont: { family: "'Lato', sans-serif" }, padding: 10, callbacks: { label: (c) => `${c.dataset.label || ''}: ${c.parsed.y || ''}` }}
  },
  scales: {
    x: { title: { display: true, text: 'ID Задачи', color: '#e0e0e0', font: { family: "'Montserrat', sans-serif", weight: '600'}}, ticks: { color: '#c0c0c0', font: { family: "'Lato', sans-serif" }}, grid: { color: 'rgba(79, 79, 111, 0.2)' }},
    y: { beginAtZero: true, title: { display: true, text: 'Количество Попыток (Всего)', color: '#e0e0e0', font: { family: "'Montserrat', sans-serif", weight: '600'}}, ticks: { color: '#c0c0c0', font: { family: "'Lato', sans-serif" }, stepSize: 1 }, grid: { color: 'rgba(79, 79, 111, 0.2)' }}
  }
});


// --- Функции для Таблицы Лидеров ---
const fetchLeaderboard = async () => {
  errorTeams.value = '';
  try {
    const response = await api.getLeaderboard();
    teams.value = response.data.teams || [];
    tableKey.value++;
    winnerTeamName.value = null; // Сбрасываем для пересчета в findWinner
  } catch (err) {
    errorTeams.value = 'Не удалось обновить таблицу лидеров.';
    console.error('Fetch leaderboard error:', err);
  } finally {
    if (loadingTeams.value) loadingTeams.value = false;
  }
};

const findWinner = () => {
    if (teams.value.length > 0 && teams.value[0].finished_at) {
        winnerTeamName.value = teams.value[0].team_name;
    } else {
        winnerTeamName.value = null;
    }
    return '';
};

const getRankClass = (index) => { // Стили для топ-3
    if (index === 0) return 'rank-1';
    if (index === 1) return 'rank-2';
    if (index === 2) return 'rank-3';
    return '';
};

// --- Функция для Графика Попыток ---
const fetchAndUpdateAttempts = async () => {
  errorAttempts.value = '';
  try {
    const response = await api.getAttempts();
    attemptsData.value = response.data.attempts || [];
    attemptsData.value.sort((a, b) => a.task - b.task);

    // Обновляем данные графика
    chartData.labels = attemptsData.value.map(item => `Задание ${item.task}`);
    chartData.datasets[0].data = attemptsData.value.map(item => item.attempts);

  } catch (err) {
    errorAttempts.value = 'Не удалось обновить статистику попыток.';
    console.error('Fetch attempts error:', err);
  } finally {
    if (loadingAttempts.value) loadingAttempts.value = false;
  }
};


// --- Хуки Жизненного Цикла ---
onMounted(() => {
  // Первоначальная загрузка
  fetchLeaderboard();
  fetchAndUpdateAttempts();

  // Запуск интервалов для polling'а
  pollingIntervalIdTeams.value = setInterval(fetchLeaderboard, POLLING_RATE_MS);
  pollingIntervalIdAttempts.value = setInterval(fetchAndUpdateAttempts, POLLING_RATE_MS);
});

onUnmounted(() => {
  // Очистка интервалов при уходе со страницы
  if (pollingIntervalIdTeams.value) clearInterval(pollingIntervalIdTeams.value);
  if (pollingIntervalIdAttempts.value) clearInterval(pollingIntervalIdAttempts.value);
});

</script>

<style scoped>
/* Общие стили для секций */
.leaderboard-section,
.attempts-section {
  margin-bottom: 40px; /* Отступ между секциями */
}

h2 {
  color: var(--samurai-secondary);
  border-bottom: 1px solid var(--samurai-border);
  padding-bottom: 0.5em;
  margin-bottom: 1.5em;
  text-align: center;
}

/* --- Стили для таблицы лидеров (копируем из LeaderboardView) --- */
.table-wrapper { overflow-x: auto; margin-top: 0; /* Убираем верхний отступ, т.к. есть отступ у секции */}
table { width: 100%; border-collapse: separate; border-spacing: 0; border: 1px solid var(--samurai-border); border-radius: 6px; overflow: hidden; }
th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid var(--samurai-border); }
th { background-color: var(--samurai-bg); color: var(--samurai-secondary); font-family: var(--font-main); font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
tbody tr:last-child td { border-bottom: none; }
th.place, td.place, th.score, td.score { text-align: center; width: 100px; }
th.team-name, td.team-name { width: auto; font-weight: 600; }
th.status, td.status { text-align: center; width: 120px; font-style: italic; color: var(--samurai-secondary); }
tbody tr:nth-child(even) { background-color: rgba(0, 0, 0, 0.1); }
tbody tr:hover { background-color: rgba(230, 162, 60, 0.1); }
tbody tr.rank-1 td { background-color: rgba(212, 175, 55, 0.2); font-weight: 700; }
tbody tr.rank-2 td { background-color: rgba(192, 192, 192, 0.15); }
tbody tr.rank-3 td { background-color: rgba(205, 127, 50, 0.15); }
tbody tr.rank-1 td.place { color: #D4AF37; }
tbody tr.rank-2 td.place { color: #c0c0c0; }
tbody tr.rank-3 td.place { color: #cd7f32; }
.winner-flag { margin-left: 8px; font-size: 1.1em; color: gold; cursor: default; display: inline-block; }

/* --- Стили для графика (копируем из AttemptsView) --- */
.chart-wrapper { position: relative; margin: 0 auto; /* Убираем верхний/нижний отступ */ padding: 15px; background-color: var(--samurai-bg); border-radius: 6px; border: 1px solid var(--samurai-border); min-height: 300px; }
.chart-wrapper .no-data,
.table-wrapper .no-data /* Общий стиль для "нет данных" */
{ text-align: center; padding: 20px 0; color: var(--samurai-text); font-style: italic; }

/* Стили loading / error-message используются глобальные */
</style>