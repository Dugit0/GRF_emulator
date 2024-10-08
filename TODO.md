# TODO
## Известные баги
- [x] Исправить GUI после внедрения `DEFINITION:` и `CALL:` меток
- [x] Добавить 1-2 '\n' после секции `DEFINITION:`
- [ ] Исправить тесты после внедрения `DEFINITION:` и `CALL:` меток
- [ ] Добавить подсветку в окне дебага
- [ ] Исправить лютый трэш с отображением номеров строк (учесть изменения
    размера шрифта, размера окна, скрол окна и ложный перенос строк)
- [ ] Добавить проверку в дебаггере на то, что все функции, которые были
    выбраны все еще есть
- [ ] Исправить баги с пустыми вводами call gramm и сделать critical окна
    в GUI.

## Улучшения поведения
- [ ] Изменение размера шрифта
- [ ] Раскраска GUI
    - [ ] Изменить раздражающую белую полоску в darkorange
    - [ ] Использовать палитру gruvbox dark, а не gruvbox light
- [ ] Добавить красивые кнопки для Run, Debug, DebugMark
- [ ] Сделать комментирование на `Ctrl + /`
- [ ] Сделать многострочное комментирование на `Ctrl + /`
- [ ] Сделать какую-то вменяемую обработку ошибок в GUI
- [ ] F7 не должно сбивать выбранные функции (сделать кнопку "Сбросить все")

## Необходимые дополнения
- [ ] Решить проблему venv/pipfile/poetry
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
- [ ] Переделать минимизацию (зачем?)
- [ ] Дописать юнит тесты (а какие еще нужны?)
- [ ] Решить проблему с тем тестом, который падает (каким?)
