// ============================================================
//  ЭМУЛЯЦИЯ (двойник сервера) для варианта 23, порт 3624
//  Отдаёт заранее заготовленные ответы из коллекции — реальный
//  сервер (server.js) при этом может быть выключен.
//  Запуск:  node mock-server.js
// ============================================================

const http = require('http');

const PORT = 3624;
const ROUTE = decodeURIComponent('/опрос');

function sendJson(res, code, obj) {
  res.writeHead(code, { 'Content-Type': 'application/json; charset=utf-8' });
  res.end(JSON.stringify(obj, null, 2));
}

const server = http.createServer((req, res) => {
  const path = decodeURIComponent(req.url.split('?')[0]);
  console.log(`[MOCK] ${req.method} ${path}`);

  if (req.method === 'GET' && path === '/') {
    res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
    res.end('<h1>Сервер работает</h1><p>Это эмуляция (двойник) сервера варианта 23.</p>');
    return;
  }

  if (path === ROUTE) {
    if (req.method !== 'POST') {
      res.setHeader('Allow', 'POST');
      sendJson(res, 405, { error: 'Метод не разрешён', allowed: 'POST' });
      return;
    }

    let body = '';
    req.on('data', (c) => (body += c));
    req.on('end', () => {
      // заготовленный ответ «неверный тип содержимого»
      const contentType = (req.headers['content-type'] || '').toLowerCase();
      if (!contentType.includes('application/json')) {
        sendJson(res, 415, {
          error: 'Неподдерживаемый тип содержимого',
          expected: 'application/json',
          received: contentType || '(не указан)',
        });
        return;
      }

      let data = {};
      try {
        data = JSON.parse(body || '{}');
      } catch (e) {
        sendJson(res, 400, { error: 'Некорректный формат обмена (JSON не разобран)' });
        return;
      }

      const topic = typeof data['тема'] === 'string' ? data['тема'].trim() : '';
      const score = Number(data['оценка']);
      if (!topic || !Number.isInteger(score) || score < 1 || score > 5) {
        // заготовленный ответ «Пустые данные»
        sendJson(res, 400, {
          error: 'Заполните все поля',
          details: {
            'тема': topic ? 'ok' : 'поле обязательно и не может быть пустым',
            'оценка': 'требуется целое число от 1 до 5',
          },
        });
        return;
      }

      // заготовленный пример «Правильные данные»
      sendJson(res, 200, {
        status: 'ok',
        message: 'Ответ на опрос принят',
        received: {
          id: 1,
          'тема': topic,
          'оценка': score,
          дата: '2025-11-19T09:00:00.000Z',
        },
        total: 1,
      });
    });
    return;
  }

  sendJson(res, 404, { error: 'Не найдено', path });
});

server.listen(PORT, () => {
  console.log(`Эмуляция (двойник) запущена на порту ${PORT}`);
  console.log('Реальный сервер для проверки эмуляции можно не запускать.');
});
