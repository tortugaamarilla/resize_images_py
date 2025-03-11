# Приложение для пакетного изменения размеров изображений

Это приложение на базе Streamlit позволяет загружать несколько изображений и изменять их размеры до одного из двух стандартных форматов:
- 1600x832 пикселей (для видео и TN)
- 2688x1512 пикселей (для полноразмерных изображений)

## Установка

1. Убедитесь, что у вас установлен Python 3.7 или выше.
2. Клонируйте этот репозиторий или загрузите его файлы.
3. Установите необходимые зависимости:

```bash
pip install -r requirements.txt
```

## Запуск приложения

Чтобы запустить приложение, выполните следующую команду в терминале:

```bash
streamlit run app.py
```

Приложение откроется в вашем веб-браузере по адресу `http://localhost:8501`.

## Использование

1. Загрузите изображения с помощью кнопки "Browse files" или перетаскивания файлов.
2. Выберите нужное разрешение с помощью ползунка:
   - 1600x832 (видео (1i.jpg, 2i.jpg...) и TN)
   - 2688x1512 (изображения (1.jpg, 2.jpg...))
3. Нажмите кнопку "Обработать".
4. После обработки всех изображений вы сможете скачать архив с обработанными фотографиями.

## Особенности

- Приложение автоматически масштабирует и обрезает изображения для достижения требуемых пропорций.
- Прозрачные фоны (в PNG и других форматах с альфа-каналом) заменяются белым фоном.
- Все изображения конвертируются в формат JPEG.
- Результаты предоставляются в ZIP-архиве для удобства скачивания. 