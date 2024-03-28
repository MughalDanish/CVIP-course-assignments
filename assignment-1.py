import sys
import numpy as np
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog

class CanvasApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Canvas Generator')
        self.setGeometry(100, 100, 300, 150)

        self.button = QPushButton('Choose Images', self)
        self.button.clicked.connect(self.choose_images)

        layout = QVBoxLayout()
        layout.addWidget(self.button)
        self.setLayout(layout)

    def choose_images(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(self, 'Select Images', '', 'Image files (*.jpg *.jpeg *.png)')

        if file_paths:
            self.generate_canvas(file_paths)

    def generate_canvas(self, selected_images):
        # A4 dimensions in pixels at 300 DPI
        a4_width_px, a4_height_px = 3307, 2381

        # Create a blank white canvas (A4 size)
        canvas = np.ones((a4_height_px, a4_width_px, 3), dtype=np.uint8) * 255

        # Outer rectangle dimensions in pixels
        outer_rect_width_px, outer_rect_height_px = 840, 1140

        # Assuming equal spacing and centering the frames, calculate the margins
        horizontal_margin = (a4_width_px - 2 * outer_rect_width_px) // 6
        vertical_margin = (a4_height_px - 2 * outer_rect_height_px) // 4

        # Additional horizontal spacing from the left side
        horizontal_left_spacing = -250  # Adjust this value to control the additional spacing from the left side

        # Function to place the nine Polaroid frames on the canvas
        def place_frames():
            for row in range(2):  # 3 rows
                for col in range(3):  # 3 columns
                    x = horizontal_margin + col * (outer_rect_width_px + horizontal_margin) + (col * horizontal_left_spacing)
                    y = vertical_margin + row * (outer_rect_height_px + vertical_margin)

                    # For visualization, draw the rectangles
                    cv2.rectangle(canvas, (x, y), (x + outer_rect_width_px, y + outer_rect_height_px), (0, 0, 0), 2)

        # Function to place the resized image at the start of the inner rectangle of a frame
        def place_resized_image(img, frame_position, top_difference):
            # Get the dimensions of the image
            img_h, img_w = img.shape[:2]

            # Calculate the position for the image in the collage
            y_img_offset = frame_position[1] + top_difference
            x_img_offset = frame_position[0] + (outer_rect_width_px - img_w) // 2  # Adjusted to shift the image towards the left edge

            # Calculate the region where the image will be placed
            img_region = canvas[y_img_offset:y_img_offset + img_h, x_img_offset:x_img_offset + img_w]

            # Ensure that the image fits by taking the minimum of the two shapes
            canvas[y_img_offset:y_img_offset + img_h, x_img_offset:x_img_offset + img_w] = img[:img_region.shape[0], :img_region.shape[1]]

        # Draw/place the Polaroid frames on the canvas
        place_frames()

        # Inside your loop where you process each image:
        for i, img_path in enumerate(selected_images):
            img = cv2.imread(img_path)

            resized_img = resize_image(img, 790)
            # Check if the resized image height is greater than the available height in the rectangle
            if resized_img.shape[1] > outer_rect_width_px:
                # Rotate the image 90 degrees clockwise
                rotated_img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                # Use the rotated image for placement
                resized_img = resize_image(rotated_img, 850)

            # Set the differences for top and bottom placement
            top_difference = 50
            bottom_difference = 150

            frame_position = (horizontal_margin + (i % 3) * (outer_rect_width_px + horizontal_margin) + (i % 3 * horizontal_left_spacing),
                              vertical_margin + (i // 3) * (outer_rect_height_px + vertical_margin))
            place_resized_image(resized_img, frame_position, top_difference)
        
        # Open a file dialog to get the save path
        save_path, _ = QFileDialog.getSaveFileName(self, 'Save Canvas', '', 'PNG files (*.png);;All files (*.*)')
   
        if save_path:
            # Save the canvas to a file
            cv2.imwrite(save_path, canvas)
            print(f"Canvas saved to {save_path}")

def resize_image(image, target_height):
    # Calculate the ratio of the target height to the original height
    r = target_height / image.shape[0]

    # Calculate the new dimensions
    dim = (int(image.shape[1] * r), target_height)

    # Perform the resizing
    resized = cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

    return resized

def main():
    app = QApplication(sys.argv)
    canvas_app = CanvasApp()
    canvas_app.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
