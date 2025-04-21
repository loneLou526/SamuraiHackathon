<template>
  <div class="leaderboard-container page-container">
    <h1>Таблица лидеров</h1>

    <div v-if="loading && !teams.length" class="loading">Загрузка...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!loading || teams.length" class="table-wrapper">
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
    </div>
    <p v-if="!loading && !teams.length && !error" class="no-data">Пока нет данных о командах.</p>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '@/services/api';

const teams = ref([]);
const loading = ref(true);
const error = ref('');
const pollingIntervalId = ref(null);
const POLLING_RATE_MS = 10000; // Обновляем каждые 10 секунд
const tableKey = ref(0); // Ключ для принудительного обновления таблицы
const winnerTeamName = ref(null); // Храним имя победителя

// Функция загрузки и обновления данных
const fetchLeaderboard = async () => {
  // Не показываем лоадер при авто-обновлении
  // loading.value = true;
  error.value = ''; // Сбрасываем ошибку перед запросом
  try {
    const response = await api.getLeaderboard();
    // Бэкенд теперь возвращает отсортированный список с finished_at
    teams.value = response.data.teams || [];
    // Принудительно обновляем ключ таблицы, чтобы Vue перерисовал её
    tableKey.value++;
    // Сбрасываем победителя, чтобы findWinner() отработала заново
    winnerTeamName.value = null;

  } catch (err) {
    error.value = 'Не удалось обновить таблицу лидеров.';
    console.error('Fetch leaderboard error:', err);
    // Можно остановить polling при ошибках, если нужно
    // if (pollingIntervalId.value) clearInterval(pollingIntervalId.value);
  } finally {
    // Убираем лоадер только после первой загрузки
    if (loading.value) {
        loading.value = false;
    }
  }
};

// Функция для определения победителя (вызывается из шаблона)
// Делаем это здесь, а не в fetchLeaderboard, чтобы избежать лишних вычислений до рендера
const findWinner = () => {
    // Бэкенд уже отсортировал, победитель - первый в списке,
    // если у него решены все задачи (проверяем по первому) и есть время финиша
    if (teams.value.length > 0 && teams.value[0].finished_at) {
        // Простая проверка - если у первого есть время финиша, он победитель
        // Для надежности можно было бы передавать max_task_id с бэка и сравнивать
        winnerTeamName.value = teams.value[0].team_name;
    } else {
        winnerTeamName.value = null; // Нет победителя
    }
    return ''; // Функция должна что-то вернуть для шаблона
};


// Классы для топ-3 (без изменений)
const getRankClass = (index) => {
    if (index === 0) return 'rank-1';
    if (index === 1) return 'rank-2';
    if (index === 2) return 'rank-3';
    return '';
};

// Запускаем при монтировании
onMounted(() => {
  fetchLeaderboard(); // Первая загрузка
  pollingIntervalId.value = setInterval(fetchLeaderboard, POLLING_RATE_MS); // Запуск polling'а
});

// Очищаем интервал при размонтировании
onUnmounted(() => {
  if (pollingIntervalId.value) {
    clearInterval(pollingIntervalId.value);
  }
});
</script>

<style scoped>
.leaderboard-container {
  /* Стили page-container применяются глобально */
}
.table-wrapper {
    overflow-x: auto; /* Для адаптивности на мал. экранах */
}
table {
  width: 100%;
  border-collapse: separate; /* Используем separate для border-radius */
  border-spacing: 0;
  margin-top: 20px;
  border: 1px solid var(--samurai-border);
  border-radius: 6px; /* Скругляем углы таблицы */
  overflow: hidden; /* Чтобы обрезать фон ячеек по радиусу */
}
th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--samurai-border);
}

th {
  background-color: var(--samurai-bg); /* Темный фон для заголовков */
  color: var(--samurai-secondary); /* Золотой текст заголовков */
  font-family: var(--font-header);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Убираем нижнюю границу у последней строки */
tbody tr:last-child td {
    border-bottom: none;
}

/* Центрирование для места и очков */
th.place, td.place,
th.score, td.score {
    text-align: center;
    width: 100px; /* Фикс. ширина для этих колонок */
}
th.team-name, td.team-name {
    width: auto; /* Авто ширина для имени */
    font-weight: 600;
}


/* Чередование строк */
tbody tr:nth-child(even) {
  background-color: rgba(0, 0, 0, 0.1); /* Легкий темный фон для четных */
}
tbody tr:hover {
    background-color: rgba(230, 162, 60, 0.1); /* Золотистый фон при наведении */
}


/* Выделение топ-3 */
tbody tr.rank-1 td {
    background-color: rgba(212, 175, 55, 0.2); /* Золотой фон */
    font-weight: 700;
}
tbody tr.rank-2 td {
    background-color: rgba(192, 192, 192, 0.15); /* Серебряный фон */
}
tbody tr.rank-3 td {
    background-color: rgba(205, 127, 50, 0.15); /* Бронзовый фон */
}

/* Выделение места для топ-3 */
tbody tr.rank-1 td.place { color: #D4AF37; } /* Золото */
tbody tr.rank-2 td.place { color: #c0c0c0; } /* Серебро */
tbody tr.rank-3 td.place { color: #cd7f32; } /* Бронза */


.no-data {
    text-align: center;
    margin-top: 30px;
    color: var(--samurai-text);
    font-style: italic;
}

th.status, td.status {
    text-align: center;
    width: 120px; /* Ширина колонки статуса */
    font-style: italic;
    color: var(--samurai-secondary); /* Золотой цвет для статуса */
}

.winner-flag {
  margin-left: 8px;
  font-size: 1.1em; /* Чуть больше иконка */
  color: gold; /* Или var(--samurai-secondary) */
  cursor: default; /* Убираем курсор по умолчанию для span */
  display: inline-block; /* Чтобы title работал */
}

/* Адаптация стилей рангов, если нужно */
tbody tr.rank-1 td.team-name {
    font-weight: 700; /* Уже должно быть */
}


/* Остальные стили без изменений */
.leaderboard-container { }
.table-wrapper {
    overflow-x: auto;
    margin-top: 20px;
}
table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  border: 1px solid var(--samurai-border);
  border-radius: 6px;
  overflow: hidden;
}
th, td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid var(--samurai-border);
}
th {
  background-color: var(--samurai-bg);
  color: var(--samurai-secondary);
  font-family: var(--font-header);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}
tbody tr:last-child td { border-bottom: none; }
th.place, td.place, th.score, td.score {
    text-align: center;
    width: 100px;
}
th.team-name, td.team-name { width: auto; font-weight: 600; }
tbody tr:nth-child(even) { background-color: rgba(0, 0, 0, 0.1); }
tbody tr:hover { background-color: rgba(230, 162, 60, 0.1); }
tbody tr.rank-1 td { background-color: rgba(212, 175, 55, 0.2); font-weight: 700; }
tbody tr.rank-2 td { background-color: rgba(192, 192, 192, 0.15); }
tbody tr.rank-3 td { background-color: rgba(205, 127, 50, 0.15); }
tbody tr.rank-1 td.place { color: #D4AF37; }
tbody tr.rank-2 td.place { color: #c0c0c0; }
tbody tr.rank-3 td.place { color: #cd7f32; }
.no-data { text-align: center; margin-top: 30px; color: var(--samurai-text); font-style: italic; }
</style>