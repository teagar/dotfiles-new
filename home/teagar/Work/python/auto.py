import pytesseract
from PIL import Image
from subprocess import check_output
import time

# Defina as coordenadas da Ã¡rea de interesse
x1, y1, x2, y2 = 100, 200, 300, 400  # Substitua pelos valores apropriados

# Defina as coordenadas para os cliques
x_middle, y_middle = 200, 300  # Substitua pelos valores apropriados
x_top_center, y_top_center = 200, 100  # Substitua pelos valores apropriados

while True:
    # Capture um screenshot da Ã¡rea especificada usando adb
    check_output(["adb", "shell", "screencap", "-p", "/sdcard/screenshot.png"])
    check_output(["adb", "pull", "/sdcard/screenshot.png", "."])

    # Recorte o screenshot para a Ã¡rea desejada
    image = Image.open("screenshot.png")
    area_of_interest = image.crop((x1, y1, x2, y2))

    # Realize OCR na imagem recortada
    text = pytesseract.image_to_string(area_of_interest)

    # Verifique se o texto Ã© "perfect!"
    if "perfect!" in text.lower():
        print("It's perfect!")
    else:
        # Simule um toque no meio da tela
        check_output(["adb", "shell", "input", "tap", str(x_middle), str(y_middle)])
        # Simule um toque no topo do centro da tela
        check_output(["adb", "shell", "input", "tap", str(x_top_center), str(y_top_center)])

    # Adicione um intervalo para evitar verificaÃ§Ãµes muito frequentes
    time.sleep(1)
