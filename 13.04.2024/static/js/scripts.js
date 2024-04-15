// Функция для проверки валидности логина
function validateLogin() {
    var username = document.getElementById("username").value; // Получаем значение имени пользователя
    var password = document.getElementById("password").value; // Получаем значение пароля

    // Специальная проверка для администратора
    if (username === "admin" && password === "465132") {
        document.querySelector('.login-box').style.display = 'none'; // Скрываем форму логина
        document.getElementById('bot-container').style.display = 'block'; // Показываем основной контент
    } else {
        // Отправка данных на сервер для проверки
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({username: username, password: password}) // Отправляем данные в формате JSON
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector('.login-box').style.display = 'none'; // Скрываем форму логина
                document.getElementById('bot-container').style.display = 'block'; // Показываем основной контент
            } else {
                showModal('failModal'); // Показываем модальное окно об ошибке
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showModal('failModal'); // Показываем модальное окно об ошибке
        });
    }
    return false; // Предотвращаем стандартное поведение формы
}

// Функция для отправки запроса и отображения ответа в истории диалога
function sendQuery() {
  var queryInput = document.getElementById("query-input"); // Получаем элемент ввода запроса
  var dialogueHistory = document.getElementById("dialogue-history"); // Получаем контейнер для истории диалога
  var query = queryInput.value.trim(); // Получаем введенный текст, убирая пробелы по краям

  if (query) {
      // Создание и добавление записи пользователя в историю диалога
      var userEntry = document.createElement("div");
      userEntry.classList.add("dialogue-entry");
      userEntry.textContent = "Вы: " + query;
      dialogueHistory.appendChild(userEntry);

      // Отправка запроса на сервер
      var dataToSend = JSON.stringify({ text: query });
      fetch('/predict', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: dataToSend,
      })
      .then(response => response.json())
      .then(data => {
          // Отображение ответа от сервера
          var predictionEntry = document.createElement("div");
          predictionEntry.classList.add("dialogue-entry");
          predictionEntry.textContent = "Бот: " + data.prediction;
          dialogueHistory.appendChild(predictionEntry);
      })
      .catch(error => {
          // Обработка ошибки при получении данных
          console.error('Ошибка:', error);
          var errorEntry = document.createElement("div");
          errorEntry.classList.add("dialogue-entry");
          errorEntry.textContent = "Ошибка при получении прогноза";
          dialogueHistory.appendChild(errorEntry);
      });
      queryInput.value = ""; // Очистка поля ввода после отправки запроса
  }
}

// При загрузке страницы вызывается функция fetchBitcoinData
document.addEventListener("DOMContentLoaded", fetchBitcoinData);

// Функция для переключения темы оформления
function toggleTheme() {
  document.body.classList.toggle('light-theme'); // Переключение класса для изменения темы
}

// Функция для возвращения к форме логина из формы регистрации
function returnToLogin() {
  document.getElementById('register-box').style.display = 'none'; // Скрытие формы регистрации
  document.querySelector('.login-box').style.display = 'block'; // Показ формы входа
  document.getElementById('registrationForm').reset(); // Сброс формы регистрации
}

// Функция для регистрации пользователя
function registerUser() {
    var username = document.getElementById('register-username').value; // Получаем введенный логин
    var password = document.getElementById('register-password').value; // Получаем введенный пароль
    var email = document.getElementById('register-email').value; // Получаем введенный email

    if (!username || !password || !email) {
        alert('Все поля должны быть заполнены!'); // Проверка заполнения всех полей
        return false;
    }

    var userData = {
        username: username,
        password: password,
        email: email
    };

    fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData) // Отправка данных пользователя в формате JSON
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Обработка успешного ответа
        } else {
            throw new Error('Failed to register'); // Создание ошибки при неудачной попытке
        }
    })
    .then(data => {
        console.log(data);
        showModal('successModal'); // Показ модального окна об успешной регистрации
        returnToLogin(); // Возврат к форме входа
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка регистрации. Попробуйте снова.'); // Уведомление пользователя об ошибке
    });

    return false; // Предотвращение стандартного действия формы
}

// Функция для показа формы регистрации
function showRegistrationForm() {
  document.querySelector('.login-box').style.display = 'none'; // Скрытие формы входа
  document.getElementById('register-box').style.display = 'block'; // Отображение формы регистрации
}

