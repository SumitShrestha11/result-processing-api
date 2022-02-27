from distutils.command import config
import pytesseract
import cv2
import numpy as np
img = cv2.imread(r"./f{counter}.jpg",0)
kernel = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])
img = cv2.filter2D(src=img, ddepth=-1, kernel=kernel)
blur = cv2.GaussianBlur(img,(5,5),0)
kernel = np.array([[0, -1, 0],
                   [-1, 5,-1],
                   [0, -1, 0]])
image_sharp = cv2.filter2D(src=blur, ddepth=-1, kernel=kernel)

ret, otsu = cv2.threshold(image_sharp,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

marks = otsu[0:-1, 520:-1]
fma = otsu[0:-1,520:590]
fmf = otsu[0:-1,590:630]
pma = otsu[0:-1,650:700]
pmf = otsu[0:-1,720:780]
oma = otsu[0:-1,780:850]
omf = otsu[0:-1,950:1000]
# cv2.imshow("test",fma)
# cv2.waitKey(1000)
# cv2.imshow("test",fmf)
# cv2.waitKey(1000)
cv2.imshow("test",marks)
cv2.waitKey(1000)
# cv2.imshow("test",pmf)
# cv2.waitKey(1000)
# cv2.imshow("test",oma)
# cv2.waitKey(1000)
# cv2.imshow("test",omf)
# cv2.waitKey(1000)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

conf = r'--oem 1 --psm 6 digits'
marks_num=[]
marks = pytesseract.image_to_string(marks, config=conf)
for word in marks.split():
    if word.isdigit():
        marks_num.append(int(word))
print(marks_num)