import cv2
import numpy as np

def detect_edges(image_path):
    # Read the image
    img = cv2.imread(image_path)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply GaussianBlur to reduce noise and help edge detection
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use Canny edge detector
    edges = cv2.Canny(blurred, 50, 150)

    # Display the original and edge-detected images at original size
    # cv2.imshow('Original Image', cv2.resize(img, (img.shape[1] // 2, img.shape[0] // 2)))
    cv2.imshow('Edge Detection', cv2.resize(edges, (edges.shape[1] // 2, edges.shape[0] // 2)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    image_path = '''img/WhatsApp Image 2024-01-09 at 3.33.22 PM.jpeg'''  # Replace with the actual path to your car image
    detect_edges(image_path)
