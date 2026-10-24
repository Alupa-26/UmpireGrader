import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Define strike zone
STRIKE_ZONE = {'left': -.8, 'right': .8, 'bottom': 1.575, 'top': 3.575}

def in_strike_zone(x, y):
    '''Check if a pitch is in the strike zone'''
    return STRIKE_ZONE['left'] <= x <= STRIKE_ZONE['right'] and STRIKE_ZONE['bottom'] <= y <= STRIKE_ZONE['top']

st.title("Umpire Grader")

# Replace tkinter filedialog with Streamlit's file_uploader
uploaded_file = st.file_uploader("Upload Trackman CSV", type="csv")

if uploaded_file is not None:
    try:
        # Streamlit's uploaded_file can be read directly by pandas
        df = pd.read_csv(uploaded_file)

        # Filter the dataframe for 'BallCalled' and 'StrikeCalled'
        df = df[df['PitchCall'].isin(['BallCalled', 'StrikeCalled'])]

        # Determine if the pitch location is a ball or strike
        df['IsStrike'] = df.apply(lambda row: in_strike_zone(row['PlateLocSide'], row['PlateLocHeight']), axis=1)

        # Determine if the pitch was called correctly
        df['CorrectCall'] = df.apply(lambda row: (row['IsStrike'] and row['PitchCall'] == 'StrikeCalled') or
                                                       (not row['IsStrike'] and row['PitchCall'] == 'BallCalled'), axis=1)

        # Calculate the percentage of correct calls
        correct_call_percentage = df['CorrectCall'].mean() * 100

        st.metric("Percentage of Correct Calls", f"{correct_call_percentage:.2f}%")

        # Create a scatter plot of the pitch locations
        fig, ax = plt.subplots()
        ax.set_aspect('equal')
        colors = df.apply(lambda row: 'red' if row['PitchCall'] == 'StrikeCalled' else 'green', axis=1)
        ax.scatter(df['PlateLocSide'], df['PlateLocHeight'], c=colors, alpha=0.5)

        # Plot the strike zone
        ax.plot([STRIKE_ZONE['left'], STRIKE_ZONE['right'], STRIKE_ZONE['right'], STRIKE_ZONE['left'], STRIKE_ZONE['left']],
                 [STRIKE_ZONE['bottom'], STRIKE_ZONE['bottom'], STRIKE_ZONE['top'], STRIKE_ZONE['top'], STRIKE_ZONE['bottom']], 'b-')

        ax.set_title(f"Percentage of correct calls: {correct_call_percentage:.2f}%")

        # Display the plot in the Streamlit app
        st.pyplot(fig)

        # Create a PDF buffer to allow downloading directly from the web app
        buf = io.BytesIO()
        fig.savefig(buf, format="pdf")
        st.download_button(
            label="Download Plot as PDF",
            data=buf.getvalue(),
            file_name="umpire_grade.pdf",
            mime="application/pdf"
        )

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")
