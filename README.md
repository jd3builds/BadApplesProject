
# BadApplesProject

### Why
Have you ever forgotten you have something in the fridge until after it expires? According to a report by the Natural Resources Defense Council, America throws out more than 1,250 calories per day per person. That is a lot of wasted resources. Our application will solve this problem by tracking produce.

### What
Produce tracker is an user-friendly application that will help you keep track of potential expired products to minimize waste. It will allow you to keep track of your pantry items and notify you upon imminent expirations. 

### How

The first step to use our application is to upload grocery or item receipts. The application will automatically use optical character recognition (OCR, pytesseract) to match receipts to items in our database. Our database pulls information from reputable food expiration websites (such as https://www.eatbydate.com/) and matches the receipt item with one of the items in this database.

After the upload process, the user will be able to look at their items and view information of interest (such as expiration dates). There will be notifications implemented in the future, so the user is notified when the item is about to expire. 

Currently, our application can be tested with the following produce: fresh apples, blueberries, grapes, and bananas.

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
