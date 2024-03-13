// Функция для проверки валидности логина
function validateLogin() {
    var username = document.getElementById("username").value;
    var password = document.getElementById("password").value;

    // Специальная проверка для администратора
    if (username === "admin" && password === "465132") {
        document.querySelector('.login-box').style.display = 'none';
        document.getElementById('bot-container').style.display = 'block';
    } else {
        // Отправка данных на сервер для проверки
        fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({username: username, password: password})
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector('.login-box').style.display = 'none';
                document.getElementById('bot-container').style.display = 'block';
            } else {
                showModal('failModal');
            }
        })
        .catch(error => {
            console.error('Ошибка:', error);
            showModal('failModal');
        });
    }
    return false; // Предотвращаем стандартное поведение формы
}

// Функция для отправки запроса и отображения ответа в истории диалога
function sendQuery() {
  var queryInput = document.getElementById("query-input");
  var dialogueHistory = document.getElementById("dialogue-history");
  var query = queryInput.value.trim();

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
          predictionEntry.textContent = "Бот: Прогноз - " + data.prediction;
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
      queryInput.value = ""; // Очистка поля ввода
  }
}

// При загрузке страницы вызывается функция fetchBitcoinData
document.addEventListener("DOMContentLoaded", fetchBitcoinData);

// Функция для переключения темы оформления
function toggleTheme() {
  document.body.classList.toggle('light-theme');
}

// Функция для возвращения к форме логина из формы регистрации
function returnToLogin() {
  document.getElementById('register-box').style.display = 'none';
  document.querySelector('.login-box').style.display = 'block';
  document.getElementById('registrationForm').reset();
}

// Функция для регистрации пользователя
function registerUser() {
    var username = document.getElementById('register-username').value;
    var password = document.getElementById('register-password').value;
    var email = document.getElementById('register-email').value;

    if (!username || !password || !email) {
        alert('Все поля должны быть заполнены!');
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
        body: JSON.stringify(userData)
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Преобразуем тело ответа в JSON, если запрос успешен
        } else {
            throw new Error('Failed to register'); // Генерируем ошибку, если запрос не успешен
        }
    })
    .then(data => {
        console.log(data);
        showModal('successModal');
        returnToLogin();
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Ошибка регистрации. Попробуйте снова.');
    });

    return false; // Предотвращаем перезагрузку страницы
}



// Функция для показа формы регистрации
function showRegistrationForm() {
  document.querySelector('.login-box').style.display = 'none';
  document.getElementById('register-box').style.display = 'block';
}

// Функция для отображения модальных окон
function showModal(modalId) {
  var modal = document.getElementById(modalId);
  modal.style.display = "block";
  // Настройка закрытия модального окна
  modal.querySelector('.close').onclick = function() {
      modal.style.display = "none";
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
      const prices = data.prices.map(price => price[1]);
      const dates = data.prices.map(price => new Date(price[0]).toLocaleDateString());
      const ctx = document.getElementById("bitcoinChart").getContext("2d");
      new Chart(ctx, {
          type: "line",
          data: {
              labels: dates,
              datasets: [{
                  label: "Bitcoin Price (USD)",
                  data: prices,
                  borderColor: "rgb(3,233,244)",
                  backgroundColor: "rgb(2,154,161)",
              }],
          },
          options: {
              scales: {
                  y: {
                      beginAtZero: false,
                  },
              },
          },
      });
  })
  .catch(error => console.error("Error fetching data:", error));
}

// Функция для переключения отображения дополнительной информации
function showInfo(type) {
  var allInfoTexts = document.querySelectorAll('.info-text');
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
