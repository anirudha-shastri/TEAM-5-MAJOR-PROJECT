import cv2
from dat import db
from dat.models import Img_Annotated
import numpy as np
import pandas as pd
from flask_login import current_user

colors = {'blue': (255, 0, 0), 'green': (0, 255, 0), 'red': (0, 0, 255), 
                        'yellow': (0, 255, 255),'magenta': (255, 0, 255), 
                        'cyan': (255, 255, 0), 'white': (255, 255, 255), 'black': (0, 0, 0), 
                        'gray': (125, 125, 125), 
                        'rand': np.random.randint(0, high=256, size=(3,)).tolist(), 
                        'dark_gray': (50, 50, 50), 'light_gray': (220, 220, 220)}

text=['']


def exit_imgdisp(image):
        while True:
            cv2.imshow('neck_X-ray1', image)
            # Continue until 'q' is pressed:
            if cv2.waitKey(20) & 0xFF == ord('q'):
                    break

def exit_imgdisp(image_final):
        while True:
            cv2.imshow('neck_X-ray1', image_final)
            # Continue until 'q' is pressed:
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break

def draw_dots(event, x, y, flags, param):
        x_vals = param[0]
        y_vals = param[1]
        annotation_vals = param[2]
        image_final = param[3]
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(image_final, (x, y), 2,colors['magenta'], -1)
            
            #text1=input("enter the text")
            
            x_vals.append(x)
            y_vals.append(y)
            annotation_vals.append(text[0])

