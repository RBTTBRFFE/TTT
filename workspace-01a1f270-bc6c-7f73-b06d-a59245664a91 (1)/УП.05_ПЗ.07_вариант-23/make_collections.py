#!/usr/bin/env python3
# Генерация файлов экспорта коллекций для ПЗ.07, вариант 23
import json, os, time

OUT = os.path.dirname(os.path.abspath(__file__))
ROUTE_ENC = "/%D0%BE%D0%BF%D1%80%D0%BE%D1%81"      # /опрос
NOT_FOUND_ENC = "/%D0%BD%D0%B5%D0%B2%D0%B5%D1%80%D0%BD%D1%8B%D0%B9-%D0%B0%D0%B4%D1%80%D0%B5%D1%81"  # /неверный-адрес

def js(lines):
    return "\n".join(lines)

# ---------------------------------------------------------- Postman v2.1
def request(name, method, path, tests, body=None, desc="", form=None):
    req = {
        "name": name,
        "event": [
            {
                "listen": "test",
                "script": {"type": "text/javascript", "exec": tests.split("\n")},
            }
        ],
        "request": {
            "method": method,
            "header": [],
            "url": {
                "raw": "{{baseUrl}}" + path,
                "host": ["{{baseUrl}}"],
                "path": [p for p in path.split("/") if p],
            },
            "description": desc,
        },
        "response": [],
    }
    if body is not None:
        req["request"]["header"].append({"key": "Content-Type", "value": "application/json", "type": "text"})
        req["request"]["body"] = {
            "mode": "raw",
            "raw": body,
            "options": {"raw": {"language": "json"}},
        }
    if form is not None:
        req["request"]["body"] = {
            "mode": "urlencoded",
            "urlencoded": [{"key": k, "value": v, "type": "text"} for k, v in form],
        }
    return req

REQ_MAIN_TESTS = js([
    "// Автотест по конфигурации К3: код успеха",
    "pm.test(\"Код ответа 200 (успех)\", function () {",
    "    pm.response.to.have.status(200);",
    "});",
])

REQ_EMPTY_TESTS = js([
    "// Негативный сценарий: пустые поля -> 400",
    "pm.test(\"Код ответа 400 (некорректный запрос)\", function () {",
    "    pm.response.to.have.status(400);",
    "});",
])

REQ_404_TESTS = js([
    "// Несуществующий адрес -> 404",
    "pm.test(\"Код ответа 404 (не найдено)\", function () {",
    "    pm.response.to.have.status(404);",
    "});",
])

REQ_405_TESTS = js([
    "// Неверное действие на маршруте отправки -> 405",
    "pm.test(\"Код ответа 405 (метод не разрешён)\", function () {",
    "    pm.response.to.have.status(405);",
    "});",
])

REQ_415_TESTS = js([
    "// Дополнительно: тело не в формате обмена -> 415",
    "pm.test(\"Код ответа 415 (тип содержимого)\", function () {",
    "    pm.response.to.have.status(415);",
    "});",
])

BODY_OK = json.dumps({"тема": "Удобство расписания", "оценка": 5}, ensure_ascii=False, indent=2)
BODY_EMPTY = json.dumps({"тема": "", "оценка": ""}, ensure_ascii=False, indent=2)

items = [
    request("01 Главная страница", "GET", "/", REQ_MAIN_TESTS,
            desc="Проверка, что сервер ПЗ.06 запущен и отвечает на главной странице."),
    request("02 Отправка данных (правильные)", "POST", ROUTE_ENC, REQ_MAIN_TESTS, BODY_OK,
            desc="Маршрут «опрос». Конфигурация К3: тело в формате обмена (application/json), поля «тема», «оценка»."),
    request("03 Пустые данные", "POST", ROUTE_ENC, REQ_EMPTY_TESTS, BODY_EMPTY,
            desc="Негативный сценарий: пустые обязательные поля, ожидаем 400."),
    request("04 Неверный адрес", "GET", NOT_FOUND_ENC, REQ_404_TESTS,
            desc="Адрес, которого нет на сервере, ожидаем 404."),
    request("05 Неверный метод", "GET", ROUTE_ENC, REQ_405_TESTS,
            desc="На маршрут отправки данных пришли действием GET, ожидаем 405."),
    request("06 Доп.: неверный формат тела", "POST", ROUTE_ENC, REQ_415_TESTS,
            form=[("тема", "Удобство расписания"), ("оценка", "5")],
            desc="Дополнительный сценарий: для конфигурации К3 сервер ждёт формат обмена, а данные отправлены как данные формы (application/x-www-form-urlencoded). Ожидаем 415."),
]

