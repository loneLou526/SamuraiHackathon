<template>
  <div class="attempts-container page-container">
    <h1>Статистика Попыток</h1>

    <div v-if="loading && !chartData.datasets[0].data.length" class="loading">Загрузка статистики...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="!loading || chartData.datasets[0].data.length" class="chart-wrapper">
      <Bar
          v-if="chartData.labels.length > 0"
      :data="chartData"
      :options="chartOptions"
      :key="JSON.stringify(chartData.datasets[0].data)"
      :style="{ maxHeight: '450px' }"
      />
      <p v-else-if="!loading && !error" class="no-data">Пока нет данных о попытках.</p>
    </div>

  </div>
</template>

<script setup>
import {onMounted, onUnmounted, reactive, ref} from 'vue';
import {Bar} from 'vue-chartjs'; // Импортируем компонент Bar
import {BarElement, CategoryScale, Chart as ChartJS, Legend, LinearScale, Title, Tooltip} from 'chart.js'; // Импортируем необходимые модули Chart.js
import api from '@/services/api';

// --- Регистрация компонентов Chart.js ---
// Это обязательно нужно сделать перед использованием
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

// --- Состояние компонента ---
const loading = ref(true);
const error = ref('');
const attemptsData = ref([]); // Исходные данные с API
const pollingIntervalId = ref(null); // ID для setInterval, чтобы его можно было остановить
const POLLING_RATE_MS = 10000; // Частота опроса в миллисекундах (здесь 10 секунд)

// --- Реактивные данные для графика ---
// Используем reactive для вложенных структур, чтобы Vue отслеживал изменения
const chartData = reactive({
  labels: [], // Массив ID задач (ось X)
  datasets: [
    {
      label: 'Всего попыток',
      backgroundColor: 'rgba(54, 162, 235, 0.7)',
      borderColor: 'rgba(54, 162, 235, 1)',      // Темно-красный для границ
      borderWidth: 1,
      data: [], // Массив количества попыток (ось Y)
      barThickness: 'flex', // Или можно задать фиксированную ширину, напр. 30
      maxBarThickness: 50, // Макс. ширина столбика
    }
  ]
});

// --- Опции для графика ---
const chartOptions = reactive({
  responsive: true,       // Делает график адаптивным
  maintainAspectRatio: false, // Позволяет задавать высоту через CSS/style
  plugins: {
    legend: {
      display: false // Легенда не нужна, т.к. только один набор данных
    },
    title: {
      display: true,
      text: 'Количество попыток по задачам',
      color: '#e0e0e0', // Цвет текста заголовка (из темы)
      font: {
        size: 16,
        family: "'Montserrat', sans-serif" // Шрифт заголовка (из темы)
      }
    },
    tooltip: { // Настройки всплывающих подсказок при наведении
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleFont: {family: "'Montserrat', sans-serif"},
      bodyFont: {family: "'Lato', sans-serif"},
      padding: 10,
      callbacks: { // Форматируем текст подсказки
        label: function (context) {
          let label = context.dataset.label || '';
          if (label) {
            label += ': ';
          }
          if (context.parsed.y !== null) {
            label += context.parsed.y;
          }
          return label;
        }
      }
    }
  },
  scales: { // Настройки осей
    x: {
      title: {
        display: true,
        text: 'ID Задачи',
        color: '#e0e0e0',
        font: {family: "'Montserrat', sans-serif", weight: '600'}
      },
      ticks: {
        color: '#c0c0c0', // Цвет подписей на оси X
        font: {family: "'Lato', sans-serif"}
      },
      grid: {
        color: 'rgba(79, 79, 111, 0.2)' // Цвет сетки X (из темы --samurai-border)
      }
    },
    y: {
      beginAtZero: true, // Начинать ось Y с нуля
      title: {
        display: true,
        text: 'Количество Попыток',
        color: '#e0e0e0',
        font: {family: "'Montserrat', sans-serif", weight: '600'}
      },
      ticks: {
        color: '#c0c0c0', // Цвет подписей на оси Y
        font: {family: "'Lato', sans-serif"},
        stepSize: 1 // Шаг оси Y (показывать целые числа)
      },
      grid: {
        color: 'rgba(79, 79, 111, 0.2)' // Цвет сетки Y (из темы --samurai-border)
      }
    }
  }
});

// --- Функция загрузки и обновления данных ---
const fetchAndUpdateAttempts = async () => {
  console.log('AttemptsView: fetchAndUpdateAttempts function started.');
  // Не показываем индикатор загрузки при авто-обновлении, чтобы график не мигал
  // loading.value = true; // Раскомментируй, если хочешь видеть индикатор при каждом обновлении
  error.value = ''; // Сбрасываем ошибку при попытке обновления
  try {
    const response = await api.getAttempts();
    attemptsData.value = response.data.attempts || []; // Сохраняем исходные данные

    // Сортируем по ID задачи для консистентности оси X
    attemptsData.value.sort((a, b) => a.task - b.task);

    const oldLabels = JSON.stringify(chartData.labels);
    const oldData = JSON.stringify(chartData.datasets[0].data);

    // Обновляем данные для графика (важно пересоздать массивы, чтобы Vue увидел изменения)
    chartData.labels = attemptsData.value.map(item => `Задание ${item.task}`); // Метки оси X
    chartData.datasets[0].data = attemptsData.value.map(item => item.attempts); // Данные оси Y


    console.log('AttemptsView: chartData updated.');
    console.log('AttemptsView: Previous Data:', oldData); // <--- Лог старых данных
    console.log('AttemptsView: New Data:', JSON.stringify(chartData.datasets[0].data)); // <--- Лог новых данных
    console.log('AttemptsView: New Labels:', JSON.stringify(chartData.labels)); // <--- Лог новых меток


  } catch (err) {
    console.error('Fetch attempts error:', err);
    // Не сбрасываем график при ошибке обновления, показываем ошибку
    error.value = 'Не удалось обновить статистику попыток.';
    // Можно добавить логику остановки polling при повторных ошибках
  } finally {
    // Убираем loading только после *первой* загрузки
    if (loading.value) {
      loading.value = false;
    }
  }
};

// --- Хуки жизненного цикла ---
onMounted(() => {
  fetchAndUpdateAttempts(); // Первоначальная загрузка данных

  // Запускаем периодический опрос
  pollingIntervalId.value = setInterval(fetchAndUpdateAttempts, POLLING_RATE_MS);
});

onUnmounted(() => {
  // Очищаем интервал при уничтожении компонента, чтобы избежать утечек памяти
  if (pollingIntervalId.value) {
    clearInterval(pollingIntervalId.value);
  }
});

</script>

<style scoped>
.attempts-container {
  /* Стили page-container применяются глобально */
}

.chart-wrapper {
  position: relative; /* Необходимо для Chart.js responsive */
  margin: 30px auto; /* Отступы сверху/снизу и центрирование */
  padding: 15px;
  background-color: var(--samurai-bg); /* Темный фон под графиком, чуть темнее page-container */
  border-radius: 6px;
  border: 1px solid var(--samurai-border);
  min-height: 300px; /* Минимальная высота, чтобы было видно сообщение об отсутствии данных */
}

/* Стили для сообщения об отсутствии данных внутри chart-wrapper */
.chart-wrapper .no-data {
  text-align: center;
  position: absolute; /* Позиционируем по центру контейнера */
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--samurai-text);
  font-style: italic;
}

/* Глобальные стили для loading и error-message уже есть в main.css */
/* Убери или закомментируй старые стили для table, если они остались */

</style>