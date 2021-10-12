
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 14:47:28 2021

@author: mgu
"""

# importing required libraries

import sys
import shutil, os
import cv2
from pathlib import Path
import math
import numpy as np
from PyQt5 import QtWidgets,QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
import time
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import pandas as pd
import glob
from datetime import datetime
from openpyxl import Workbook, load_workbook
from win32com.client import Dispatch


COIL_ID = ''
actual_pixel = 0.0
actual_length = 0.0
actual_size = 0.0
HEAT = 0.0
Shear_value = 0.0

x_pixel, y_pixel = [], []
drawing = False # true if mouse is pressed
pt1_x , pt1_y = None , None
DICTIONARY = {}




g_window_name, g_window_name1 = "Draw a line", 'Draw a polygon'  
g_window_wh = [1000, 800]  

g_location_win, g_location_win1 = [0, 0],[0, 0] 
location_win, location_win1 = [0, 0], [0, 0]  
g_location_click, g_location_release = [0, 0], [0, 0]  
g_location_click1, g_location_release1 = [0, 0], [0, 0]

g_zoom, g_step = 1, 0.1
g_zoom1, g_step1 = 1, 0.1
g_image_original, g_image_original1 = '', ''
g_image_zoom, g_image_zoom1 = '', ''
g_image_show,g_image_show1 = '',''
        
        
        

def reset():
    global x_pixel, y_pixel, drawing, pt1_x, pt1_y, actual_pixel, actual_length
    x_pixel, y_pixel = [], []
    pt1_x , pt1_y = None , None
    actual_pixel, actual_length, actual_size = 0.0, 0.0, 0.0
    HEAT, Shear_value, COIL_ID = 0.0, 0.0, ''
    ######
    DICTIONARY = {}
    ######


#########################################
###  Calculate Polygon area  ###
def PolyArea(x,y):
    x, y = np.array(x), np.array(y)
    
    return 0.5*np.abs(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1)))

def check_location(img_wh, win_wh, win_xy):
    for i in range(2):
        if win_xy[i] < 0:
            win_xy[i] = 0
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] > win_wh[i]:
            win_xy[i] = img_wh[i] - win_wh[i]
        elif win_xy[i] + win_wh[i] > img_wh[i] and img_wh[i] < win_wh[i]:
            win_xy[i] = 0
    # print(img_wh, win_wh, win_xy)


def count_zoom(flag, step, zoom):
    if flag > 0: 
        zoom += step
        if zoom > 1 + step * 20: 
            zoom = 1 + step * 20
    else:
        zoom -= step
        if zoom < step:  
            zoom = step
    zoom = round(zoom, 2)  
    return zoom
        
# Main window class
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100,
                         1500, 1000)
        self.setStyleSheet("background : lightgrey;")
        self.available_cameras = QCameraInfo.availableCameras()
        if not self.available_cameras:
            sys.exit()  
        self.status = QStatusBar()
        self.status.setStyleSheet("background : white;")
        self.setStatusBar(self.status)
        self.save_path = ""
        self.viewfinder = QCameraViewfinder()
        self.viewfinder.show()
        self.setCentralWidget(self.viewfinder)
        self.select_camera(0)
        toolbar = QToolBar("Camera Tool Bar")
        self.addToolBar(toolbar)
        
        
        

        
        mainMenu = self.menuBar()
        
        FolderMenu = mainMenu.addMenu('Folder Control')
        change_folder_action = QAction("Choose Image Location",
                                       self)
        change_folder_action.setStatusTip("Choose folder where pictures will be saved.")
        # adding tool tip to it
        change_folder_action.setToolTip("Change save location")
        change_folder_action.triggered.connect(self.change_folder)
        
        submit_folder = QAction("Submit folder", self)
        submit_folder.setStatusTip("This will submit all the images in this folder to the default folder")
        submit_folder.setToolTip("Submit folder")
        submit_folder.triggered.connect(self.submitFolder)
        
        FolderMenu.addAction(change_folder_action)
        FolderMenu.addAction(submit_folder)
        
        
        
        CameraMenu = mainMenu.addMenu('Calibration Panel')
        Take_camera = QAction("Take a snapshoot",
                                       self)
        Take_camera.setStatusTip("Enter the file name and save the image.")
        # adding tool tip to it
        Take_camera.setToolTip("Take a snapshoot")
        Take_camera.triggered.connect(self.click_photo)
        
        Open_image = QAction("Open image", self)
        Open_image.setStatusTip("Open the image to draw.")
        Open_image.setToolTip("Open_image")
        Open_image.setCheckable(True)
        Open_image.setChecked(False)
        Open_image.triggered.connect(self.openImage)
        
        #############################
        Enter_data = QAction("Enter data", self)
        Enter_data.setStatusTip("Enter the data of the COIL.")
        Enter_data.setToolTip("Enter data")
        Enter_data.triggered.connect(self.enterLength)
        
        CameraMenu.addAction(Take_camera)
        CameraMenu.addAction(Enter_data)
        CameraMenu.addAction(Open_image)
        
        ResultMenu = mainMenu.addMenu('Data panel')
        print_dict = QAction("Print dictionary", self)
        print_dict.setStatusTip("Print the dictionary")
        print_dict.setToolTip("Print dictionary")
        print_dict.triggered.connect(self.printDict)
        
        store_dict = QAction("Data collection", self)
        store_dict.setStatusTip("Store data in excel")
        store_dict.setToolTip("Data collection")
        store_dict.triggered.connect(self.storeExcel)
        
        Reset = QAction("Clear the results", self)
        Reset.setStatusTip("Clear the results")
        Reset.setToolTip("Clear the results")
        Reset.triggered.connect(self.RESET)
        
        ResultMenu.addAction(print_dict)
        ResultMenu.addAction(store_dict)
        ResultMenu.addAction(Reset)
        
        ############
        #ExitMenu = mainMenu.addMenu('Exit')
        #exitButton = QAction(QIcon('exit24.png'), 'Exit', self)
        #exitButton.setStatusTip('Exit application')
        #exitButton.triggered.connect(self.close)
        #ExitMenu.addAction(exitButton)
        ############
        
        camera_selector = QComboBox()
        camera_selector.setStatusTip("Choose camera to take pictures")
        camera_selector.setToolTip("Select Camera")
        camera_selector.setToolTipDuration(2500)
        camera_selector.addItems([camera.description()
                                  for camera in self.available_cameras])
        camera_selector.currentIndexChanged.connect(self.select_camera)
        toolbar.addWidget(camera_selector)
        toolbar.setStyleSheet("background : white;")
        ############
        
        
        
        
        self.text_browser = QTextBrowser(self)
        self.text_browser.move(1200,100)
        self.text_browser.resize(300,800)
        self.tmpStr1, self.tmpStr2 = '<p style="font-size: 20px">', '</p>'
        STR = 'Welcome! There are 3 panels, Folder Control, Calibration Panel and Data Panel.'
        STR += 'You must choose a target folder first by clicking Choose Image Location.'
        STR += 'You can copy the images in another folder to the target folder by clicking submit folder. '
        
        self.text_browser.setText(self.tmpStr1 + STR + self.tmpStr2)
        self.text_browser.append(self.tmpStr1 + 'Now click on Choose Image Location.' + self.tmpStr2)
        self.setWindowTitle("PyQt5 Camera")
        
        self.xl = Dispatch('Excel.Application')
        self.xl.Visible = False
        
        self.show()
        
    def RESET(self):
        reset()
        
    def openImage(self):
        global g_image_original, g_image_original1, g_image_zoom,g_image_zoom1, g_image_show,g_image_show1, g_window_name, g_window_name1
        global g_zoom, g_zoom1
        
        fname = QFileDialog.getOpenFileName(self, 'Open an image. ', 
    'c:\\',"Image files (*.jpg *.gif)")
        if str(fname[0]) == '':
            self.text_browser.append(self.tmpStr1 + 'No Image selected. Please Select one image.' + self.tmpStr2)
            return
        img = cv2.imread(str(fname[0]))
        img1 = img.copy()
        
        g_image_original, g_image_original1 = img, img1
        g_image_zoom = g_image_original.copy()  
        g_image_show = g_image_original[g_location_win[1]:g_location_win[1] + g_window_wh[1], g_location_win[0]:g_location_win[0] + g_window_wh[0]]
        g_image_zoom1 = g_image_original1.copy()  
        g_image_show1 = g_image_original1[g_location_win[1]:g_location_win[1] + g_window_wh[1], g_location_win[0]:g_location_win[0] + g_window_wh[0]]
        
        cv2.namedWindow(g_window_name)
        cv2.namedWindow(g_window_name1)
        self.text_browser.append(self.tmpStr1 + 'Use mouse left button to adjust the image. Use right button to draw a line in the left image and draw a polygon in the right image.' + self.tmpStr2)
        self.text_browser.append(self.tmpStr1 + 'When you finish drawing both, enter q in keyboard to close the window.' + self.tmpStr2)
        def mouse(event, x, y, flags, param):
            global g_location_click, g_location_release, g_image_show, g_window_name, g_image_zoom, g_location_win, location_win, g_zoom
            global pt1_x, pt1_y,drawing,actual_pixel
            if event == cv2.EVENT_LBUTTONDOWN:  
                g_location_click = [x, y]
                location_win = [g_location_win[0], g_location_win[1]] 
            elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON): 
                g_location_release = [x, y]  
                h1, w1 = g_image_zoom.shape[0:2]  
                w2, h2 = g_window_wh  
                show_wh = [0, 0]  
                if w1 < w2 and h1 < h2:  
                    show_wh = [w1, h1]
                    g_location_win = [0, 0]
                elif w1 >= w2 and h1 < h2: 
                    show_wh = [w2, h1]
                    g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
                elif w1 < w2 and h1 >= h2:  
                    show_wh = [w1, h2]
                    g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
                else:  
                    show_wh = [w2, h2]
                    g_location_win[0] = location_win[0] + g_location_click[0] - g_location_release[0]
                    g_location_win[1] = location_win[1] + g_location_click[1] - g_location_release[1]
                check_location([w1, h1], [w2, h2], g_location_win)  
                g_image_show = g_image_zoom[g_location_win[1]:g_location_win[1] + show_wh[1], g_location_win[0]:g_location_win[0] + show_wh[0]]  
                
            elif event == cv2.EVENT_MOUSEWHEEL:  
                z = g_zoom 
                g_zoom = count_zoom(flags, g_step, g_zoom)  
                w1, h1 = [int(g_image_original.shape[1] * g_zoom), int(g_image_original.shape[0] * g_zoom)] 
                w2, h2 = g_window_wh  
                g_image_zoom = cv2.resize(g_image_original, (w1, h1), interpolation=cv2.INTER_AREA)  
                show_wh = [0, 0]  
                if w1 < w2 and h1 < h2: 
                    show_wh = [w1, h1]
                    cv2.resizeWindow(g_window_name, w1, h1)
                elif w1 >= w2 and h1 < h2:  
                    show_wh = [w2, h1]
                    cv2.resizeWindow(g_window_name, w2, h1)
                elif w1 < w2 and h1 >= h2:  
                    show_wh = [w1, h2]
                    cv2.resizeWindow(g_window_name, w1, h2)
                else:  
                    show_wh = [w2, h2]
                    cv2.resizeWindow(g_window_name, w2, h2)
                g_location_win = [int((g_location_win[0] + x) * g_zoom / z - x), int((g_location_win[1] + y) * g_zoom / z - y)]  
                check_location([w1, h1], [w2, h2], g_location_win)  
                # print(g_location_win, show_wh)
                g_image_show = g_image_zoom[g_location_win[1]:g_location_win[1] + show_wh[1], g_location_win[0]:g_location_win[0] + show_wh[0]]  
            
                      
            elif event==cv2.EVENT_RBUTTONDOWN:
                drawing=True
                pt1_x,pt1_y=x,y
                cv2.circle(g_image_show, (x,y), 0, color=(0,0,255), thickness = 2)
    
            elif event==cv2.EVENT_RBUTTONUP:
                drawing=False
                cv2.line(g_image_show,(pt1_x,pt1_y),(x,y),color=(100,0,200),thickness=2)
                # line is red color
                cv2.circle(g_image_show, (x,y), 0, color=(0,0,255), thickness = 2)

                actual_pixel = math.sqrt((x-pt1_x)*(x-pt1_x) + (y-pt1_y)*(y-pt1_y))
                #self.text_browser.append(self.tmpStr1 + f'The actual pixel of this line is {actual_pixel}' + self.tmpStr2)
            cv2.imshow(g_window_name, g_image_show)
            
        
        
        def mouse1(event,x,y,flags,param):
            global g_location_click1, g_location_release1, g_image_show1, g_window_name1, g_image_zoom1, g_location_win1, location_win1, g_zoom1
            global pt1_x, pt1_y,drawing,actual_pixel
            if event == cv2.EVENT_LBUTTONDOWN: 
                g_location_click1 = [x, y]  
                location_win1 = [g_location_win1[0], g_location_win1[1]]  
            elif event == cv2.EVENT_MOUSEMOVE and (flags & cv2.EVENT_FLAG_LBUTTON):  
                g_location_release1 = [x, y] 
                h1, w1 = g_image_zoom1.shape[0:2]  
                w2, h2 = g_window_wh  
                show_wh = [0, 0]  
                if w1 < w2 and h1 < h2:  
                    show_wh = [w1, h1]
                    g_location_win1 = [0, 0]
                elif w1 >= w2 and h1 < h2: 
                    show_wh = [w2, h1]
                    g_location_win1[0] = location_win1[0] + g_location_click1[0] - g_location_release1[0]
                elif w1 < w2 and h1 >= h2:  
                    show_wh = [w1, h2]
                    g_location_win1[1] = location_win1[1] + g_location_click1[1] - g_location_release1[1]
                else:  
                    show_wh = [w2, h2]
                    g_location_win1[0] = location_win1[0] + g_location_click1[0] - g_location_release1[0]
                    g_location_win1[1] = location_win1[1] + g_location_click1[1] - g_location_release1[1]
                check_location([w1, h1], [w2, h2], g_location_win1)  
                g_image_show1 = g_image_zoom1[g_location_win1[1]:g_location_win1[1] + show_wh[1], g_location_win1[0]:g_location_win1[0] + show_wh[0]]  
                
            elif event == cv2.EVENT_MOUSEWHEEL:  
                z = g_zoom1  
                g_zoom1 = count_zoom(flags, g_step, g_zoom1)  
                w1, h1 = [int(g_image_original.shape[1] * g_zoom1), int(g_image_original.shape[0] * g_zoom1)]  
                w2, h2 = g_window_wh  
                g_image_zoom1 = cv2.resize(g_image_original1, (w1, h1), interpolation=cv2.INTER_AREA)  
                show_wh = [0, 0] 
                if w1 < w2 and h1 < h2:  
                    show_wh = [w1, h1]
                    cv2.resizeWindow(g_window_name1, w1, h1)
                elif w1 >= w2 and h1 < h2:  
                    show_wh = [w2, h1]
                    cv2.resizeWindow(g_window_name1, w2, h1)
                elif w1 < w2 and h1 >= h2:  
                    show_wh = [w1, h2]
                    cv2.resizeWindow(g_window_name1, w1, h2)
                else:  
                    show_wh = [w2, h2]
                    cv2.resizeWindow(g_window_name1, w2, h2)
                g_location_win1 = [int((g_location_win1[0] + x) * g_zoom1 / z - x), int((g_location_win1[1] + y) * g_zoom1 / z - y)]  
                check_location([w1, h1], [w2, h2], g_location_win1)  
                # print(g_location_win, show_wh)
                g_image_show1 = g_image_zoom1[g_location_win1[1]:g_location_win1[1] + show_wh[1], g_location_win1[0]:g_location_win1[0] + show_wh[0]]

            elif event==cv2.EVENT_RBUTTONDOWN:
                drawing=True
                pt1_x,pt1_y=x,y
                x_pixel.append(x)
                y_pixel.append(y)
                cv2.circle(g_image_show1, (x,y), 0, color=(0,0,255), thickness = 2)
    
            elif event==cv2.EVENT_RBUTTONUP:
                drawing=False
                cv2.line(g_image_show1,(pt1_x,pt1_y),(x,y),color=(100,0,200),thickness=2)
                # line is red color
                cv2.circle(g_image_show1, (x,y), 0, color=(0,0,255), thickness = 2)
            cv2.imshow(g_window_name1, g_image_show1)
        

        while(1):
            
            cv2.setMouseCallback(g_window_name, mouse)
            cv2.setMouseCallback(g_window_name1, mouse1)
            if cv2.waitKey(1)&0xFF == ord('q'):
                break
                
            
        cv2.destroyAllWindows()  
        global COIL_ID, Shear_value, actual_size
        Actual_area = PolyArea(x_pixel, y_pixel) * math.pow((actual_length/ actual_pixel), 2) * math.pow((g_zoom/ g_zoom1), 2)
        self.text_browser.append(self.tmpStr1 + f'The actual size of the polygon is {Actual_area} mm^2.' + self.tmpStr2)
        self.text_browser.append(self.tmpStr1 + 'Now you have finished the calibration. You can see the result temporarily by clicking Print Dictionary, you can also click Data Collection to store the data in the excel.' + self.tmpStr2)
        Base_area = 8 * actual_length
        
        Shear_value = round((1 - Actual_area / Base_area) * 100, 3)
        actual_size = Actual_area
        DICTIONARY[str(COIL_ID)] = str(Shear_value) + '%'
        
        
    # method to select camera
    def select_camera(self, i):
        # getting the selected camera
        self.camera = QCamera(self.available_cameras[i])
        # setting view finder to the camera
        self.camera.setViewfinder(self.viewfinder)
        # setting capture mode to the camera
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        # if any error occur show the alert
        self.camera.error.connect(lambda: self.alert(self.camera.errorString()))
        # start the camera
        self.camera.start()
        # creating a QCameraImageCapture object
        self.capture = QCameraImageCapture(self.camera)
        # showing alert if error occur
        self.capture.error.connect(lambda error_msg, error,
                                   msg: self.alert(msg))
        # when image captured showing message
        self.capture.imageCaptured.connect(lambda d,
                                           i: self.status.showMessage("Image captured : " 
                                                                      + str(self.save_seq)))
        # getting current camera name
        self.current_camera_name = self.available_cameras[i].description()
        # inital save sequence
        self.save_seq = 0
    

        
            
    # method to take photo
    def click_photo(self):
        # time stamp
        self.text_browser.append(self.tmpStr1 + 'Enter the name and save the photo.' + self.tmpStr2)
        timestamp = time.strftime("%d-%b-%Y-%H_%M_%S")
        
        sname = QFileDialog.getSaveFileName(self, 'Enter Coil ID as image name', 
   'c:\\',"Image files (*.jpg *.gif)")
        self.capture.capture(str(sname[0]))
        
        # increment the sequence
        self.save_seq += 1
    

        
    # change folder method
    def change_folder(self):
        # open the dialog to select path
        path = QFileDialog.getExistingDirectory(self, 
                                                "Picture Location", "")
        # if path is selected
        if path:
            # update the path
            self.save_path = path
            file_abs_path = path + '/' + 'Shear_Value_Result.xlsx'
            csv_files = glob.glob(os.path.join(self.save_path, "Shear_Value_Result.xlsx"))
           
            if csv_files == []:
                workbook = Workbook()
                workbook.save(file_abs_path)
            
            self.wb = self.xl.Workbooks.Open(file_abs_path)
            mySheet = self.wb.WorkSheets('Sheet')

            mySheet.Cells(1,1).Value = 'COIL ID'
            mySheet.Cells(1,2).Value = 'Temperature in C'
            mySheet.Cells(1,3).Value = 'No. of Test'
            mySheet.Cells(1,4).Value = 'Date'
            mySheet.Cells(1,5).Value = 'Time'
            mySheet.Cells(1,6).Value = 'Size (mm^2)'
            mySheet.Cells(1,7).Value = 'Length (mm)'
            mySheet.Cells(1,8).Value = 'Shear Value (%)'
            
            self.wb.Save()
            #wb.Close()
            ###################################################
            #absolutePath = Path(file_abs_path).resolve()
            #os.system(f'start excel.exe "{absolutePath}"')
            ###################################################
            
            # update the sequence
            self.save_seq = 0
            self.text_browser.append(self.tmpStr1 + f'Target location changed to {self.save_path}. Now you can click on submit folder if you want. You can click on Take a snapshoot to take an image. You can also start the calibration by clicking Enter data.' + self.tmpStr2)
        
    
    def submitFolder(self):
        path = QFileDialog.getExistingDirectory(self, 
                                                "Custom Picture Location", "")
        if path:
            for file_name in os.listdir(path):
                # construct full file path
                if file_name.endswith('jpg') or file_name.endswith('png'):
                    source = path + '/' + file_name
                    destination = self.save_path + '//' + file_name
                    self.text_browser.append(self.tmpStr1 + f'{source} is copied.' + self.tmpStr2)
                    # copy only files
                    if os.path.isfile(source):
                        shutil.copy(source, destination)
                    

    def storeExcel(self):
        global HEAT, COIL_ID, actual_length, Shear_value, actual_size
        file_abs_path = self.save_path + '/' + 'Shear_Value_Result.xlsx'
        mySheet = self.wb.WorkSheets('Sheet')
        #mySheet.Cells(2,1).Value = '123'
        index = 2
        self.text_browser.append(self.tmpStr1 + 'Now you can calibrate another image by clicking Enter data.' + self.tmpStr2)
        while mySheet.Cells(index,1).Value != None:
            
            if str(round(mySheet.Cells(index,1).Value)) == COIL_ID:
                
                if mySheet.Cells(index + 1 , 3).Value == None:
                    now = datetime.now()
                    mySheet.Cells(index + 1 , 3).Value = '2'
                    mySheet.Cells(index + 1 , 4).Value = "%s/%s/%s" % (now.month, now.day, now.year)
                    mySheet.Cells(index + 1 , 5).Value = "%s:%s:%s" % (now.hour, now.minute, now.second)
                    mySheet.Cells(index + 1 , 6).Value = str(actual_size)
                    mySheet.Cells(index + 1 , 7).Value = str(actual_length)
                    mySheet.Cells(index + 1 , 8).Value = str(Shear_value)
                    self.wb.Save()
                    reset()
                    return
                if mySheet.Cells(index + 2 , 3).Value == None:
                    now = datetime.now()
                    mySheet.Cells(index + 2 , 3).Value = '3'
                    mySheet.Cells(index + 2 , 4).Value = "%s/%s/%s" % (now.month, now.day, now.year)
                    mySheet.Cells(index + 2 , 5).Value = "%s:%s:%s" % (now.hour, now.minute, now.second)
                    mySheet.Cells(index + 2 , 6).Value = str(actual_size)
                    mySheet.Cells(index + 2 , 7).Value = str(actual_length)
                    mySheet.Cells(index + 2 , 8).Value = str(Shear_value)
                    self.wb.Save()
                    reset()
                    return
                self.text_browser.append(self.tmpStr1 + 'Already conducted 3 trails for this coil.' + self.tmpStr2)
                self.wb.Save()
                reset()
                return
            index += 3
        now = datetime.now()
        mySheet.Cells(index , 1).Value = str(COIL_ID)
        mySheet.Cells(index , 2).Value = str(HEAT)
        mySheet.Cells(index , 3).Value = '1'
        mySheet.Cells(index , 4).Value = "%s/%s/%s" % (now.month, now.day, now.year)
        mySheet.Cells(index , 5).Value = "%s:%s:%s" % (now.hour, now.minute, now.second)
        mySheet.Cells(index , 6).Value = str(actual_size)
        mySheet.Cells(index , 7).Value = str(actual_length)
        mySheet.Cells(index , 8).Value = str(Shear_value)
        self.wb.Save()
        reset()
    
    def printDict(self):
        global DICTIONARY
        for key, value in DICTIONARY.items():
            self.text_browser.append(self.tmpStr1 + f'Image name: {key}, Shear value is {value}.' + self.tmpStr2)
            
        
    def enterLength(self):
        #text, okPressed = QInputDialog.getText(self, "Get text","Enter actual length in cm:", QLineEdit.Normal, "")
        #if okPressed and text != '':
        #    actual_length = float(text)
        #    print(f'Actual length of this line is {actual_length} cm.')
        #    print()
        self.text_browser.append(self.tmpStr1 + 'Click on show' + self.tmpStr2)
        self.formGroupBox = QGroupBox("Input data")
        flo = QFormLayout()
        e1 = QLineEdit()
        e1.textChanged.connect(self.textchanged1)
        e2 = QLineEdit()
        e2.textChanged.connect(self.textchanged2)
        e3 = QLineEdit()
        e3.textChanged.connect(self.textchanged3)
        flo.addRow("Input Coil ID",e1)
        flo.addRow("Input Temperature in C",e2)
        flo.addRow("Input Length in mm",e3)
        btn = QPushButton("Show")
        btn.clicked.connect(self.gettext)
        flo.addRow(btn)
        
        self.formGroupBox.setLayout(flo)
        self.formGroupBox.show()
        
    def textchanged1(self, text):
        global COIL_ID
        COIL_ID = str(text)
        
    def textchanged2(self, text):
        global HEAT
        HEAT = str(text)
        
    def textchanged3(self, text):
        global actual_length
        actual_length = float(text)
        
    def gettext(self):
        global COIL_ID, HEAT, actual_length
        self.text_browser.append(self.tmpStr1 + f'COIL ID is {COIL_ID}' + self.tmpStr2)
        self.text_browser.append(self.tmpStr1 + f'HEAT is {HEAT} C' + self.tmpStr2)
        self.text_browser.append(self.tmpStr1 + f'Actual length is {actual_length} mm' + self.tmpStr2)
        self.text_browser.append(self.tmpStr1 + 'Now close it and click on Open Image.' + self.tmpStr2)
        
    def alert(self, msg):
        error = QErrorMessage(self)
        error.showMessage(msg)
        
        
App = QApplication(sys.argv)
window = MainWindow()

sys.exit(App.exec())