# Сохранённые примеры ответов (нужны для эмуляции на основе коллекции)
EXAMPLE_OK = {
    "status": "ok",
    "message": "Ответ на опрос принят",
    "received": {"id": 1, "тема": "Удобство расписания", "оценка": 5, "дата": "2025-11-19T09:00:00.000Z"},
    "total": 1,
}
items[0]["response"].append({
    "name": "Пример: сервер работает (200)",
    "originalRequest": {
        "method": "GET",
        "header": [],
        "url": {"raw": "{{baseUrl}}/", "host": ["{{baseUrl}}"], "path": []},
    },
    "status": "OK", "code": 200, "_postman_previewlanguage": "html",
    "header": [{"key": "Content-Type", "value": "text/html; charset=utf-8"}],
    "cookie": [],
    "body": "<h1>Сервер работает</h1>",
})
items[1]["response"].append({
    "name": "Пример: ответ принят (200)",
    "originalRequest": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": BODY_OK},
        "url": {"raw": "{{baseUrl}}" + ROUTE_ENC, "host": ["{{baseUrl}}"], "path": [ROUTE_ENC.strip("/")]},
    },
    "status": "OK", "code": 200, "_postman_previewlanguage": "json",
    "header": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}],
    "cookie": [],
    "body": json.dumps(EXAMPLE_OK, ensure_ascii=False, indent=2),
})
items[2]["response"].append({
    "name": "Пример: заполните все поля (400)",
    "originalRequest": {
        "method": "POST",
        "header": [{"key": "Content-Type", "value": "application/json"}],
        "body": {"mode": "raw", "raw": BODY_EMPTY},
        "url": {"raw": "{{baseUrl}}" + ROUTE_ENC, "host": ["{{baseUrl}}"], "path": [ROUTE_ENC.strip("/")]},
    },
    "status": "Bad Request", "code": 400, "_postman_previewlanguage": "json",
    "header": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}],
    "cookie": [],
    "body": json.dumps({
        "error": "Заполните все поля",
        "details": {"тема": "поле обязательно и не может быть пустым",
                    "оценка": "требуется целое число от 1 до 5"},
    }, ensure_ascii=False, indent=2),
})
items[3]["response"].append({
    "name": "Пример: не найдено (404)",
    "originalRequest": {
        "method": "GET", "header": [],
        "url": {"raw": "{{baseUrl}}" + NOT_FOUND_ENC, "host": ["{{baseUrl}}"], "path": [NOT_FOUND_ENC.strip("/")]},
    },
    "status": "Not Found", "code": 404, "_postman_previewlanguage": "json",
    "header": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}],
    "cookie": [],
    "body": json.dumps({"error": "Не найдено", "path": "/неверный-адрес"}, ensure_ascii=False, indent=2),
})
items[4]["response"].append({
    "name": "Пример: метод не разрешён (405)",
    "originalRequest": {
        "method": "GET", "header": [],
        "url": {"raw": "{{baseUrl}}" + ROUTE_ENC, "host": ["{{baseUrl}}"], "path": [ROUTE_ENC.strip("/")]},
    },
    "status": "Method Not Allowed", "code": 405, "_postman_previewlanguage": "json",
    "header": [{"key": "Content-Type", "value": "application/json; charset=utf-8"}],
    "cookie": [],
    "body": json.dumps({"error": "Метод не разрешён", "allowed": "POST"}, ensure_ascii=False, indent=2),
})

collection = {
    "info": {
        "_postman_id": "b7c1f2a4-3623-4d5e-9a11-pz07variant23",
        "name": "тест-опрос-23",
        "description": (
            "УП.05, ПЗ.07, вариант 23.\n"
            "Предметная область: О5 «Опрос». Маршрут отправки данных: /опрос (поля «тема», «оценка»).\n"
            "Конфигурация К3: тело в формате обмена (application/json), автотест — код успеха.\n"
            "Дополнительный сценарий 06 показывает разницу форматов тела.\n"
            "Порт: 3623. Стартовый инструмент: А (Postman)."
        ),
        "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
    },
    "item": items,
    "event": [
        {"listen": "prerequest", "script": {"type": "text/javascript", "exec": [""]}},
        {"listen": "test", "script": {"type": "text/javascript", "exec": [""]}},
    ],
    "variable": [{"key": "baseUrl", "value": "http://localhost:3623", "type": "string"}],
}

