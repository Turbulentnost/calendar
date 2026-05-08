# Backend API

Базовый URL: `http://<host>/`

Для пользовательских запросов нужен заголовок:

```http
Authorization: Token <user_token>
```

Для запросов задач проекта дополнительно нужен проектный JWT:

```http
X-Project-Token: <project_token>
```

## Auth

### Регистрация

`POST /api/v1/auth/register/`

Регистрация создает только аккаунт пользователя. Проект создается или выбирается отдельным запросом после входа.

```json
{
  "nickname": "ivan",
  "password": "12345",
  "first_name": "Иван",
  "last_name": "Иванов"
}
```

Ответ:

```json
{
  "token": "user-token",
  "user": {
    "id": 1,
    "nickname": "ivan",
    "first_name": "Иван",
    "last_name": "Иванов",
    "app_role": "user"
  }
}
```

### Вход пользователя

`POST /api/v1/auth/login/`

```json
{
  "nickname": "ivan",
  "password": "12345"
}
```

Ответ:

```json
{
  "token": "user-token",
  "user": {
    "id": 1,
    "nickname": "ivan",
    "app_role": "user"
  }
}
```

### Выход пользователя

`POST /api/v1/auth/logout/`

Тело не требуется.

Ответ: `204 No Content`.

### Текущий пользователь

`GET /api/v1/auth/me/`

Ответ:

```json
{
  "id": 1,
  "nickname": "ivan",
  "first_name": "Иван",
  "last_name": "Иванов",
  "photo": null,
  "photo_url": null,
  "app_role": "user",
  "department": "",
  "job_title": "",
  "is_staff": false,
  "is_active": true,
  "date_joined": "2026-04-27T10:00:00Z"
}
```

### Обновить профиль

`PATCH /api/v1/auth/me/`

```json
{
  "first_name": "Иван",
  "last_name": "Петров",
  "department": "Разработка",
  "job_title": "Backend developer"
}
```

Ответ: объект текущего пользователя.

### Загрузить фото профиля

`POST /api/v1/auth/me/photo/`

Формат: `multipart/form-data`

```text
photo=<image-file>
```

Ответ:

```json
{
  "id": 1,
  "nickname": "ivan",
  "photo": "/media/users/photos/avatar.jpg",
  "photo_url": "http://<host>/media/users/photos/avatar.jpg"
}
```

### Заменить фото профиля

`PATCH /api/v1/auth/me/photo/`

Формат: `multipart/form-data`, поле `photo`.

Ответ: объект текущего пользователя.

### Удалить фото профиля

`DELETE /api/v1/auth/me/photo/`

Тело не требуется.

Ответ: объект текущего пользователя с `photo: null`.

### Зарегистрировать device token

`POST /api/v1/auth/device-token/`

Нужен auth token пользователя. Backend использует этот токен для push-уведомлений на устройство.

```json
{
  "token": "fcm-device-token",
  "platform": "android"
}
```

Ответ:

```json
{
  "id": 1,
  "token": "fcm-device-token",
  "platform": "android",
  "is_active": true
}
```

### Сменить пароль

`POST /api/v1/auth/change-password/`

```json
{
  "old_password": "12345",
  "new_password": "new-pass"
}
```

Ответ:

```json
{
  "token": "new-user-token"
}
```

### Пользователи

`GET /api/v1/users/`

Ответ:

```json
[
  {
    "id": 1,
    "nickname": "ivan",
    "app_role": "user"
  }
]
```

`POST /api/v1/users/`

```json
{
  "nickname": "user2",
  "password": "12345",
  "first_name": "User",
  "last_name": "Two",
  "app_role": "user"
}
```

Ответ: созданный пользователь.

### Поиск пользователей

`GET /api/v1/users/search/?q=ivan`

Возвращает активных пользователей для приглашений в проект, кроме текущего пользователя.

Ответ:

```json
{
  "results": [
    {
      "id": 2,
      "nickname": "ivan",
      "first_name": "Иван",
      "photo_url": null
    }
  ]
}
```

## Проекты

### Список проектов пользователя

`GET /api/calendar/projects/`

Возвращает проекты, в которых состоит текущий пользователь.

Ответ:

```json
[
  {
    "id": 1,
    "login": "main-office",
    "title": "Основной проект",
    "creator": 1,
    "creator_nickname": "ivan",
    "name": "Комната офиса",
    "image": null,
    "image_url": null,
    "description": "Рабочие задачи отдела",
    "my_project_role": 1.0,
    "room_created_at": "2026-04-27T10:00:00Z"
  }
]
```

