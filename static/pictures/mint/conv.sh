#!/bin/bash

for file in ./*.jpg; do
    # Проверяем, существует ли файл
    if [ -f "$file" ]; then
        # Конвертируем и сжимаем файл
        echo "Обрабатываем файл: $file -> $file"
        convert "$file" -quality 20 "$file"
    else
        echo "Ошибка при обработке файла $file"
    fi
done
