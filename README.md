
# BadApplesProject

### Why
Have you ever forgotten you have something in the fridge until after it expires? According to a report by the Natural Resources Defense Council, America throws out more than 1,250 calories per day per person. That is a lot of wasted resources. Our application will solve this problem by tracking produce.

### What
Produce tracker is an user-friendly application that will help you keep track of potential expired products to minimize waste. It will allow you to keep track of your pantry items and notify you upon imminent expirations. 

### How

The first step to use our application is to upload grocery or item receipts. Reciepts can either be scanned via the camera, or manually entered in the Pantry. The application will automatically use optical character recognition (OCR, pytesseract) to match receipts to items in our database. Our database pulls information from reputable food expiration websites (such as https://www.eatbydate.com/) and matches the receipt item with one of the items in this database.

After the upload process, the user will be able to look at their items and view information of interest (such as expiration dates) on the Pantry. The user's produce is also stored in the database, ensuring that their data is persistent across all states of the application. There will be notifications implemented in the future, so the user is notified when the item is about to expire. 

Currently, our application can be tested with the following produce: fresh apples, blueberries, grapes, and bananas.



![Landing Screen](https://user-images.githubusercontent.com/55852769/96529371-f90e1500-1252-11eb-84a2-0e31fe436143.png) ![Succesful Scan](https://user-images.githubusercontent.com/55852769/96529454-35417580-1253-11eb-9931-19e696cafc71.png) 
![Pantry Screen](https://user-images.githubusercontent.com/55852769/96529531-6c178b80-1253-11eb-84f1-3b3b2a913b1e.png) 
![Manual Entry Screen](https://user-images.githubusercontent.com/55852769/96529598-9a956680-1253-11eb-8eb8-d9b14b797f50.png)
<p align="center">
  <img width="399" height="299" src="https://user-images.githubusercontent.com/55852769/96529666-cc0e3200-1253-11eb-8c75-8d779ab9d405.png">
</p>




### Technologies Used
- Kivy v2.0.0
- Python v3.8
- SQLite3
- Pytesseract
- Numpy

### Pitch

If you would like a quick overview of the concept/idea before development, you can view this [elevator pitch](https://www.youtube.com/watch?v=OB2ZTpWcwHo) about the project.

# Package Name for PIP:

    pip install our-package-name

# Initialization & Run Commands:

    todo

# Source Code
https://github.com/jd3builds/BadApplesProject/tree/master