// Функция для отображения модальных окон
function showModal(modalId) {
  var modal = document.getElementById(modalId);
  modal.style.display = "block"; // Показ модального окна
  // Настройка закрытия модального окна
  modal.querySelector('.close').onclick = function() {
      modal.style.display = "none"; // Скрытие модального окна при клике на крестик
  };

  window.onclick = function(event) {
      // Закрытие модального окна при клике вне его
      if (event.target == modal) {
          modal.style.display = "none";
      }
  }
}

// Функция для загрузки и отображения данных о курсе Bitcoin
function fetchBitcoinData() {
  fetch("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30")
  .then(response => response.json())
  .then(data => {
      // Обработка и отображение данных о курсе Bitcoin
      const prices = data.prices.map(price => price[1]); // Получение массива цен
      const dates = data.prices.map(price => new Date(price[0]).toLocaleDateString()); // Преобразование меток времени в даты
      const ctx = document.getElementById("bitcoinChart").getContext("2d"); // Получение контекста для графика
      new Chart(ctx, {
          type: "line",
          data: {
              labels: dates, // Метки по оси X
              datasets: [{
                  label: "Bitcoin Price (USD)", // Название набора данных
                  data: prices, // Данные для графика
                  borderColor: "rgb(3,233,244)", // Цвет линии
                  backgroundColor: "rgb(2,154,161)", // Цвет фона
              }],
          },
          options: {
              scales: {
                  y: {
                      beginAtZero: false, // Начало оси Y не с нуля
                  },
              },
          },
      });
  })
  .catch(error => console.error("Error fetching data:", error)); // Обработка ошибок запроса
}

// Функция для переключения отображения дополнительной информации
function showInfo(type) {
  var allInfoTexts = document.querySelectorAll('.info-text'); // Получение всех элементов с информацией
  var currentInfo = document.getElementById(type);

  if (currentInfo.classList.contains('active')) {
      // Скрытие активной информации
      currentInfo.classList.remove('active');
      currentInfo.style.display = 'none';
  } else {
      // Отображение выбранной информации и скрытие остальной
      allInfoTexts.forEach(function(info) {
          info.classList.remove('active');
          info.style.display = 'none';
      });

      currentInfo.classList.add('active');
      currentInfo.style.display = 'block';
  }
}

function getBitcoinData() {
    fetch('/bitcoin-data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Ошибка при получении данных о биткоине');
            }
            return response.json();
        })
        .then(data => {
            updateBitcoinData(data);
        })
        .catch(error => {
            console.error('Ошибка:', error);
            alert('Не удалось получить данные о биткоине. Попробуйте позже.');
        })
        .finally(() => {
            document.getElementById('loadingIndicator').style.display = 'none'; // Скрываем индикатор загрузки
        });
}


function updateBitcoinData(data) {
    document.getElementById('open').textContent = `Открытие: ${data.open.toFixed(2)}`;
    document.getElementById('high').textContent = `Максимум: ${data.high.toFixed(2)}`;
    document.getElementById('low').textContent = `Минимум: ${data.low.toFixed(2)}`;
    document.getElementById('close').textContent = `Закрытие: ${data.close.toFixed(2)}`;
    document.getElementById('priceChangePercentage').textContent = `Изменение цены: ${data.price_change_percentage.toFixed(2)}%`;
    document.getElementById('volume').textContent = `Объем: ${data.volume.toFixed(2)}`;
    document.getElementById('tradeCount').textContent = `Количество сделок: ${data.tradecount}`;
    document.getElementById('bitcoinDataBox').style.display = 'block';
    
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('fetchBitcoinButton').addEventListener('click', getBitcoinData);
});

function toggleBitcoinDataVisibility() {
    var bitcoinDataBox = document.getElementById('bitcoinDataBox');
    if (bitcoinDataBox.style.display === 'none' || bitcoinDataBox.style.display === '') {
        // Если элемент скрыт или свойство display не установлено, показываем его
        getBitcoinData(); // Вызываем функцию, которая загружает и отображает данные
    } else {
        // Если элемент показан, скрываем его
        bitcoinDataBox.style.display = 'none';
    }
}
document.getElementById('fetchBitcoinButton').addEventListener('click', toggleBitcoinDataVisibility);
document.getElementById('bitcoinDataBox').style.display = 'none';
