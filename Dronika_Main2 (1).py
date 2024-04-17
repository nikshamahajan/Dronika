#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont
from roboflow import Roboflow
import datetime
import pandas as pd
from geopy.geocoders import Nominatim

# Initialize Roboflow Client
rf = Roboflow(api_key="mBpJmBoaKiCx1RiriSWy")
project = rf.workspace().project("pistol-wgcvl")
roboflow_model = project.version(1).model


# Create a folder to store detected images
output_folder = "detected_images"
os.makedirs(output_folder, exist_ok=True)

# Initialize DataFrame to store image names, datetime, class, and accuracy
data = {'Image Name': [], 'Date and Time': [], 'Class': [], 'Accuracy': [], 'Latitude': [], 'Longitude': []}
df = pd.DataFrame(data)

# Initialize geolocator
geolocator = Nominatim(user_agent="roboflow_gps")

# Function to get GPS coordinates
def get_gps_coordinates(location):
    try:
        location = geolocator.geocode(location)
        return location.latitude, location.longitude
    except Exception as e:
        print("Error:", e)
        return None, None

# Function to perform object detection with Roboflow model
def perform_object_detection():
    global df  # Access the DataFrame defined outside the function
    
    # Open a file dialog for the user to select an image file
    file_path = filedialog.askopenfilename()

    # Check if a file was selected
    if file_path:
        # Perform object detection with Roboflow model
        predictions_json = roboflow_model.predict(file_path, confidence=40, overlap=30).json()
        print(predictions_json)  # Print predictions to the console

        # Save the detected image from Roboflow to the folder
        original_image_name = os.path.splitext(os.path.basename(file_path))[0]  # Extract the filename without extension
        roboflow_detected_image_path = os.path.join(output_folder, f"{original_image_name}_roboflow_detected.jpg")
        roboflow_model.predict(file_path, confidence=40, overlap=30).save(roboflow_detected_image_path)

        # Get current date and time
        current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get GPS coordinates based on current location
        current_location = "Your location"  # Replace with your actual location or use GPS sensor to get location
        latitude, longitude = get_gps_coordinates(current_location)

        # Open the detected image with Pillow
        with Image.open(roboflow_detected_image_path) as img:
            # Define text to overlay
            text = f"{current_datetime}\nGPS: {latitude}, {longitude}"

            # Define font and size
            font = ImageFont.truetype("arial.ttf", 150)

            # Create a drawing context
            draw = ImageDraw.Draw(img)

            # Calculate text size and position
            text_width, text_height = draw.textsize(text, font)
            image_width, image_height = img.size
            text_x = image_width - text_width - 10
            text_y = image_height - text_height - 10

            # Add text to image
            # Change fill color to black with white highlight
            draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font, stroke_fill=(255, 255, 255), stroke_width=2)

            # Save the modified image
            img.save(roboflow_detected_image_path)

            # Extract class and accuracy from predictions JSON
            classes = [pred['class'] for pred in predictions_json['predictions']]
            accuracies = [pred['confidence'] for pred in predictions_json['predictions']]

            # Add the image name, datetime, class, accuracy, latitude, and longitude to the DataFrame
            for class_name, accuracy in zip(classes, accuracies):
                df = pd.concat([df, pd.DataFrame({'Image Name': [os.path.basename(roboflow_detected_image_path)], 
                                                  'Date and Time': [current_datetime], 
                                                  'Class': [class_name], 
                                                  'Accuracy': [accuracy], 
                                                  'Latitude': [latitude], 
                                                  'Longitude': [longitude]})], ignore_index=True)

        # Display the original and detected images with titles
        display_window = tk.Toplevel(root)
        display_window.title("Images")

        # Display the original image with title
        original_image = Image.open(file_path)
        original_image.thumbnail((300, 300))
        original_image_tk = ImageTk.PhotoImage(original_image)
        original_label = tk.Label(display_window, text="Original Image", font=("Helvetica", 12, "bold"))
        original_label.pack()
        original_label = tk.Label(display_window, image=original_image_tk)
        original_label.image = original_image_tk
        original_label.pack(side=tk.LEFT, padx=10)

        # Display the detected image from Roboflow with title
        roboflow_detected_image = Image.open(roboflow_detected_image_path)
        roboflow_detected_image.thumbnail((300, 300))
        roboflow_detected_image_tk = ImageTk.PhotoImage(roboflow_detected_image)
        roboflow_detected_label = tk.Label(display_window, text="Detected Image (Roboflow)", font=("Helvetica", 12, "bold"))
        roboflow_detected_label.pack()
        roboflow_detected_label = tk.Label(display_window, image=roboflow_detected_image_tk)
        roboflow_detected_label.image = roboflow_detected_image_tk
        roboflow_detected_label.pack(side=tk.LEFT, padx=10)

        # Display a success message
        success_label.config(text=f"Detected image saved in the '{output_folder}' folder.")

        # Automatically save data to Excel
        save_to_excel()

# Function to save the DataFrame to an Excel file
def save_to_excel():
    global df  # Access the DataFrame defined outside the function
    excel_file_path = r"C:\Users\NIKSHA MAHAJAN\Desktop\dronika.xlsx"  # Specify the path
    df.to_excel(excel_file_path, index=False)
    success_label.config(text=f"Data saved to '{excel_file_path}'.")

# Create the main application window
root = tk.Tk()
root.title("Roboflow Object Detection GUI")
root.geometry("900x400")  # Adjust the window size as needed
root.configure(bg="white")  # Set background color to white

# Label for instructions
instructions_label = tk.Label(root, text="Select an image file for object detection:", font=("Helvetica", 14))
instructions_label.pack(pady=10)

# Button to trigger object detection
detect_button = tk.Button(root, text="Choose Image", command=perform_object_detection, bg="lightblue", font=("Helvetica", 12))
detect_button.pack(pady=20)

# Label to display success message
success_label = tk.Label(root, text="", font=("Helvetica", 12), fg="green")
success_label.pack(pady=10)

# Start the main event loop
root.mainloop()


# In[ ]:




