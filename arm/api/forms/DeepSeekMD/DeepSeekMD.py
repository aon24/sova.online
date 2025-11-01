import os
import json
from django.conf import settings
from arm.api.forms.classPage import Page
from arm.api.forms.formTools import style, _div, _field
from arm.tools.first import err
from .md_converter import md_to_xml_structure


class DeepSeekMD(Page):
    title = 'MD File Viewer'
    form = 'deepseek_md'

    def __init__(self, request):
        # self.jsCssUrl = [f'/api/jsv?forms/{self.form}/{self.form}.js']
        super().__init__(request)

    def page(self, request):
        """Формирование структуры формы для отображения MD-файла"""
        return self.docPage([_div(children=[
            _div(**style(padding='10px', borderBottom='1px solid #ccc', background='#f5f5f5'),
                 children=[_field('fileName', 'fd', **style(fontWeight='bold', fontSize='16px'))]
                 ),
            _div(**style(height='calc(100vh - 60px)', overflow='auto', padding='10px'),
                 children=[_field('content', 'json', **style(width='100%', minHeight='100%'))]
                 )
        ])])

    def queryOpen(self, request):
        """Загрузка и преобразование MD-файла"""
        try:
            # Получаем имя файла из параметров запроса или используем по умолчанию
            file_name = request.dcUK.fileName or 'Sova-description.md'

            # Устанавливаем имя файла в поле
            request.dcUK.doc.fileName = file_name

            # Получаем полный путь к файлу
            file_path = os.path.join(settings.BASE_DIR, 'doc', file_name)

            # Читаем содержимое файла
            content = ""
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"Файл {file_path} не найден"

            # Преобразуем содержимое MD-файла в XML-подобную структуру
            xml_structure = md_to_xml_structure(content)

            # Записываем результат в поле content как JSON-строку
            request.dcUK.doc.content = json.dumps(xml_structure, ensure_ascii=False)

        except Exception as e:
            err(f"Error in DeepSeekMD.queryOpen: {str(e)}", cat=self.form)
            request.dcUK.doc.fileName = f"Ошибка: {file_name}"
            request.dcUK.doc.content = json.dumps({
                "_teg": "div",
                "attributes": {
                    "style": {
                        "color": "red",
                        "padding": "20px",
                        "fontFamily": "monospace"
                    }
                },
                "text": f"Ошибка загрузки файла: {str(e)}"
            }, ensure_ascii=False)
