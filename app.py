import streamlit as st
from PIL import Image, UnidentifiedImageError
import io
import os
import zipfile
import tempfile
import time

# Инициализация session_state для отслеживания состояния
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = None
if "processed" not in st.session_state:
    st.session_state.processed = False
if "custom_size" not in st.session_state:
    st.session_state.custom_size = False
if "custom_width" not in st.session_state:
    st.session_state.custom_width = 1920
if "custom_height" not in st.session_state:
    st.session_state.custom_height = 1080
if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = "file_uploader_" + str(int(time.time()))

# Функция для проверки, является ли файл изображением
def is_image_file(file):
    try:
        with Image.open(file) as img:
            return True
    except UnidentifiedImageError:
        return False

# Функция изменения размера и обрезки изображения
def resize_and_crop(img, target_width, target_height):
    try:
        if img.mode == 'P':
            img = img.convert('RGBA')

        original_width, original_height = img.size
        ratio = max(target_width / original_width, target_height / original_height)
        new_width = int(round(original_width * ratio))
        new_height = int(round(original_height * ratio))
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

        left = (new_width - target_width) / 2
        top = (new_height - target_height) / 2
        right = (new_width + target_width) / 2
        bottom = (new_height + target_height) / 2
        img = img.crop((left, top, right, bottom))

        if img.mode in ('RGBA', 'LA'):
            alpha = img.getchannel('A')
            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, mask=alpha)
            img = bg.convert('RGB')

        return img
    except Exception as e:
        st.error(f"Ошибка при обработке изображения: {e}")
        return None

# Функция для очистки загруженных файлов
def clear_uploads():
    # Генерируем новый ключ для компонента загрузки файлов
    st.session_state.uploader_key = "file_uploader_" + str(int(time.time()))
    st.session_state.uploaded_files = None
    st.session_state.processed = False

# Заголовок приложения
st.title("Пакетное изменение размеров изображений")

# Описание приложения
st.write("Загрузите изображения, выберите желаемое разрешение и нажмите кнопку 'Обработать'.")

# Загрузка изображений с использованием динамического ключа
uploaded_files = st.file_uploader(
    "Выберите изображения", 
    type=["jpg", "jpeg", "png", "bmp", "webp"], 
    accept_multiple_files=True,
    key=st.session_state.uploader_key
)

# Сохраняем загруженные файлы в session_state
if uploaded_files:
    st.session_state.uploaded_files = uploaded_files

# Отображаем количество загруженных файлов
if st.session_state.uploaded_files:
    st.write(f"Загружено файлов: {len(st.session_state.uploaded_files)}")

# Выбор разрешения через радиокнопки 
resolution_options = [
    "1600x832 (видео (1i.jpg, 2i.jpg...) и TN)", 
    "2688x1512 (изображения (1.jpg, 2.jpg...))",
    "Произвольный размер"
]

resolution_option = st.radio(
    "Выберите разрешение:",
    options=resolution_options,
    index=0
)

# Установка флага произвольного размера
st.session_state.custom_size = (resolution_option == "Произвольный размер")

# Получение размеров на основе выбора
if "1600x832" in resolution_option:
    desired_width, desired_height = 1600, 832
elif "2688x1512" in resolution_option:
    desired_width, desired_height = 2688, 1512
else:
    # Поля для ввода произвольных размеров
    col1, col2 = st.columns(2)
    
    # Используем числовые поля ввода для ширины и высоты
    st.session_state.custom_width = col1.number_input(
        "Ширина (пикселей):", 
        min_value=100, 
        max_value=5000, 
        value=st.session_state.custom_width
    )
    
    st.session_state.custom_height = col2.number_input(
        "Высота (пикселей):", 
        min_value=100, 
        max_value=5000, 
        value=st.session_state.custom_height
    )
    
    # Устанавливаем желаемые размеры из пользовательского ввода
    desired_width = st.session_state.custom_width
    desired_height = st.session_state.custom_height

# Вывод выбранных размеров
st.write(f"Выбранное разрешение: {desired_width}x{desired_height}")

# Создаем строку с кнопками
col1, col2 = st.columns(2)

# Кнопка обработки в первой колонке
process_button = col1.button("Обработать")

# Кнопка очистки во второй колонке
if col2.button("Очистить"):
    clear_uploads()
    st.experimental_rerun()

# Обработка изображений при нажатии на кнопку
if process_button and st.session_state.uploaded_files and not st.session_state.processed:
    # Показываем прогресс-бар
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Для сохранения обработанных изображений
    processed_images = []
    filenames = []
    
    # Счетчики для статистики
    processed_count = 0
    total_count = len(st.session_state.uploaded_files)
    
    # Обрабатываем каждое изображение
    for i, uploaded_file in enumerate(st.session_state.uploaded_files):
        if is_image_file(uploaded_file):
            # Обновляем статус
            status_text.text(f"Обрабатываем изображение {i+1} из {total_count}...")
            
            # Преобразуем файл в объект изображения PIL
            image = Image.open(uploaded_file)
            
            # Изменяем размер и обрезаем
            processed_img = resize_and_crop(image, desired_width, desired_height)
            
            if processed_img:
                # Сохраняем обработанное изображение и имя файла
                img_byte_array = io.BytesIO()
                processed_img.save(img_byte_array, format='JPEG')
                processed_images.append(img_byte_array.getvalue())
                filenames.append(uploaded_file.name)
                processed_count += 1
        
        # Обновляем прогресс-бар
        progress_bar.progress((i + 1) / total_count)
    
    # Создаем ZIP-архив с обработанными изображениями
    if processed_images:
        status_text.text("Создаем архив для скачивания...")
        
        # Создаем буфер для ZIP-файла
        zip_buffer = io.BytesIO()
        
        # Создаем ZIP-файл
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i, (img_data, filename) in enumerate(zip(processed_images, filenames)):
                # Получаем имя файла без расширения
                name_without_ext = os.path.splitext(filename)[0]
                # Добавляем файл в архив
                zip_file.writestr(f"{name_without_ext}.jpg", img_data)
        
        # Сбрасываем указатель буфера на начало
        zip_buffer.seek(0)
        
        # Кнопка для скачивания (встроенная в Streamlit)
        st.download_button(
            label="Скачать обработанные изображения",
            data=zip_buffer,
            file_name="processed_images.zip",
            mime="application/zip"
        )
        
        # Показываем статистику
        status_text.text(f"Обработано изображений: {processed_count} из {total_count}")
        
        if processed_count != total_count:
            st.warning("ВНИМАНИЕ: Количество обработанных изображений не совпадает с количеством исходных изображений.")
        
        # Отмечаем, что обработка завершена
        st.session_state.processed = True
    else:
        st.error("Не удалось обработать изображения. Пожалуйста, проверьте, что загруженные файлы являются корректными изображениями.")
        
# Инструкция по использованию кнопки очистки
if st.session_state.processed:
    st.info("Чтобы загрузить новый пакет изображений, нажмите кнопку 'Очистить'.") 