# md_converter.py
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from arm.tools.first import err


def md_to_xml_structure(md_content):
    """
    Преобразует Markdown содержимое в XML-подобную структуру используя Pygments
    """
    try:
        # Используем Pygments для преобразования MD в HTML
        lexer = get_lexer_by_name('markdown')
        formatter = HtmlFormatter(
            full=True,  # Генерировать полный HTML документ
            style='default',
            noclasses=False,  # Использовать CSS классы
            linenos=False  # Без номеров строк
        )

        html_content = highlight(md_content, lexer, formatter)

        # Преобразуем HTML в XML-структуру
        return _html_to_xml_structure(html_content)

    except Exception as e:
        err(f"Ошибка преобразования Markdown: {str(e)}", cat="md_converter")
        return {
            "_teg": "div",
            "attributes": {
                "style": {
                    "color": "red",
                    "fontWeight": "bold",
                    "padding": "20px"
                }
            },
            "text": f"Ошибка преобразования Markdown: {str(e)}"
        }


def _html_to_xml_structure(html_content):
    """
    Преобразует HTML содержимое в XML-подобную структуру для поля типа 'json'
    """
    # Создаем базовую структуру
    structure = {
        "_teg": "div",
        "attributes": {
            "style": {
                "fontFamily": 'Arial, sans-serif',
                "lineHeight": '1.6',
                "color": '#333',
                "padding": '20px',
                "maxWidth": '800px',
                "margin": '0 auto'
            }
        },
        "children": []
    }

    # Pygments уже преобразовал MD в HTML, просто оборачиваем результат
    structure['children'].append({
        "_teg": "div",
        "attributes": {
            "dangerouslySetInnerHTML": {
                "__html": html_content
            }
        }
    })

    return structure