### Список всех проектов

`GET /api/calendar/projects/all/`

Возвращает все проекты, которые есть в системе. Используется для общего каталога проектов перед входом по паролю.

Ответ:

```json
[
  {
    "id": 1,
    "login": "main-office",
    "title": "Основной проект",
    "creator": 1,
    "creator_nickname": "ivan",
    "name": "Комната офиса",
    "image": null,
    "image_url": null,
    "description": "Рабочие задачи отдела",
    "my_project_role": null,
    "room_created_at": "2026-04-27T10:00:00Z"
  }
]
```

### Создать проект

`POST /api/calendar/projects/`

Можно отправлять как `application/json`, так и `multipart/form-data` с полем `image`.

```json
{
  "login": "main-office",
  "password": "project-pass",
  "title": "Основной проект",
  "name": "Комната офиса",
  "description": "Рабочие задачи отдела"
}
```

Ответ:

```json
{
  "project_token": "project-jwt",
  "project": {
    "id": 1,
    "login": "main-office",
    "title": "Основной проект"
  }
}
```

Создатель автоматически становится участником проекта с ролью `1.0` - админ проекта. Вернувшийся `project_token` делает этот проект активным для задач.

### Пригласить пользователя в активный проект

`POST /api/calendar/projects/current/invite/`

Нужен `X-Project-Token`. Доступно админу проекта. Создаёт уведомление-приглашение и сразу отправляет push на сохранённые device tokens пользователя. `project_login` и `project_password` обязательны.

```json
{
  "user_id": 2,
  "project_login": "main-office",
  "project_password": "project-pass"
}
```

Ответ:

```json
{
  "id": 1,
  "notification_type": "project_invitation",
  "title": "Приглашение в проект Основной проект",
  "message": "ivan приглашает вас в проект Основной проект. Логин: main-office. Пароль: project-pass.",
  "project_login": "main-office",
  "project_password": "project-pass",
  "project": 1,
  "sender": 1,
  "is_read": false,
  "push_sent": 1
}
```

### Уведомления пользователя

`GET /api/calendar/notifications/`

Возвращает уведомления текущего пользователя, включая приглашения в проекты.

`DELETE /api/calendar/notifications/`

Удаляет все уведомления текущего пользователя из базы.

Ответ:

```json
{
  "deleted": 3
}
```

### Войти в проект / присоединиться

`POST /api/calendar/projects/login/`

Альтернативный endpoint: `POST /api/calendar/projects/join/`

```json
{
  "login": "main-office",
  "password": "project-pass"
}
```

Если пароль верный, пользователь добавляется в участники проекта с ролью `10.0` - обычный участник. Один пользователь может состоять в нескольких проектах.

Ответ:

```json
{
  "project_token": "project-jwt",
  "project": {
    "id": 1,
    "login": "main-office",
    "title": "Основной проект"
  }
}
```

### Текущий проект по токену

`GET /api/calendar/projects/current/`

Нужен `X-Project-Token`. Токен определяет активный проект текущей сессии.

Ответ: объект проекта.

### Участники активного проекта

`GET /api/calendar/projects/current/members/`

Нужен `X-Project-Token`.

Ответ:

```json
[
  {
    "id": 1,
    "project": 1,
    "user": 1,
    "user_nickname": "ivan",
    "user_full_name": "Иван Иванов",
    "role": 1.0,
    "joined_at": "2026-04-27T10:00:00Z"
  }
]
```

### Изменить роль участника

`PATCH /api/calendar/projects/current/members/<user_id>/`

Доступно только админу проекта. В проекте должен остаться хотя бы один админ.

```json
{
  "role": 10.0
}
```

Ответ: обновленный участник проекта.

### Удалить участника

`DELETE /api/calendar/projects/current/members/<user_id>/`

Доступно только админу проекта. Нельзя удалить последнего админа проекта.

Ответ: `204 No Content`.

### Получить проект

`GET /api/calendar/projects/<id>/`

Ответ: объект проекта.

### Обновить проект

`PATCH /api/calendar/projects/<id>/`

```json
{
  "title": "Новое название",
  "description": "Новое описание",
  "password": "new-project-pass"
}
```

Ответ: обновленный проект.

### Удалить проект

`DELETE /api/calendar/projects/<id>/`

Ответ: `204 No Content`.

## Задачи проекта

