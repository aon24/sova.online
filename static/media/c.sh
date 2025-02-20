#!/bin/bash

# Проверка наличия FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg не установлен. Установите его и попробуйте снова."
    exit 1
fi

# Проверка количества аргументов
if [ $# -lt 2 ]; then
    echo "Использование: $0 <input_file> <output_file>"
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_FILE="$2"

# Проверка существования входного файла
if [ ! -f "$INPUT_FILE" ]; then
    echo "Входной файл не найден: $INPUT_FILE"
    exit 1
fi

# Получение размера видео
VIDEO_SIZE=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE")

# Вывод информации о видео
echo "Информация о видео:"
echo "Размер: $VIDEO_SIZE"
echo "Длительность: $(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$INPUT_FILE") секунд"

# Запрос параметров от пользователя
#read -p "Укажите желаемый битрейт (в кб/с): " BITRATE
#read -p "Выберите кодек (например, libx264 или h264_omnidir): " CODEC

CODEC="libx264"
BITRATE="2000000"
# Формирование команды FFmpeg
ffmpeg_command=(
    "ffmpeg"
    "-i" "$INPUT_FILE"
    "-c:v" "$CODEC"
    "-crf" "23"  # CRF 23 обычно дает хорошее соотношение качества и скорости
    "-preset" "medium"
    "-b:v" "$BITRATE" 
    "-maxrate" "$BITRATE"
    "-bufsize" "$(expr $BITRATE + $BITRATE)"
    "-c:a" "copy"  # Сохраняем звук без изменения
    "-movflags" "+faststart"
    "$OUTPUT_FILE"
)

# Выполнение команды FFmpeg
if ! "${ffmpeg_command[@]}"; then
    echo "Ошибка при сжатии видео: $?"
    exit 1
else
    echo "Видео успешно сжато и сохранено в $OUTPUT_FILE"
fi
