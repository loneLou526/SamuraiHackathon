<template>
  <div id="app-wrapper">
    <canvas id="matrix-canvas" class="background-effect"></canvas>


    <div class="peeking-samurai samurai-left">
      <img src="/images/samurai-left.png" alt="Samurai Left"/>
    </div>
    <div class="peeking-samurai samurai-right">
      <img src="/images/samurai-right.png" alt="Samurai Right"/>
    </div>

    <header class="app-header">
      <nav>
        <router-link to="/task" v-if="isLoggedIn">Задание</router-link>
        <router-link to="/statistics">Статистика</router-link>
        <button @click="logout" v-if="isLoggedIn" class="logout-button">Выйти</button>
      </nav>
    </header>

    <main>
      <RouterView/>
    </main>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import {RouterLink, RouterView, useRouter} from 'vue-router';

const router = useRouter();
const isLoggedIn = computed(() => !!localStorage.getItem('hackathon_token'));
const logout = () => {
  localStorage.removeItem('hackathon_token');
  localStorage.removeItem('hackathon_finished');
  router.push('/login');
};
const canvasRef = ref(null); // Ссылка на canvas (не используется напрямую здесь, но можно)
let animationFrameId = null;

const startMatrixEffect = () => {
  const canvas = document.getElementById('matrix-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Задаем размер canvas равным размеру окна
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  const characters = 'アァカサタナハマヤャラワガザダバパイィキシチニヒミリヰギジヂビピウゥクスツヌフムユュルグズブヅプエェケセテネヘメレヱゲゼデベペオォコソトノホモヨョロヲゴゾドボポヴッン0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  // const characters = '0123456789 hacked by samurai'; // Упрощенный вариант
  const charArray = characters.split('');

  const fontSize = 14; // Размер шрифта
  const columns = Math.floor(canvas.width / fontSize); // Количество колонок

  // Массив для хранения текущей Y-позиции каждой капли
  const drops = [];
  for (let x = 0; x < columns; x++) {
    drops[x] = Math.random() * canvas.height / fontSize; // Случайная начальная позиция
  }

  const draw = () => {
    // Затемнение холста для создания эффекта "хвоста"
    ctx.fillStyle = 'rgba(26, 26, 45, 0.06)'; // Используем --samurai-bg с малой прозрачностью
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Цвет символов (красный из палитры)
    ctx.fillStyle = 'rgba(211, 47, 47, 0.7)'; // --samurai-primary с прозрачностью
    ctx.font = `${fontSize}px monospace`;

    // Рисуем капли
    for (let i = 0; i < drops.length; i++) {
      // Выбираем случайный символ
      const text = charArray[Math.floor(Math.random() * charArray.length)];
      // Рисуем символ
      ctx.fillText(text, i * fontSize, drops[i] * fontSize);

      // Сдвигаем каплю вниз
      drops[i]++;

      // Если капля ушла за экран, возвращаем ее наверх со случайной задержкой
      if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
        drops[i] = 0;
      }
    }
    // Запрашиваем следующий кадр анимации
    animationFrameId = requestAnimationFrame(draw);
  };

  // Отменяем предыдущую анимацию, если она была
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  draw(); // Запускаем отрисовку
};

// Обработчик изменения размера окна
const handleResize = () => {
  startMatrixEffect(); // Перезапускаем эффект с новыми размерами
};


onMounted(() => {
  // Используем setTimeout для небольшой задержки, чтобы браузер успел "увидеть" начальное состояние
  setTimeout(() => {
    const samuraiLeft = document.querySelector('.samurai-left');
    const samuraiRight = document.querySelector('.samurai-right');
    if (samuraiLeft) samuraiLeft.classList.add('visible');
    if (samuraiRight) samuraiRight.classList.add('visible');
  }, 100); // Небольшая задержка в 100мс
  // Запускаем эффект матрицы
  startMatrixEffect();
  // Добавляем слушатель изменения размера окна
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  // Останавливаем анимацию и удаляем слушатель
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  window.removeEventListener('resize', handleResize);
});


</script>

<style scoped>
.app-header {
  position: relative; /* Необходимо для z-index */
  z-index: 10; /* Выше самураев */
  background-color: var(--samurai-bg-light);
  padding: 15px 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

nav {
  display: flex;
  gap: 25px;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
}

nav a {
  font-family: var(--font-main);
  font-weight: 600;
  color: var(--samurai-text);
  padding: 8px 12px;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  position: relative;
  overflow: hidden;
}

nav a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: -100%;
  width: 100%;
  height: 2px;
  background-color: var(--samurai-primary);
  transition: left 0.3s ease-out;
}

