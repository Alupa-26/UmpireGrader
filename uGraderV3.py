import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
import os
from tkinter import filedialog

# Define strike zone
STRIKE_ZONE = {'left': -.8, 'right': .8, 'bottom': 1.575, 'top': 3.575}

def in_strike_zone(x, y):
    '''Check if a pitch is in the strike zone'''
    return STRIKE_ZONE['left'] <= x <= STRIKE_ZONE['right'] and STRIKE_ZONE['bottom'] <= y <= STRIKE_ZONE['top']

def process_csv(file_path):
    '''Load and process the CSV data'''
    try:
        print(f"Processing file: {file_path}")
        df = pd.read_csv(file_path)

        # Filter the dataframe for 'BallCalled' and 'StrikeCalled'
        df = df[df['PitchCall'].isin(['BallCalled', 'StrikeCalled'])]

        # Determine if the pitch location is a ball or strike
        df['IsStrike'] = df.apply(lambda row: in_strike_zone(row['PlateLocSide'], row['PlateLocHeight']), axis=1)

        # Determine if the pitch was called correctly
        df['CorrectCall'] = df.apply(lambda row: (row['IsStrike'] and row['PitchCall'] == 'StrikeCalled') or
                                                       (not row['IsStrike'] and row['PitchCall'] == 'BallCalled'), axis=1)

        # Calculate the percentage of correct calls
        correct_call_percentage = df['CorrectCall'].mean() * 100

        print(f"Percentage of correct calls: {correct_call_percentage:.2f}%")

        # Create a scatter plot of the pitch locations
        fig, ax = plt.subplots()  # You need to get the Axes object when creating the plot
        ax.set_aspect('equal')  # Set the aspect ratio to be equal
        colors = df.apply(lambda row: 'red' if row['PitchCall'] == 'StrikeCalled' else 'green', axis=1)
        plt.scatter(df['PlateLocSide'], df['PlateLocHeight'], c=colors, alpha=0.5)

        # Plot the strike zone
        plt.plot([STRIKE_ZONE['left'], STRIKE_ZONE['right'], STRIKE_ZONE['right'], STRIKE_ZONE['left'], STRIKE_ZONE['left']],
                 [STRIKE_ZONE['bottom'], STRIKE_ZONE['bottom'], STRIKE_ZONE['top'], STRIKE_ZONE['top'], STRIKE_ZONE['bottom']], 'b-')

        # Add the percentage of correct calls as the title
        plt.title(f"Percentage of correct calls: {correct_call_percentage:.2f}%")

        # Save the plot to a PDF
        base_name = os.path.basename(file_path)  # Get the base name
        pdf_name = os.path.splitext(base_name)[0] + '.pdf'  # Replace the extension with .pdf
        plt.savefig(pdf_name)
    except Exception as e:
        print(f"An error occurred while processing the file: {e}")

def select_file():
    '''Prompt the user to select a file'''
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename()
    root.destroy()  # Destroy the root window after getting the file path
    if file_path.endswith('.csv'):
        process_csv(file_path)
    else:
        print('Please select a .csv file')

# Prompt the user to select a file
select_file()
