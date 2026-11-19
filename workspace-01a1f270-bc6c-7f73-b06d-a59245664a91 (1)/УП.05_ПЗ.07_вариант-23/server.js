// ============================================================
//  УП.05, ПЗ.07 (вариант 23)
//  Предметная область: О5 «Опрос»      Маршрут: /опрос
//  Конфигурация: К3 (формат обмена — JSON, автотест на код успеха)
//  Порт: 3623
// ============================================================
//  Запуск:  node server.js
//  Проверка: http://localhost:3623/
// ------------------------------------------------------------

const http = require('http');

const PORT = 3623;

// Маршрут отправки данных. В URL он приходит закодированным
// (/опрос -> /%D0%BE%D0%BF%D1%80%D0%BE%D1%81), поэтому сравниваем
// раскодированный путь.
const ROUTE = decodeURIComponent('/опрос');

// «База данных» в памяти — чтобы ответы выглядели правдоподобно
let nextId = 1;
const responses = [];

function sendJson(res, code, obj) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(obj, null, 2));
}

const server = http.createServer((req, res) => {
  const path = decodeURIComponent(req.url.split('?')[0]);

  // ---------- 1. Главная страница ----------
  if (req.method === 'GET' && path === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end(
      '<!DOCTYPE html><html lang="ru"><head><meta charset="utf-8">' +
      '<title>Опрос — сервер ПЗ.06</title></head><body>' +
      '<h1>Сервер работает</h1>' +
      '<p>Вариант 23: предметная область О5 «Опрос», конфигурация К3, порт 3623.</p>' +
      '<p>Маршрут отправки данных: <b>POST /опрос</b> (тело — JSON, поля ' +
      '<code>тема</code>, <code>оценка</code>).</p>' +
      '</body></html>'
    );
    return;
  }

  // ---------- 2. Маршрут отправки данных ----------
  if (path === ROUTE) {
    // 2.1 Неверное действие -> 405 «Метод не разрешён»
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST');
      sendJson(res, 405, { error: 'Метод не разрешён', allowed: 'POST' });
      return;
    }

    // 2.2 Собираем тело запроса
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
    });
    req.on('end', () => {
      // Конфигурация К3 -> сервер ждёт формат обмена (JSON)
      const contentType = (req.headers['content-type'] || '').toLowerCase();
      if (!contentType.includes('application/json')) {
        sendJson(res, 415, {
          error: 'Неподдерживаемый тип содержимого',
          expected: 'application/json',
          received: contentType || '(не указан)',
        });
        return;
      }

      // 2.3 Разбор JSON + негативный сценарий (пустые/битые данные)
      let data;
      try {
        data = JSON.parse(body);
      } catch (e) {
        sendJson(res, 400, { error: 'Некорректный формат обмена (JSON не разобран)' });
        return;
      }

      const topic = typeof data['тема'] === 'string' ? data['тема'].trim() : '';
      const scoreRaw = data['оценка'];
      const score = Number(scoreRaw);
      const scoreOk =
        scoreRaw !== '' && scoreRaw !== null && scoreRaw !== undefined &&
        Number.isInteger(score) && score >= 1 && score <= 5;

      if (!topic || !scoreOk) {
        sendJson(res, 400, {
          error: 'Заполните все поля',
          details: {
            'тема': topic ? 'ok' : 'поле обязательно и не может быть пустым',
            'оценка': scoreOk ? 'ok' : 'требуется целое число от 1 до 5',
          },
        });
        return;
      }

      // 2.4 Успешный сценарий
      const record = { id: nextId++, 'тема': topic, 'оценка': score, дата: new Date().toISOString() };
      responses.push(record);

      sendJson(res, 200, {
        status: 'ok',
        message: 'Ответ на опрос принят',
        received: record,
        total: responses.length,
      });
    });
    return;
  }

  // ---------- 3. Все остальные адреса ----------
  sendJson(res, 404, { error: 'Не найдено', path });
});

server.listen(PORT, () => {
  console.log(`Сервер варианта 23 запущен на порту ${PORT}`);
  console.log(`Главная:            http://localhost:${PORT}/`);
  console.log(`Отправка данных:    POST http://localhost:${PORT}/опрос  (JSON)`);
});
