from pickletools import pyset
import time
from unittest import result
import cv2
import numpy as np
from imutils.perspective import four_point_transform
import pytesseract
import json
import os 


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
    values = {
        "name":None,
        "level":None,
        "campus":None,
    }

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
        try:
            for each_character in value:
                if each_character == ' ':
                    temp_ += " "
                if each_character.isalpha():
                    temp_ += each_character

            values[key] = temp_.strip().rstrip()
        except:
            pass

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
        # cv2.imshow("Name ROI",name)
        # cv2.waitKey(100)
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

def get_crn_box(image):

    kernel = np.array(
        [[0, -1, 0],
        [-1, 5,-1],
        [0, -1, 0]])
    
    start_x = 600
    start_y = 140
    end_x = 1100
    end_y = 230

    for i in range(20):
        name = image[start_y:end_y,start_x:end_x]
        image_sharp = cv2.filter2D(src=name, ddepth=-1, kernel=kernel)
        name = cv2.cvtColor(image_sharp, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("CRN",name)
        # cv2.waitKey(100)

        data = pytesseract.image_to_string(name)
        data = data.strip().rstrip()
        data = data.split("\n")


        req_data = {
            "CRN":None,
            "Exam Roll":None,
        }
        for each_data in data:
            if "Exam" in each_data.split(" ") or "Exam " in each_data.split(" "):
                req_data["Exam Roll"] = each_data.split(" ")[-1]

            if "CRN" in each_data.split(" ") or "CRN:" in each_data.split(" ") or "CRN:-" in each_data.split(" "):
                req_data["CRN"] = each_data.split(" ")[-1]
        

        start_x += 10
        start_y += 10
        end_x += 10
        end_y += 10

        if i > 10:
            start_x -= 40
            start_y -= 40
            end_x -= 40
            end_y -= 40

        if req_data["CRN"] is not None and req_data["Exam Roll"] is not None:
            return req_data
        
        
    return req_data
    

def get_subject_code(image):
    kernel = np.array(
        [[0, -1, 0],
        [-1, 5,-1],
        [0, -1, 0]])

    start_x = 20
    end_x = 130

    start_y = 0
    end_y = -1

    subject = image[start_y:end_y,start_x:end_x]

    _,thres = cv2.threshold(subject,200,255,cv2.THRESH_BINARY) 
    thres = cv2.filter2D(src=thres, ddepth=-1, kernel=kernel)
    thres = cv2.blur(thres, (2,2))
    thres = cv2.filter2D(src=thres, ddepth=-1, kernel=kernel)
   
    data = pytesseract.image_to_string(thres)
    data = data.strip().rstrip()

    if data == "":
        return None


    if len(data) < 5:
        return None
    else:
        s = str()

        for i in data:
            if i == "S" or i == "s":
                s += "5"
            else:
                s+= i

        return s


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
            # cv2.imshow("Rows",each_row)
            # cv2.waitKey(500)
        else:
            # print("Can't detect anything")
            err_count += 1
            if err_count >= 3:
                # print("Couldn't detect anything thrice in a row")
                return rows
            start += 5
            end += 5
            each_row = image[start:end,0:1100]
            # cv2.imshow("Rows",each_row)
            # cv2.waitKey(500)

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
    ret_data = {
        "Subject" : None,
        "code" : None,
    }

    start_x = 90
    end_x = 530

    kernel = np.array(
        [[0, -1, 0],
        [-1, 5,-1],
        [0, -1, 0]])

    subject = image[0:-1,start_x:end_x]
    
    
    ret_data["code"] = get_subject_code(image)
    
    _,thres = cv2.threshold(subject,200,255,cv2.THRESH_BINARY) 
    thres = cv2.filter2D(src=thres, ddepth=-1, kernel=kernel)

    data = pytesseract.image_to_string(thres)
    data = data.strip().rstrip()
    s = str()

    for i in data:
        if i.isnumeric():
            pass
        else:
            s+= i


    s = s.strip().rstrip()
    x = s.split(" ")
    if len(x[0]) < 3:
        s = " ".join(x[1:])


    if "Subjects" in data or "Code" in data or "Title" in data:
        pass
    else:
        ret_data["Subject"] = s
    return ret_data

def get_grand_total(image):
    start_x = 600
    end_x = 1100
    start_y = 950
    end_y = 1100


    for i in range(20):
        subject = image[start_y:end_y,start_x:end_x]
        data = pytesseract.image_to_string(subject)
        data = data.rstrip().strip().split("\n")
        
        if "Grand Total" in data:
            for each in data:
                try:
                    int(each)
                except:
                    pass
                else:
                    return {"Total":int(each)}

        else:
            start_x += 5
            start_y += 5
            end_y += 5

            if i > 10:
                start_x -= 20
                start_y -= 20
                end_y -= 20
    
    return {"Total":0}

def get_marks(image):
    ret = {
        "full_marks_asst":0,
        "full_marks_prac":0, 
        "pass_marks_asst":0, 
        "pass_marks_prac":0, 
        "marks_obtained_asst":0,
        "marks_obtained_prac":0,
        "total":0,
    }

    kernel = np.array(
        [[0, -1, 0],
        [-1, 5,-1],
        [0, -1, 0]])
    
    start_x = 540
    end_x = 630 
    start_y = 10
    end_y = 45

    true_start_x = start_x
    true_end_x = end_x
    true_start_y = start_y 
    true_end_y = end_y

    x = list()
    x = 7 * [0]
    for j in range(7):
        for i in range(20):
            try:
                conf_ = r'--oem 1 --psm 6 digits'
                marks = image[start_y:end_y,start_x:end_x]
                _,thres = cv2.threshold(marks,200,255,cv2.THRESH_BINARY) 
                thres = cv2.filter2D(src=thres, ddepth=-1, kernel=kernel)
                thres = cv2.blur(thres, (2,2))
                thres = cv2.filter2D(src=thres, ddepth=-1, kernel=kernel)
                thres = cv2.blur(thres, (2,2))
                data = pytesseract.image_to_string(thres,config=conf_)
                data = data.rstrip().strip()

            except Exception as e:
                pass
            
            if data:
                s = str()
                t = str(data)
                for each in t:
                    if each.isnumeric():
                        s += each 
                    if each == "s" or each == "S":
                        s += "5"
                try:
                    x[j] = int(s)
                    break
                except:
                    pass
                
            else:
                if i < 10:
                    start_x -= 2
                    end_x -= 2
                    start_y -= 1 
                    end_y -= 1
                else:
                    start_x += 3
                    end_x += 3 
                    start_y += 2 
                    end_y += 2



        ret["full_marks_asst"] = x[0]
        ret["full_marks_prac"] = x[1]
        ret["pass_marks_asst"] = x[2]
        ret["pass_marks_prac"] = x[3]  
        ret["marks_obtained_asst"] = x[4]
        ret["marks_obtained_prac"] = x[5]
        ret["total"] = x[6]


        start_x = true_start_x
        end_x = true_end_x 
        start_y = true_start_y
        end_y = true_end_y

        start_x += int(65 + j *1.25)
        end_x += int(65 + j *1.25)
        start_y += int(1) 
        end_y += int(1)

        true_start_x = start_x 
        true_end_x = end_x 
        true_start_y = start_y
        true_end_y = end_y
    return ret


def get_yearpart(image):
    year_p = image[250:295,50:400]
    data = pytesseract.image_to_string(year_p)
    data = data.strip().rstrip()
    data = data.split("\n")
    for i in data:
        if len(i) > 10:
            j = i.split("-")
            return j[-1]
    return 0

def get_result(image):
    res = image[1000:1100,700:-1]
    data = pytesseract.image_to_string(res)
    data = data.strip().rstrip()
    data = data.split("\n")
    for i in data:
        j = i.split(" ")
        for k in j:
            if k == "Result" or k == "result":
                return j[-1]



def get_data():
    """

    This is the main method that calls all other functions.

    """
    counter = 0 
    try:
        # base_image = cv2.imread(f"./../samples/good3.jpg")
        base_image = cv2.imread(f"./uploads/result.jpg") 
        resized_image = cv2.resize(base_image,(IMAGE_HEIGHT,IMAGE_WIDTH))  
    except Exception as e:
        # no file is found.
        pass
    else:
        response = {"studentInfo":{}, "tableData":[], "summary":{}}
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
                    year_part = get_yearpart(image)
                    crn = get_crn_box(image)
                    grand_total = get_grand_total(image)
                    result = get_result(image)
                    
                    response["studentInfo"] = {
                        "name":data["name"],
                        "level":data["level"],
                        "campus":"Thapathali Campus",
                        "yearpart": year_part,
                        "examRollNo":crn["Exam Roll"],
                        "CRN":crn["CRN"],
                        "TURegdNo":None,
                        "programme": "Computer Engineering",
                        }
                    response["summary"] = {
                        "marksEnteredBy":None,
                        "verifiedBy":None,
                        "date":None,
                        "grandTotal":grand_total["Total"],
                        "result":result,
                    }
                    
                    #print(response)
                    # print(crn)#CRN,Exam Roll
                    # print(data)#name,level,campus
                    #print(grand_total)#Total

                    marks_table = get_marks_table(image)
                    rows = get_rows(marks_table)

                    for each_row in rows:
                        counter += 1
                        data = {
                            "subject":None,
                            "code": None,
                            "full_marks_asst":0,
                            "full_marks_prac":0,
                            "pass_marks_asst":0,
                            "pass_marks_prac":0,
                            "marks_obtained_asst":0,
                            "marks_obtained_prac":0,
                            "total":0,
                        }

                        subject = get_subject_from_row(each_row)
                        marks = get_marks(each_row)
                        
                        if subject["Subject"] is None:
                            continue

                        data["full_marks_asst"] = marks["full_marks_asst"]
                        data["full_marks_prac"] = marks["full_marks_prac"]
                        data["pass_marks_asst"] = marks["pass_marks_asst"]
                        data["pass_marks_prac"] = marks["pass_marks_prac"]
                        data["marks_obtained_asst"] = marks["marks_obtained_asst"]
                        data["marks_obtained_prac"] = marks["marks_obtained_prac"]



                        data["subject"] = subject["Subject"]
                        data["code"] = subject["code"]
                        data['total'] = marks["total"]


                        response["tableData"].append({
                            "id":counter,
                            "code":data["code"],
                            "subject":data["subject"],
                            "fullMarks":{
                                "asst":data["full_marks_asst"],
                                "final":data["full_marks_prac"]
                            },
                            "passMarks":{
                                "asst":data["pass_marks_asst"],
                                "final":data["pass_marks_prac"]
                            },
                            "obtainedMarks":{
                                "asst":data["marks_obtained_asst"],
                                "final":data["marks_obtained_prac"]
                            },
                            "total":data['total'],
                            "remarks":None
                            })
                    print(json.dumps(response))
                        #print(data)
                        

if __name__ == "__main__":
    start = time.time()
    get_data()
    end = time.time()
    t = (end - start )
    # print(f"Time taken: {t:>5.2f} secs.")