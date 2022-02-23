import cv2
import numpy as np
from imutils.perspective import four_point_transform
import pytesseract

IMAGE_HEIGHT = 1200
IMAGE_WIDTH = 1200

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def parse_data(text:str) -> dict:
    """
    This function is used to parse the data that's been extracted from the AI model.

    Params:

    text -> Raw String that needs to be parsed

    Returns:

    {
        "name" : ...,
        "level" : ...,
        "campus" : ...,
    }

    """
    text = text.strip().rstrip()
    lines = text.split("\n")
    
    temp = list()
    values = dict()

    for line in lines:
        if line == '':
            pass 
        else:
            temp.append(line)

    for each_value in temp:
        if each_value[0:4] == "Name":
            values["name"] = each_value[5:]
        if each_value[0:5] == "Level":
            values["level"] = each_value[5:]
        if each_value[0:6] == "Campus":
            values["campus"] = each_value[6:]

    for key,value in values.items():
        temp_=str()
        for each_character in value:
            if each_character == ' ':
                temp_ += " "
            if each_character.isalpha():
                temp_ += each_character

        values[key] = temp_.strip().rstrip()

    return values

def get_paper(image:np.array,edges:list) -> np.array:
    """
    This function takes a image and edges and performs the four-point transformation seperate the image from the background

    Params:
    
    image -> The base image
    edges -> list of detected edges

    Returns:

    An image after the four-point transformation.

    """
    cropped_image  = four_point_transform(image, edges.reshape(4, 2))
    return cropped_image


def get_name_box(image:np.array) -> dict:
    """
    This method iterates over the name ROI and checks if the name data can be distracted or not.

    Params:

    image -> The base image

    Returns:

    A dict containing the name,level and campus

    """

    kernel = np.array(
        [[0, -1, 0],
        [-1, 5,-1],
        [0, -1, 0]])
    
    start_x = 10
    start_y = 140
    end_x = 350
    end_y = 230

    for i in range(20):
        name = image[start_y:end_y,start_x:end_x]
        image_sharp = cv2.filter2D(src=name, ddepth=-1, kernel=kernel)
        name = cv2.cvtColor(image_sharp, cv2.COLOR_BGR2GRAY)
        cv2.imshow("Name ROI",name)
        cv2.waitKey(100)
        data = parse_data(pytesseract.image_to_string(name))
        try:
            if data["name"]:
                return data
        except Exception as e:
            pass

        start_x += 10
        start_y += 10
        end_x += 10
        end_y += 10

        if i > 10:
            start_x -= 40
            start_y -= 40
            end_x -= 40
            end_y -= 40
    
    return "Error"

def get_marks_table(image:np.array) -> np.array:
    """
    This function checks for the marks table

    Params:

    image -> The base image

    Returns:

    A image containing the marks table

    """
    start_x = 30
    start_y = 300
    end_x = -1
    end_y = -1

    for i in range(20):
        marks_table = image[start_y:end_y,start_x:end_x]
        if pytesseract.image_to_string(marks_table):
            kernel = np.array(
                [[0, -1, 0],
                [-1, 5,-1],
                [0, -1, 0]])

            image_sharp = cv2.filter2D(src=marks_table, ddepth=-1, kernel=kernel)
            marks_table = cv2.cvtColor(image_sharp, cv2.COLOR_BGR2GRAY)
            return marks_table

        else:
            start_x += 10
            start_y += 10
            end_y += 10

            if i > 10:
                start_x -= 40
                start_y -= 40
                end_y -= 40


    return "Done"

