<template>
  <div class="task-container page-container">
    <h1>Задание Хакатона</h1>

    <div v-if="loading" class="loading">Загрузка задания...</div>
    <div v-if="error" class="error-message">{{ error }}</div>

    <div v-if="task && !finished">
      <h2>Задание #{{ task.id }}</h2>

      <div v-if="task.image_url" class="task-image-container">
        <img :src="task.image_url" alt="Изображение к заданию" class="task-image">
      </div>

      <pre class="task-text">{{ task.text }}</pre>

      <div v-if="task.download_url" class="task-download-container">
        <a :href="task.download_url" :download="task.download_display_name || true" class="download-link">
          {{ task.download_display_name || 'Нажмите для скачивания' }}
        </a>
        <span class="icon">📎</span>
      </div>

      <form @submit.prevent="handleSubmit" class="answer-form">
        <div class="form-group">
          <label for="answer">Ваш ответ</label>
          <input type="text" id="answer" v-model="answer" required :disabled="submitting">
        </div>
        <button type="submit" :disabled="submitting || !answer">
          {{ submitting ? 'Отправка...' : 'Отправить ответ' }}
        </button>
      </form>
      <p v-if="feedback" :class="['feedback', isCorrect ? 'correct' : 'incorrect']">{{ feedback }}</p>
    </div>

    <div v-if="finished" class="finished-message">
      <h2>Поздравляем! <span class="icon">🏆</span></h2>
      <p>Вы успешно решили все задания!</p>
      <router-link to="/statistics">Посмотреть статистику</router-link>

    </div>
  </div>
</template>

<script setup>
// ... (Импорты и setup скрипт остаются БЕЗ ИЗМЕНЕНИЙ) ...
// Функция fetchTask уже будет получать новые поля image_url, download_url и т.д.
import {onMounted, ref} from 'vue';
import api from '@/services/api';
// import { useRouter } from 'vue-router'; // Не нужен, т.к. ссылка в шаблоне

const task = ref(null);
const answer = ref('');
const loading = ref(true);
const error = ref('');
const submitting = ref(false);
const feedback = ref('');
const isCorrect = ref(false);
const finished = ref(false);
// const router = useRouter();

const fetchTask = async () => {
  loading.value = true;
  error.value = '';
  feedback.value = '';
  isCorrect.value = false;
  answer.value = '';
  task.value = null; // Сброс перед запросом
  try {
    const response = await api.getCurrentTask();
    task.value = response.data; // Теперь здесь будут и image_url, download_url
  } catch (err) { /* ... (обработка ошибок как раньше) ... */
    if (err.response && err.response.status === 404) {
      if (localStorage.getItem('hackathon_finished') === 'true') {
        finished.value = true;
        localStorage.removeItem('hackathon_finished');
      } else {
        error.value = "Не удалось загрузить текущее задание.";
      }
    } else {
      error.value = 'Не удалось загрузить задание.';
      console.error('Fetch task error:', err);
    }
  } finally {
    loading.value = false;
  }
};
const handleSubmit = async () => { /* ... (без изменений) ... */
  submitting.value = true;
  feedback.value = '';
  error.value = '';
  isCorrect.value = false;
  try {
    const response = await api.submitAnswer(answer.value);
    isCorrect.value = response.data.correct;
    if (isCorrect.value) {
      feedback.value = 'Верно! Загружаем следующее задание...';
      if (response.data.finished) {
        localStorage.setItem('hackathon_finished', 'true');
        setTimeout(() => {
          finished.value = true;
          task.value = null;
        }, 1500);
      } else {
        setTimeout(fetchTask, 1500);
      }
    } else {
      feedback.value = 'Неверный ответ. Попробуйте еще раз.';
    }
  } catch (err) {
    error.value = 'Ошибка при отправке ответа.';
    console.error('Submit answer error:', err);
  } finally {
    setTimeout(() => {
      submitting.value = false;
    }, isCorrect.value ? 1500 : 500);
  }
};
onMounted(fetchTask);
</script>


<style scoped>
.task-container {
  /* Стили page-container применяются глобально */
}