def print_txt_img(df, image_final):
        i=0
        while i in range(len(df)):
            # height = image_final.shape[0]
            width = image_final.shape[1]

            x_temp=df.iloc[i][0]
            y_temp=df.iloc[i][1]
            text=df.iloc[i][2]

            text_x_pos = None
            text_y_pos = y_temp

            if x_temp < (width/2):
                text_x_pos = int(x_temp + (width * 0.03))
            else:
                text_x_pos = int(x_temp - (width * 0.03))

            # Write text on the image
            cv2.putText(image_final, text, (text_x_pos,text_y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.4, colors['red'], 2)

            #cv2.imwrite(OUTPUT_IMAGE[0], image_final)
            i=i+1   

def single_dot1(event, x, y, flags, param):
        x_vals1 = param[0]
        y_vals1 = param[1]
        image_final1 = param[2]
        if event == cv2.EVENT_LBUTTONDOWN:         
            cv2.circle(image_final1, (x, y), 2, colors['magenta'], -1)
            
            x_vals1.append(x)
            y_vals1.append(y)

# This is the main function for the annotation of points and drawing all the lines and adding the whole 
    #second image copy with depth identification 
def auto_full_anno(image_final,x_vals,y_vals,annotation_vals, image, filename):
        
        
        x_vals1=[]
        y_vals1=[]
        temp_lst=[]
        # Close()
     
        
        cv2.namedWindow('neck_X-ray1')
        param = [x_vals, y_vals, annotation_vals, image_final]
        cv2.setMouseCallback('neck_X-ray1', draw_dots, param) 
        exit_imgdisp(image_final)
        cv2.destroyAllWindows()
        
        temp_lst=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19']
        for i in range(len(temp_lst)):
            annotation_vals[i]=temp_lst[i]
            
        
        data = {'X':x_vals,'Y':y_vals,'Annotation':annotation_vals}
        df = pd.DataFrame(data)
        print_txt_img(df, image_final)
      

        data = {'X':x_vals,'Y':y_vals,'Annotation':annotation_vals}
        df = pd.DataFrame(data)
        cv2.line(image_final,(df.iloc[0][0],df.iloc[0][1]),(df.iloc[1][0],df.iloc[1][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[1][0],df.iloc[1][1]),(df.iloc[2][0],df.iloc[2][1]),colors['yellow'],1)
        
        #C3 
        cv2.line(image_final,(df.iloc[3][0],df.iloc[3][1]),(df.iloc[4][0],df.iloc[4][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[4][0],df.iloc[4][1]),(df.iloc[5][0],df.iloc[5][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[5][0],df.iloc[5][1]),(df.iloc[7][0],df.iloc[7][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[3][0],df.iloc[3][1]),(df.iloc[6][0],df.iloc[6][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[6][0],df.iloc[6][1]),(df.iloc[8][0],df.iloc[8][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[7][0],df.iloc[7][1]),(df.iloc[10][0],df.iloc[10][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[8][0],df.iloc[8][1]),(df.iloc[9][0],df.iloc[9][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[9][0],df.iloc[9][1]),(df.iloc[10][0],df.iloc[10][1]),colors['yellow'],1)
        
        
        #c4
        cv2.line(image_final,(df.iloc[11][0],df.iloc[11][1]),(df.iloc[12][0],df.iloc[12][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[12][0],df.iloc[12][1]),(df.iloc[13][0],df.iloc[13][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[13][0],df.iloc[13][1]),(df.iloc[15][0],df.iloc[15][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[11][0],df.iloc[11][1]),(df.iloc[14][0],df.iloc[14][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[14][0],df.iloc[14][1]),(df.iloc[16][0],df.iloc[16][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[15][0],df.iloc[15][1]),(df.iloc[18][0],df.iloc[18][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[16][0],df.iloc[16][1]),(df.iloc[17][0],df.iloc[17][1]),colors['yellow'],1)
        cv2.line(image_final,(df.iloc[17][0],df.iloc[17][1]),(df.iloc[18][0],df.iloc[18][1]),colors['yellow'],1)
        
        
        #getting new image:
        # IMAGE_NAME=IMAGE_NAME_LST[0]
        image1 = image
        res1=cv2.resize(image1,None,fx=0.5,fy=0.5,interpolation=cv2.INTER_CUBIC)
        image_final1 = res1[400:1000,0:250]
        
        #findind the line equation between point 1 and 3
        cv2.line(image_final1,(df.iloc[0][0],df.iloc[0][1]),(df.iloc[2][0],df.iloc[2][1]),colors['yellow'],1)
        
        cv2.line(image_final1,(df.iloc[0][0],df.iloc[0][1]),(df.iloc[1][0],df.iloc[1][1]),colors['yellow'],1)
        cv2.line(image_final1,(df.iloc[1][0],df.iloc[1][1]),(df.iloc[2][0],df.iloc[2][1]),colors['yellow'],1)
        
        
        #findind the line equation between point 9 and 11
        cv2.line(image_final1,(df.iloc[8][0],df.iloc[8][1]),(df.iloc[10][0],df.iloc[10][1]),colors['yellow'],1)
        
        cv2.line(image_final1,(df.iloc[8][0],df.iloc[8][1]),(df.iloc[9][0],df.iloc[9][1]),colors['yellow'],1)
        cv2.line(image_final1,(df.iloc[9][0],df.iloc[9][1]),(df.iloc[10][0],df.iloc[10][1]),colors['yellow'],1)
        
        
        #findind the line equation between point 9 and 11
        cv2.line(image_final1,(df.iloc[16][0],df.iloc[16][1]),(df.iloc[18][0],df.iloc[18][1]),colors['yellow'],1)
        
        cv2.line(image_final1,(df.iloc[16][0],df.iloc[16][1]),(df.iloc[17][0],df.iloc[17][1]),colors['yellow'],1)
        cv2.line(image_final1,(df.iloc[17][0],df.iloc[17][1]),(df.iloc[18][0],df.iloc[18][1]),colors['yellow'],1)
        
                    
        cv2.namedWindow('neck_X-ray1') 
        param = [x_vals1, y_vals1, image_final1]
        cv2.setMouseCallback('neck_X-ray1',single_dot1, param)
        while True:
            cv2.imshow('neck_X-ray1', image_final1)
            # Continue until 'q' is pressed:
            if cv2.waitKey(20) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
                                
        cv2.line(image_final1,(df.iloc[1][0],df.iloc[1][1]),(x_vals1[0],y_vals1[0]),colors['red'],1)
        cv2.line(image_final1,(df.iloc[9][0],df.iloc[9][1]),(x_vals1[1],y_vals1[1]),colors['red'],1)
        cv2.line(image_final1,(df.iloc[17][0],df.iloc[17][1]),(x_vals1[2],y_vals1[2]),colors['red'],1)       
        
        #getting both images to be saved as string
        img_str1 = cv2.imencode('.jpg',image_final)[1].tostring()
        img_name1 = filename.replace('.jpg','')+"_annotated.jpg"
        img_str2 = cv2.imencode('.jpg',image_final1)[1].tostring()
        img_name2 = filename.replace('.jpg','')+"_annotated2.jpg"
        

        image_final = cv2.hconcat([image_final, image_final1])
        
        exit_imgdisp(image_final)
        cv2.destroyAllWindows()

        
        
        user_id = current_user.id
        img_ann = Img_Annotated(user_id=user_id,img1 = img_str1, name1 = img_name1, img2= img_str2, name2 = img_name2)
        db.session.add(img_ann)
        db.session.commit()
        # OUTPUT_IMAGE= 'dat/annotated/'+filename.replace('.jpg','')+ "_annotated.jpg"
        # cv2.imwrite(OUTPUT_IMAGE, image_final)