Для всех запросов нужен `Authorization` и `X-Project-Token`. Смотреть и ставить задачи можно только в активном проекте из `project_token`.

Назначать задачи можно участникам с такой же или большей числовой ролью проекта: `2.0 -> 10.0` можно, `10.0 -> 2.0` нельзя.

### Список задач

`GET /api/calendar/tasks/`

Фильтры: `is_closed`, `importance`, `status`, `assigned_to_me`, `authored_by_me`.

Пример:

`GET /api/calendar/tasks/?is_closed=false&assigned_to_me=true`

Ответ:

```json
[
  {
    "id": 1,
    "project": 1,
    "author": 1,
    "author_nickname": "ivan",
    "assignee": 2,
    "assignee_nickname": "petr",
    "date_from": "2026-04-27",
    "date_to": "2026-04-28",
    "short_description": "Подготовить отчет по задачам",
    "description": "Собрать данные и отправить руководителю.",
    "deadline": "2026-04-28T18:00:00Z",
    "importance": "normal",
    "status": "new",
    "is_closed": false,
    "is_carried_over": false,
    "carried_over_at": null
  }
]
```

### Создать задачу

`POST /api/calendar/tasks/`

```json
{
  "assignee": 2,
  "date_from": "2026-04-27",
  "date_to": "2026-04-28",
  "short_description": "Подготовить отчет по задачам",
  "description": "Собрать данные и отправить руководителю.",
  "deadline": "2026-04-28T18:00:00Z",
  "importance": "normal",
  "status": "new"
}
```

Ответ: созданная задача.

### Получить задачу

`GET /api/calendar/tasks/<id>/`

Ответ: объект задачи.

### Обновить задачу

`PATCH /api/calendar/tasks/<id>/`

```json
{
  "short_description": "Обновить отчет",
  "importance": "high",
  "status": "in_progress"
}
```

Ответ: обновленная задача.

### Удалить задачу

`DELETE /api/calendar/tasks/<id>/`

Ответ: `204 No Content`.

### Закрыть задачу

`POST /api/calendar/tasks/<id>/close/`

Тело не требуется.

Ответ: задача со статусом `done` и `is_closed: true`.

### Открыть задачу заново

`POST /api/calendar/tasks/<id>/reopen/`

Тело не требуется.

Ответ: задача со статусом `in_progress` и `is_closed: false`.

### Перенести задачу на сегодня

`POST /api/calendar/tasks/<id>/carry-over/`

Тело не требуется.

Ответ: задача с `is_carried_over: true`, сегодняшними датами и `importance: critical`.

## Admin API

Нужен пользователь с правами staff/admin.

### Статистика

`GET /api/admin/stats/`

Ответ:

```json
{
  "total_users": 10,
  "superadmins": 1,
  "admins": 2
}
```

### Список пользователей

`GET /api/admin/users/?q=ivan&page=1&page_size=10`

Ответ:

```json
{
  "results": [],
  "page": 1,
  "page_size": 10,
  "total": 0,
  "pages": 1
}
```

### Создать пользователя админом

`POST /api/admin/users/`

```json
{
  "nickname": "manager",
  "password": "12345",
  "first_name": "Manager",
  "app_role": "admin",
  "is_staff": true,
  "is_active": true
}
```

Ответ: созданный пользователь.

### Получить пользователя

`GET /api/admin/users/<id>/`

Ответ: объект пользователя.

### Обновить пользователя

`PUT /api/admin/users/<id>/`

```json
{
  "nickname": "manager",
  "first_name": "Manager",
  "last_name": "",
  "app_role": "admin",
  "department": "Управление",
  "job_title": "Manager",
  "is_staff": true,
  "is_active": true
}
```

Ответ: обновленный пользователь.

### Удалить пользователя

`DELETE /api/admin/users/<id>/`

Ответ: `204 No Content`.

### Сбросить пароль пользователя

`POST /api/admin/users/<id>/reset-password/`

Тело не требуется.

Ответ:

```json
{
  "detail": "Временный пароль сгенерирован.",
  "temp_password": "abc123"
}
```

### Админские задачи

`GET /api/admin/tasks/`

Ответ: список задач.

`POST /api/admin/tasks/`

```json
{
  "title": "Задача",
  "description": "Описание",
  "priority": "medium",
  "deadline": "2026-04-28",
  "assignee": 2
}
```

Ответ: созданная задача.

## Health

`GET /health/`

Ответ:

```text
ok
```
