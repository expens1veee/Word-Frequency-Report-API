import os
import tempfile

from openpyxl import Workbook


def generate_excel(data_generator) -> str:
    """
    Использует openpyxl в режиме write_only=True, 
    что позволяет сбрасывать огромные объемы данных в excel 
    без хранения всего документа в оперативной памяти
    
    На вход принимает генератор, который возвращает кортежи: 
    (словоформа, общее_кол_во, строка_построчных_вхождений)
    
    Возвращает абсолютный путь к сгенерированному файлу .xlsx
    """
    fd, excel_path = tempfile.mkstemp(suffix=".xlsx")
    os.close(fd)
    
    wb = Workbook(write_only=True)
    ws = wb.create_sheet(title="Отчет")
    
    # Заголовки таблицы
    ws.append(["Словоформа", "Кол-во во всём документе", "Кол-во в каждой из строк"])
    
    for row in data_generator:
        ws.append(list(row))
        
    wb.save(excel_path)
    wb.close()
    
    return excel_path