h2 {
  color: var(--samurai-secondary); /* Заголовок задания - золотым */
  margin-bottom: 0.8em;
  border-bottom: 1px solid var(--samurai-border);
  padding-bottom: 0.4em;
}

.task-text {
  background-color: var(--samurai-bg); /* Темнее фон для текста задачи */
  padding: 20px;
  border-radius: 5px;
  margin-bottom: 25px;
  color: #f0f0f0; /* Ярче текст для лучшей читаемости */
  font-family: 'Courier New', Courier, monospace; /* Моноширинный для кода/текста */
  font-size: 1rem;
  white-space: pre-wrap; /* Сохраняет переносы строк и пробелы */
  border: 1px solid var(--samurai-border);
  max-height: 400px; /* Ограничение высоты с прокруткой */
  overflow-y: auto; /* Добавить скролл, если текст длинный */
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
}

button[type="submit"] {
  margin-top: 10px;
}

/* Стилизация фидбека */
.feedback {
  margin-top: 20px;
  padding: 12px;
  border-radius: 5px;
  font-weight: 600;
  text-align: center;
}

.feedback.correct {
  color: white;
  background-color: var(--samurai-success); /* Зеленый фон */
  border: 1px solid #388E3C;
}

.feedback.incorrect {
  color: white;
  background-color: var(--samurai-error); /* Красный фон */
  border: 1px solid var(--samurai-primary-dark);
}

.finished-message {
  text-align: center;
  margin-top: 30px;
  color: var(--samurai-success);
}

.finished-message h2 {
  color: var(--samurai-success);
  border-bottom: none;
}

.finished-message p {
  font-size: 1.2em;
  color: var(--samurai-text);
  margin-bottom: 20px;
}

.finished-message .icon {
  font-size: 1.5em;
  margin-left: 10px;
}

.task-image-container {
  margin-bottom: 20px;
  text-align: center; /* Центрируем картинку, если она меньше контейнера */
}

.task-image {
  max-width: 100%; /* Картинка не будет вылезать за контейнер */
  height: auto; /* Сохраняем пропорции */
  border-radius: 6px;
  border: 1px solid var(--samurai-border);
}

/* Стили для текста задания (без изменений) */
.task-text {
  /* --- Добавляем/Изменяем эти строки --- */
    font-family: var(--font-main); /* Используем переменную с Bonzai Cyr */
    font-weight: 400;          /* Указываем нормальный вес */
    font-size: 1.5rem;            /* Можно немного увеличить размер для читаемости */
    //line-height: 1.7;             /* Возможно, понадобится увеличить межстрочный интервал */
    /* --- Конец изменений --- */

    /* Остальные стили для .task-text (background, padding, border-radius, color, white-space, etc.) */
    //background-color: var(--samurai-bg);
    //padding: 20px;
    //border-radius: 5px;
    //margin-bottom: 25px;
    //color: #f0f0f0;
    //white-space: pre-wrap;
    //border: 1px solid var(--samurai-border);
    //max-height: 400px;
    //overflow-y: auto;
}

/* Стили для ссылки на скачивание */
.task-download-container {
  margin-top: 15px; /* Отступ сверху */
  margin-bottom: 25px; /* Отступ снизу */
  padding: 12px 15px;
  background-color: var(--samurai-bg); /* Фон как у блока с текстом */
  border: 1px solid var(--samurai-border);
  border-radius: 5px;
  display: flex; /* Чтобы иконка была рядом */
  align-items: center;
  justify-content: center; /* Центрируем содержимое */
}

.download-link {
  color: var(--samurai-secondary); /* Золотой цвет ссылки */
  font-weight: 600;
  text-decoration: underline;
  margin-right: 10px; /* Отступ от иконки */
}

.download-link:hover {
  color: var(--samurai-primary); /* Красный при наведении */
}

.task-download-container .icon {
  color: var(--samurai-text);
  font-size: 1.2em;
}

/* Стили для формы ответа (можно добавить отступ сверху) */
.answer-form {
  margin-top: 25px;
}

.form-group { /* ... */
}

label { /* ... */
}

button[type="submit"] { /* ... */
}

.feedback { /* ... */
}

.feedback.correct { /* ... */
}

.feedback.incorrect { /* ... */
}

.finished-message { /* ... */
}
</style>