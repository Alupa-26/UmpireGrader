import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Define strike zone and baseball dimensions
STRIKE_ZONE = {'left': -.8, 'right': .8, 'bottom': 1.575, 'top': 3.575}
BALL_RADIUS = 1.45 / 12  # ~0.1208 feet (radius of a standard baseball)

def in_strike_zone(x, y):
    '''Check if any part of the baseball touches the strike zone'''
    # Find the closest point on/inside the strike zone rectangle to the pitch center
    closest_x = max(STRIKE_ZONE['left'], min(x, STRIKE_ZONE['right']))
    closest_y = max(STRIKE_ZONE['bottom'], min(y, STRIKE_ZONE['top']))
    
    # Calculate the distance from the pitch center to this closest point
    distance_x = x - closest_x
    distance_y = y - closest_y
    
    # If the squared distance is less than or equal to the squared radius, it's touching
    return (distance_x**2 + distance_y**2) <= (BALL_RADIUS**2)

st.title("Umpire Grader")

uploaded_file = st.file_uploader("Upload Trackman CSV", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        # Filter the dataframe for 'BallCalled' and 'StrikeCalled'
        df = df[df['PitchCall'].isin(['BallCalled', 'StrikeCalled'])]

        # Determine if the pitch location is a ball or strike (accounting for ball radius)
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
        
        # Plot pitches
        ax.scatter(df['PlateLocSide'], df['PlateLocHeight'], c=colors, alpha=0.5)

        # Plot the strike zone
        ax.plot([STRIKE_ZONE['left'], STRIKE_ZONE['right'], STRIKE_ZONE['right'], STRIKE_ZONE['left'], STRIKE_ZONE['left']],
                 [STRIKE_ZONE['bottom'], STRIKE_ZONE['bottom'], STRIKE_ZONE['top'], STRIKE_ZONE['top'], STRIKE_ZONE['bottom']], 'b-', linewidth=2)

        ax.set_title(f"Percentage of correct calls: {correct_call_percentage:.2f}%")
        
        # Set realistic axis limits so the plot isn't distorted
        ax.set_xlim(-2.5, 2.5)
        ax.set_ylim(0, 5)

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