nav a:hover::after, nav a.router-link-exact-active::after {
  left: 0;
}

nav a.router-link-exact-active {
  color: var(--samurai-primary);
  background-color: transparent;
}

nav a:hover {
  color: var(--samurai-secondary);
}

.logout-button {
  margin-left: auto;
  background-color: transparent;
  border: 1px solid var(--samurai-primary);
  color: var(--samurai-primary);
  padding: 8px 15px;
  cursor: pointer;
  border-radius: 4px;
  font-family: var(--font-main);
  text-transform: uppercase;
}

.logout-button:hover {
  background-color: var(--samurai-primary);
  color: white;
}

main {
  padding: 20px;
  position: relative; /* Необходимо для z-index */
  z-index: 5;
}


/* --- Стили для Самураев --- */
.peeking-samurai {
  position: fixed; /* Фиксируем относительно окна браузера */
  bottom: 0; /* Прижимаем к низу */
  //max-height: 85vh; /* Ограничиваем высоту */
  //width: auto; /* Ширина авто для сохранения пропорций */
  z-index: 1; /* Ставим за основным контентом, но над фоном body */
  //opacity: 0.8;     /* Делаем немного прозрачными, чтобы не отвлекали */
  pointer-events: none; /* Чтобы нельзя было кликнуть или выделить */

  /* --- Анимация появления --- */
  opacity: 0; /* Начальное состояние - невидимы */
  transition: transform 1.2s ease-out, opacity 1s ease-out; /* Время и плавность */
  transition-delay: 0.3s; /* Небольшая задержка перед началом */
}

.samurai-left {
  left: 0; /* Прижимаем к левому краю */
  /* Сдвигаем большую часть за экран влево (подбери % в зависимости от картинки) */
  transform: translateX(-100%);
}

.samurai-right {
  right: 0; /* Прижимаем к правому краю */
  /* Сдвигаем большую часть за экран вправо (подбери % в зависимости от картинки) */
  transform: translateX(100%);
  /* Если нужно отразить картинку: transform: translateX(65%) scaleX(-1); */
}

/* --- Класс для видимого состояния --- */
.peeking-samurai.visible {
  opacity: 1; /* Конечная прозрачность */
  /* Применяем анимацию */
  //animation: subtleSway 5s ease-in-out infinite; /* имя, длительность, плавность, повтор */
  //animation-delay: 1.5s; /* Начать качаться после появления */

}

.samurai-left.visible {
  /* Конечное положение */
  transform: translateX(-30%);
}

.samurai-right.visible {
  /* Конечное положение */
  transform: translateX(30%);
}

.peeking-samurai img {
  display: block; /* Убирает лишние отступы под img */
  max-height: 85vh; /* Задаем размер здесь */
  width: auto; /* Задаем размер здесь */
  opacity: 0.9; /* Прозрачность задаем здесь */

  /* Применяем анимацию ТОЛЬКО к img */
  /* Важно: анимация начнется только когда элемент img станет видимым
     (т.е. когда у родителя .peeking-samurai появится opacity > 0) */
  animation: subtleSway 5s ease-in-out infinite;
  /* Можно добавить задержку, чтобы анимация началась после появления */
  /* animation-delay: 1.5s; (если transition у родителя 1.2s + 0.3s) */
  will-change: transform; /* Оптимизация */
}

/* --- Адаптивность: Скрываем на маленьких экранах --- */
@media (max-width: 1200px) {
  /* Подбери ширину экрана */
  .peeking-samurai {
    /* Можно уменьшить размер или прозрачность */
    max-height: 30vh;
    opacity: 0.4;
    transform: translateX(-75%); /* Сдвигаем еще больше */
  }

  .samurai-right {
    transform: translateX(75%); /* Сдвигаем еще больше */
  }
}

@media (max-width: 992px) {
  /* Подбери ширину экрана */
  .peeking-samurai {
    display: none; /* Полностью скрываем */
  }
}

@keyframes subtleSway {
  0%, 100% {
    transform: translateY(0); /* Начальное и конечное положение по Y */
  }
  50% {
    transform: translateY(4px); /* Слегка приподнимаются в середине (подбери значение) */
  }
}

/* Стили для Canvas */
.background-effect {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0; /* Позади всего, даже самураев (если у них z-index > 0) */
  pointer-events: none; /* Не должен мешать кликам */
}
</style>