with open(os.path.join(OUT, "тест-опрос-23.postman_collection.json"), "w", encoding="utf-8") as f:
    json.dump(collection, f, ensure_ascii=False, indent=2)

# Окружение Postman
environment = {
    "id": "e3a9c1b0-0000-4000-8000-000000362300",
    "name": "опрос-23 локально",
    "values": [
        {"key": "baseUrl", "value": "http://localhost:3623", "type": "default", "enabled": True},
        {"key": "mockUrl", "value": "http://localhost:3624", "type": "default", "enabled": True},
        {"key": "route", "value": "опрос", "type": "default", "enabled": True},
    ],
    "_postman_variable_scope": "environment",
    "_postman_exported_at": "2025-11-19T09:00:00.000Z",
    "_postman_exported_using": "Postman/11.0.0",
}
with open(os.path.join(OUT, "тест-опрос-23.postman_environment.json"), "w", encoding="utf-8") as f:
    json.dump(environment, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------- Insomnia v4
now = int(time.time() * 1000)
wrk = "wrk_pz07_variant23"
env = "env_pz07_variant23"

def ins_req(rid, name, method, url, body=None, desc="", sort=0):
    r = {
        "_id": rid,
        "parentId": wrk,
        "modified": now,
        "created": now,
        "name": name,
        "description": desc,
        "url": url,
        "name": name,
        "method": method,
        "body": {},
        "parameters": [],
        "headers": [],
        "authentication": {},
        "metaSortKey": sort,
        "isPrivate": False,
        "settingStoreCookies": True,
        "settingSendCookies": True,
        "settingDisableRenderRequestBody": False,
        "settingEncodeUrl": True,
        "settingRebuildPath": True,
        "settingFollowRedirects": "global",
        "_type": "request",
    }
    if body is not None:
        r["body"] = {"mimeType": "application/json", "text": body}
        r["headers"] = [{"name": "Content-Type", "value": "application/json"}]
    return r

resources = [
    {
        "_id": wrk,
        "parentId": None,
        "modified": now,
        "created": now,
        "name": "тест-опрос-23 (Insomnia)",
        "description": "Вариант 23, О5 «Опрос», К3, порт 3623",
        "scope": "collection",
        "_type": "workspace",
    },
    {
        "_id": env,
        "parentId": wrk,
        "modified": now,
        "created": now,
        "name": "опрос-23 локально",
        "data": {"baseUrl": "http://localhost:3623", "mockUrl": "http://localhost:3624"},
        "dataPropertyOrder": {"&": ["baseUrl", "mockUrl"]},
        "color": None,
        "isPrivate": False,
        "metaSortKey": now,
        "_type": "environment",
    },
    ins_req("req_pz07_01", "01 Главная страница", "GET", "{{ _.baseUrl }}/",
            desc="Сервер ПЗ.06 отвечает", sort=-6),
    ins_req("req_pz07_02", "02 Отправка данных (правильные)", "POST",
            "{{ _.baseUrl }}/%D0%BE%D0%BF%D1%80%D0%BE%D1%81", BODY_OK,
            desc="К3: формат обмена (JSON), поля тема/оценка", sort=-5),
    ins_req("req_pz07_03", "03 Пустые данные", "POST",
            "{{ _.baseUrl }}/%D0%BE%D0%BF%D1%80%D0%BE%D1%81", BODY_EMPTY,
            desc="Негативный сценарий: пустые поля -> 400", sort=-4),
    ins_req("req_pz07_04", "04 Неверный адрес", "GET",
            "{{ _.baseUrl }}" + NOT_FOUND_ENC,
            desc="Несуществующий адрес -> 404", sort=-3),
    ins_req("req_pz07_05", "05 Неверный метод", "GET",
            "{{ _.baseUrl }}/%D0%BE%D0%BF%D1%80%D0%BE%D1%81",
            desc="GET на маршрут отправки -> 405", sort=-2),
]

insomnia = {
    "_type": "export",
    "__export_format": 4,
    "__export_date": "2025-11-19T09:00:00.000Z",
    "__export_source": "insomnia.desktop.app:v2024.5.6",
    "resources": resources,
}
with open(os.path.join(OUT, "тест-опрос-23_insomnia.json"), "w", encoding="utf-8") as f:
    json.dump(insomnia, f, ensure_ascii=False, indent=2)

print("OK:", os.listdir(OUT))
