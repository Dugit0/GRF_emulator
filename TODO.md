# TODO
## Известные баги
- [ ] Добавить подсветку в окне дебага
- [ ] После добавления QThreads если подолбить по кнопкам F5 и F8 приложение
    падает
- [ ] Исправить лютый трэш с отображением номеров строк (учесть изменения
    размера шрифта, размера окна, скрол окна и ложный перенос строк)
- [ ] Добавить проверку в дебаггере на то, что все функции, которые были
    выбраны все еще есть
- [ ] Исправить баги с пустыми вводами call gramm и сделать critical окна
    в GUI.
- [ ] Ужасное отображение Help (перевести на webbrowser)

## Улучшения поведения
- [ ] Просто перевести документацию в tex/pdf и открывать ее в браузере 
    (аналогично с README)
- [ ] Изменение размера шрифта
- [ ] Раскраска GUI
    - [ ] Изменить раздражающую белую полоску в darkorange
    - [ ] Использовать палитру gruvbox dark, а не gruvbox light
    - [ ] Отсмотреть цветовые темы, удалить те, которые плохо отображаются
    - [ ] Понять, нужно ли запекать ресурсы для цветовых тем
    - [ ] Вернуть тему darkorange
- [ ] Добавить красивые кнопки для Run, Debug, DebugMark
- [ ] Smarttabs
- [ ] Tab -> 4 пробела (сделать и их удаление при нажатии Backspace по 4 за
    одно нажатие)
- [ ] Сделать `run_counter` при вызове нового запуска
- [ ] Читать в UTF-8 в grfemulator.core
- [ ] Подсветка комментариев
- [ ] Сделать индикатор выполнения работы
- [ ] Сделать комментирование на `Ctrl + /`
- [ ] Сделать многострочное комментирование на `Ctrl + /`
- [ ] Сделать какую-то вменяемую обработку ошибок в GUI
- [ ] F7 не должно сбивать выбранные функции (сделать кнопку "Сбросить все")

## Улучшения ядра
- [ ] Оппортунистическая оптимизация
- [ ] Разворачивание рекурсии в цикл
- [ ] Задокументировать флаги и протестировать их
- [ ] Обработка ошибок

## Необходимые дополнения
- [ ] Решить проблему venv/pipfile/poetry
- [ ] Исправить кодстайл во всем проекте
- [ ] Сделать нормальные комментарии
- [ ] Написать документацию
- [ ] Создание колеса
- [ ] Автоматизация тестирования и сборки
- [ ] Публикация в PyPI

## Возможные теоретические проблемы
- [ ] Разобраться в алгоритме Эрли и ограничениях на построение LALR(1) анализатора
- [ ] Сделать список на функциях
- [ ] Сделать функцию поиска делителя
- [ ] Сделать алгоритм Евклида (если это возможно)

## Что?
- [ ] Вернуть оптимизацию после дебага (какую?) (проверить, что я этого не
    сделал)
- [ ] Решить проблему с местоположением лога (лога?)
- [ ] Дописать юнит тесты (а какие еще нужны?)

## Сделано
- [x] Исправить GUI после внедрения `DEFINITION:` и `CALL:` меток
- [x] Добавить 1-2 '\n' после секции `DEFINITION:`
- [x] Добавить разных цветовых тем (минимум светлую и темную)
    (использовать QSettings)
- [x] Исправить тесты после внедрения `DEFINITION:` и `CALL:` меток
- [x] Переделать минимизацию
- [x] Решить проблему с тем тестом, который падает
- [x] QThreads