def get_rows(image:np.array) -> list:
    """
    This function takes the marks table and, further segments the data into each row.

    Params:
    image -> An image containing the marks table

    Returns:

    A list of each row that has extractable text

    """
    start = 0
    end = 45

    rows = list()
    each_row = image[start:end,0:1100]

    threshold_of_word_count = 10
    err_count = 0 

    for i in range(25):
        context = pytesseract.image_to_string(each_row).strip().rstrip()
        word = str()
        for each_char in context:
            if each_char == "" or each_char == " " or each_char == "\n":
                pass
            else:
                word += each_char

        if word and len(word) > threshold_of_word_count:
            err_count = 0
            rows.append(each_row)
            start = end 
            end += int(40 + (0.15* i))
            each_row = image[start:end,0:1100]
            cv2.imshow("Rows",each_row)
            cv2.waitKey(500)
        else:
            print("Can't detect anything")
            err_count += 1
            if err_count >= 3:
                print("Couldn't detect anything thrice in a row")
                return rows
            start += 5
            end += 5
            each_row = image[start:end,0:1100]
            cv2.imshow("Rows",each_row)
            cv2.waitKey(500)

    return rows

def get_contours(image:np.array) -> list:
    """
    This function is used to get contours from the image

    Params:
    
    image -> The base image

    Returns:

    A list of all contours

    """
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image,(0,0,100),(179,30,255))
    result = cv2.bitwise_and(image, image, mask=mask)

    result_rgb = cv2.cvtColor(result,cv2.COLOR_HSV2BGR)
    result_gray = cv2.cvtColor(result_rgb,cv2.COLOR_BGR2GRAY)

    contours, _ = cv2.findContours(result_gray, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    return contours


def get_subject_from_row(image:np.array) -> list:
    """
    This function takes the image of a row and further segments it to each subject name only

    Params:

    image -> Image of the row

    Returns:

    An array of segmented image.

    """
    start_x = 20
    end_x = 520

    subject = image[0:-1,start_x:end_x]
    subject = cv2.resize(subject,(500,40))

    return subject


def get_data():
    """

    This is the main method that calls all other functions.

    """

    try:
        base_image = cv2.imread(f"./samples/good2.jpg")  
        resized_image = cv2.resize(base_image,(IMAGE_HEIGHT,IMAGE_WIDTH))  
    except Exception as e:
        # no file is found.
        pass
    else:
        contours = get_contours(resized_image)
        
        for each_contour in contours:
            if cv2.contourArea(each_contour) > 100000:
                perimeter = cv2.arcLength(each_contour, True)
                approximate = cv2.approxPolyDP(each_contour, 0.02 * perimeter, True)

                if len(approximate) == 4:
                    paper_boundaries = approximate
                    (x,y,w,h) = cv2.boundingRect(each_contour)
                    cv2.rectangle(resized_image,(x,y),(x+w,y+h),(0,255,0),2)
                    image = get_paper(resized_image,paper_boundaries)

                    data = get_name_box(image)
                    print(data)

                    marks_table = get_marks_table(image)

                    rows = get_rows(marks_table)

                    for each_row in rows:
                        subject = get_subject_from_row(each_row)

                        full_marks_asst = each_row[0:-1,520:600]
                        full_marks_prac = each_row[0:-1,600:680]
                        pass_marks_asst = each_row[0:-1,680:760]
                        pass_marks_prac = each_row[0:-1,760:840]
                        marks_obtained_asst = each_row[0:-1,840:920]
                        marks_obtained_prac = each_row[0:-1,920:1060]



                        print(pytesseract.image_to_string(subject))
                        print(pytesseract.image_to_string(full_marks_prac))
                        print(pytesseract.image_to_string(full_marks_asst))
                        print(pytesseract.image_to_string(pass_marks_prac))
                        print(pytesseract.image_to_string(pass_marks_asst))
                        print(pytesseract.image_to_string(marks_obtained_prac))
                        print(pytesseract.image_to_string(marks_obtained_prac))
                        cv2.imshow("Row",each_row)
                        cv2.imshow("FMA",full_marks_asst)
                        cv2.imshow("FMP",full_marks_prac)
                        cv2.imshow("PMA",pass_marks_asst)
                        cv2.imshow("PMP",pass_marks_prac)
                        cv2.imshow("MOA",marks_obtained_asst)
                        cv2.imshow("MOP",marks_obtained_prac)
                        cv2.waitKey(100)
                        

if __name__ == "__main__":
    get_data()