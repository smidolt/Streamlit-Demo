import streamlit as st
import pandas as pd
import os
from PIL import Image

# Set the path to your images directory
IMAGE_FOLDER = 'images'

# Initialize session state variables
if 'image_list' not in st.session_state:
    # Get list of image files
    image_extensions = ['.jpg', '.jpeg', '.png']
    st.session_state.image_list = [
        f for f in os.listdir(IMAGE_FOLDER)
        if os.path.splitext(f)[1].lower() in image_extensions
    ]
    st.session_state.current_index = 0
    st.session_state.all_ratings = {}
    st.session_state.criteria = {
        "Fur Texture (0-4 Points)": [0, 2, 4],
        "Fur Details in Highlights and Shadows (0-2 Points)": [0, 1, 2],
        "Proper Exposure (0-1 Point)": [0, 1],
        "Zoom Test for Pixel Quality (0/2 Point)": [0, 2],
        "Smooth Textures (0-1 Point)": [0, 1],
        "Crisp Focus on Eyes (0-4 Points)": [0, 2, 4],
        "Crisp Focus on Fur Texture (0-1 Point)": [0, 1],
        "Blurriness Check (0-1 Point)": [0, 1],
        "Resolution Check at Zoom (0-1 Point)": [0, 1]
    }

def load_image(image_path):
    return Image.open(image_path)

def show_image(image_name):
    image_path = os.path.join(IMAGE_FOLDER, image_name)
    image = load_image(image_path)
    st.image(image, caption=image_name, use_container_width=True)

def get_rating_inputs():
    ratings = {}
    for criterion, options in st.session_state.criteria.items():
        widget_key = f"{criterion}_{st.session_state.current_index}"
        options_with_prompt = ['Select an option'] + [str(option) for option in options]
        
        # Retrieve previous rating if available
        previous_ratings = st.session_state.all_ratings.get(st.session_state.current_index, {})
        previous_rating = previous_ratings.get(criterion)
        if previous_rating is not None:
            previous_rating_index = options_with_prompt.index(str(previous_rating))
        else:
            previous_rating_index = 0  # Default to 'Select an option'

        rating = st.selectbox(
            criterion,
            options_with_prompt,
            index=previous_rating_index,
            key=widget_key
        )
        if rating != 'Select an option':
            ratings[criterion] = int(rating)
        else:
            ratings[criterion] = None
    return ratings

def main():
    st.title("Image Evaluation")

    if not st.session_state.image_list:
        st.write("No images found in the specified folder.")
        return

    # Display progress
    progress = (st.session_state.current_index + 1) / len(st.session_state.image_list)
    st.progress(progress)

    # Display the current image
    image_name = st.session_state.image_list[st.session_state.current_index]
    st.subheader(f"Image {st.session_state.current_index + 1} of {len(st.session_state.image_list)}: {image_name}")
    show_image(image_name)

    # Get user ratings
    st.subheader("Rate the image based on the following criteria:")
    ratings = get_rating_inputs()

    # Save current ratings
    st.session_state.all_ratings[st.session_state.current_index] = ratings

    # Check if all images have been rated
    all_rated = all(
        index in st.session_state.all_ratings and None not in st.session_state.all_ratings[index].values()
        for index in range(len(st.session_state.image_list))
    )

    # Navigation buttons
    col1, col2 = st.columns(2)

    def next_image():
        # Check if all ratings are provided
        if None in ratings.values():
            st.warning("Please rate all criteria before proceeding to the next image.")
        else:
            if st.session_state.current_index < len(st.session_state.image_list) - 1:
                st.session_state.current_index += 1
                # Streamlit will rerun the script when session state changes
            else:
                st.success("You have completed rating all images!")

    with col1:
        st.button("Next", on_click=next_image)

    with col2:
        if all_rated:
            if st.button("Save Results"):
                # Build the DataFrame
                data = []
                for index, image_name in enumerate(st.session_state.image_list):
                    ratings = st.session_state.all_ratings.get(index, {})
                    row = {'Image': image_name}
                    total_score = 0
                    for criterion in st.session_state.criteria.keys():
                        rating = ratings.get(criterion)
                        if rating is not None:
                            row[criterion] = rating
                            total_score += rating
                        else:
                            row[criterion] = 'Not Rated'
                    row['Total Score'] = total_score
                    data.append(row)

                df = pd.DataFrame(data)
                # Reorder columns
                columns_order = ['Image'] + list(st.session_state.criteria.keys()) + ['Total Score']
                df = df[columns_order]

                # Save to CSV
                csv_path = 'image_ratings.csv'
                df.to_csv(csv_path, index=False)
                st.success(f"Ratings saved to {csv_path}")

                # Provide a download link
                st.download_button(
                    label="Download CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name='image_ratings.csv',
                    mime='text/csv',
                )
        else:
            st.write("You can download the results after rating all images.")

if __name__ == '__main__':
    main()
