from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import random
import math
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# File path for Excel (adjust if dynamic)
STAFF_FILE = 'staffs.xlsx'

# Route for the index page with the form
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assign_staffs', methods=['POST'])
def assign_staffs():
    try:
        fn = int(request.form['fn_staffs'])
        an = int(request.form['an_staffs'])
        allocation_date = request.form['allocation_date']  # Retrieve the date from the form

        # Convert date to a more readable format (e.g., DD-MM-YYYY)
        formatted_date = datetime.strptime(allocation_date, '%Y-%m-%d').strftime('%d-%m-%Y')

        df = pd.read_excel(STAFF_FILE)
        for i in df:
            df[i] = df[i].astype(str).str.upper().str.strip()

        if 'STAFF NAME' not in df.columns or 'DEPARTMENT' not in df.columns:
            flash("The Excel file must contain 'STAFF NAME' and 'DEPARTMENT' columns.", 'error')
            return redirect(url_for('index'))

        staffs = df['STAFF NAME'].tolist()
        depts = list(set(df['DEPARTMENT'].tolist()))

        if fn <= 0 or an <= 0:
            flash("Please enter positive numbers for FN and AN.", 'error')
            return redirect(url_for('index'))

        total_staff = len(staffs)
        if fn > total_staff or an > total_staff:
            flash(f"{max(fn, an)} Staffs are not available. Only {total_staff} Staffs are available.", 'error')
            return redirect(url_for('index'))

        dict1 = {dept: df[df['DEPARTMENT'] == dept]['STAFF NAME'].tolist() for dept in depts}
        allocated = {staff: 0 for staff in staffs}

        # Call the logic you don't want to change
        set1, set2 = allocate_staffs(fn, an, dict1, depts, allocated, staffs)

        # Reorder AN Staffs
        an_staffs = [set2[i] for i in range(0, len(set2), 2)][-1::-1] + [set2[i] for i in range(1, len(set2), 2)]

        # Create PDF and save with the formatted date in the filename
        filename = f"Staff Allocation - {formatted_date}.pdf"
        filepath = os.path.join(os.getcwd(), 'static', filename)
        create_pdf(filepath, set1, an_staffs, formatted_date)  # Pass the formatted date to the PDF

        # Send the file to the user for download
        return send_file(filepath, as_attachment=True)

    except FileNotFoundError:
        flash("The file 'staffs.xlsx' was not found.", 'error')
        return redirect(url_for('index'))
    except ValueError:
        flash("Please enter valid numbers for FN and AN.", 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", 'error')
        return redirect(url_for('index'))

def allocate_staffs(fn, an, dict1, depts, allocated,staffs):
    set1, set2 = set(), set()
    minimum = {dept: 0 for dept in depts}

    # Allocate FN Staffs
    index = 0
    while len(set1) < fn:
        index = index % len(depts)
        dep = depts[index]
        mini = 10000
        for i in dict1[dep]:
            mini = min(mini, allocated[i])
        minimum[dep] = mini
        x = random.randint(0, len(dict1[dep]) - 1)
        while allocated[dict1[dep][x]] > minimum[dep]:
            x = random.randint(0, len(dict1[dep]) - 1)
        if dict1[dep][x] + " " + dep not in set1:
            set1.add(dict1[dep][x] + " " + dep)
            allocated[dict1[dep][x]] += 1
        index += 1
    if fn % len(depts) == 0:
        index += 1

    # Allocate AN Staffs
    while len(set2) < an:
        index = index % len(depts)
        dep = depts[index]
        mini = 10000
        for i in dict1[dep]:
            mini = min(mini, allocated[i])
        minimum[dep] = mini
        x = random.randint(0, len(dict1[dep]) - 1)
        while allocated[dict1[dep][x]] > minimum[dep]:
            x = random.randint(0, len(dict1[dep]) - 1)
        if fn + an > len(staffs) and dict1[dep][x] + " " + dep not in set2:
            set2.add(dict1[dep][x] + " " + dep)
            allocated[dict1[dep][x]] += 1
        else:
            if dict1[dep][x] + " " + dep not in set1 and dict1[dep][x] + " " + dep not in set2:
                set2.add(dict1[dep][x] + " " + dep)
                allocated[dict1[dep][x]] += 1
        index += 1

    set1 = list(set1)
    set2 = list(set2)
    return set1, set2


def allocate_staffs(fn, an, dict1, depts, allocated,staffs):
    set1, set2 = set(), set()
    minimum = {dept: 0 for dept in depts}

    # Allocate FN Staffs
    index = 0
    while(len(set1)<fn):
            index = index%len(depts)
            dep = depts[index]
            mini = 10000
            for i in dict1[dep]:
                mini = min(mini,allocated[i])
            minimum[dep]= mini
            x = random.randint(0,len(dict1[dep])-1)
            while(allocated[dict1[dep][x]]>minimum[dep]):
                x = random.randint(0,len(dict1[dep])-1)
            if dict1[dep][x]+" "+dep not in set1:
                set1.add(dict1[dep][x]+" "+dep)
                allocated[dict1[dep][x]]+=1
            index+=1
    if fn%len(depts)==0:
            index+=1

    # Allocate AN Staffs
    while(len(set2)<an):
            index = index%len(depts)
            dep = depts[index]
            mini = 10000
            for i in dict1[dep]:
                mini = min(mini,allocated[i])
            minimum[dep]= mini
            x = random.randint(0,len(dict1[dep])-1)
            while(allocated[dict1[dep][x]]>minimum[dep]):
                x = random.randint(0,len(dict1[dep])-1)
            if fn+an>len(staffs) and dict1[dep][x]+" "+dep not in set2:
                set2.add(dict1[dep][x]+" "+dep)
                allocated[dict1[dep][x]]+=1
            else:
                if dict1[dep][x]+" "+dep not in set1 and dict1[dep][x]+" "+dep not in set2:
                    set2.add(dict1[dep][x]+" "+dep)
                    allocated[dict1[dep][x]]+=1          
            index+=1
    
    set1 = list(set1)
    set2 = list(set2)
    return set1, set2

def create_pdf(filepath, fn_staffs, an_staffs, allocation_date):
    try:
        c = canvas.Canvas(filepath, pagesize=letter)
        c.setFont("Helvetica-Bold", 18)
        change = 190
        initial = 100
        # Page 1: FN Staffs
        c.drawString(90, 750, "ERODE SENGUNTHAR ENGINEERING COLLEGE")
        c.line(100, 710, 500, 710)
        c.drawString(100, 715, "FACULTY ALLOCATION")

        c.drawString(350, 715, f"Date: {allocation_date}")  # Use the date from form input

        c.setFont("Helvetica-Bold", 18)
        c.drawString(280, 680, "FN Staffs")
        c.setFont("Helvetica", 13)
        y_position = 660
        x = 0
        if len(fn_staffs)>50:
            initial = 70
            change = 180
        for staff in fn_staffs:
            c.drawString(initial + x, y_position, staff)
            y_position -= 25
            if y_position < 50:  # New column
                x += change
                y_position = 660

        c.showPage()
        if len(fn_staffs)>50:
            initial = 70
            change = 180
        else:
            initial = 100
            change = 190
        # Page 2: AN Staffs
        c.setFont("Helvetica-Bold", 18)
        c.drawString(90, 750, "ERODE SENGUNTHAR ENGINEERING COLLEGE")
        c.line(100, 710, 500, 710)
        c.drawString(100, 715, "FACULTY ALLOCATION")

        c.drawString(350, 715, f"Date: {allocation_date}")  

        c.setFont("Helvetica-Bold", 18)
        c.drawString(280, 680, "AN Staffs")
        c.setFont("Helvetica", 13)
        
        y_position = 660
        x = 0
        for staff in an_staffs:
            c.drawString(initial + x, y_position, staff)
            y_position -= 25
            if y_position < 50:
                x += change
                y_position = 660

        c.save()

    except Exception as e:
        flash(f"Failed to create PDF: {e}", 'error')


if __name__ == '__main__':
    app.run(debug=True)
