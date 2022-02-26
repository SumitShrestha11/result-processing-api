import pytesseract
import cv2
import easyocr
image = cv2.imread(r"./f{counter}.jpg",0)



code = image[0:-1, 500:560]
reader = easyocr.Reader(['ch_sim','en']) # need to run only once to load model into memory
result = reader.readtext(code)
cv2.imshow("test",code)
cv2.waitKey(1000)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

print(pytesseract.image_to_string(code))
