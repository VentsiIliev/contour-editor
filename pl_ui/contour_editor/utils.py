import numpy as np
import cv2
from PyQt6.QtGui import QImage, QPixmap
from matplotlib import pyplot as plt
from shapely.geometry import Polygon, LineString


def zigZag(contour, spacing):
    # Convert contour to a Shapely polygon
    contour_poly = Polygon(contour.squeeze())
    if not contour_poly.is_valid:
        contour_poly = contour_poly.buffer(0)  # Fix self-intersections if any

    # Get rotated bounding box
    bbox = cv2.minAreaRect(contour)
    box = cv2.boxPoints(bbox)
    center = np.mean(box, axis=0)
    width, height = bbox[1]
    angle = bbox[2]

    if width < height:
        shorter_dim = width
        longer_dim = height
        vertical = True
    else:
        shorter_dim = height
        longer_dim = width
        vertical = False

    # Generate zigzag lines in the bbox's local frame (unrotated)
    # Generate zigzag lines in the bbox's local frame (unrotated)
    lines = []
    num_lines = int(np.floor(shorter_dim / spacing)) + 1  # ensure coverage to the far edge

    for n in range(num_lines):
        offset = n * spacing

        if vertical:
            # start exactly at left edge (-shorter_dim/2)
            x = -shorter_dim / 2 + offset
            pt1 = [x, -longer_dim / 2]
            pt2 = [x, longer_dim / 2]
        else:
            # start exactly at bottom edge (-shorter_dim/2)
            y = -shorter_dim / 2 + offset
            pt1 = [-longer_dim / 2, y]
            pt2 = [longer_dim / 2, y]

        lines.append((pt1, pt2))

    # Rotate and translate lines to match the actual bbox orientation
    theta = np.radians(angle)
    rot_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    final_coords = []
    for pt1, pt2 in lines:
        # Rotate
        pt1_rot = rot_matrix @ np.array(pt1) + center
        pt2_rot = rot_matrix @ np.array(pt2) + center

        # Clip line with actual contour
        line = LineString([pt1_rot, pt2_rot])
        clipped = line.intersection(contour_poly)

        # Add resulting points or line segments
        if clipped.is_empty:
            continue
        elif clipped.geom_type == "LineString":
            final_coords.extend(list(clipped.coords))
        elif clipped.geom_type == "MultiLineString":
            for part in clipped.geoms:
                final_coords.extend(list(part.coords))

    return np.array(final_coords)


def shrink_contour_points(contour_points, shrink_amount):
    """
    Shrink a polygon defined by contour_points inward by shrink_amount.
    Returns the new contour points as a numpy array.
    """
    from shapely.geometry import Polygon

    if len(contour_points) < 3:
        return None

    poly = Polygon(contour_points)
    if not poly.is_valid:
        poly = poly.buffer(0)

    shrunk_poly = poly.buffer(-shrink_amount)
    if shrunk_poly.is_empty:
        return None

    if shrunk_poly.geom_type == "MultiPolygon":
        shrunk_poly = max(shrunk_poly.geoms, key=lambda p: p.area)

    return np.array(shrunk_poly.exterior.coords)


def qpixmap_to_cv(qpixmap):
    qimage = qpixmap.toImage().convertToFormat(QImage.Format.Format_RGB888)
    width = qimage.width()
    height = qimage.height()
    ptr = qimage.bits()
    ptr.setsize(height * width * 3)
    arr = np.array(ptr, dtype=np.uint8).reshape((height, width, 3))
    return arr


def create_light_gray_pixmap(width=1280, height=720):
    # Create a light gray image (RGB)
    gray_value = 200  # 0=black, 255=white
    img = np.full((height, width, 3), gray_value, dtype=np.uint8)
    # Convert numpy image to QImage
    qimage = QImage(img.data, width, height, 3 * width, QImage.Format.Format_RGB888)

    # Convert QImage to QPixmap
    pixmap = QPixmap.fromImage(qimage)

    return pixmap


# --- shape generators ---
def rectangle():
    return np.array([[0, 0], [200, 0], [200, 100], [0, 100]])


def circle(num_points=100, radius=80, center=(100, 100)):
    angles = np.linspace(0, 2 * np.pi, num_points)
    return np.array([[center[0] + radius * np.cos(a), center[1] + radius * np.sin(a)] for a in angles])


def irregular():
    return np.array([[0, 0], [120, 30], [100, 80], [50, 100], [10, 60]])


def concave():
    return np.array([[0, 0], [100, 0], [100, 100], [60, 60], [0, 100]])


def blob(n=8, radius=80, center=(100, 100), noise=30):
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
    r = radius + np.random.randn(n) * noise
    return np.array([[center[0] + r[i] * np.cos(a), center[1] + r[i] * np.sin(a)] for i, a in enumerate(angles)])


# --- visualization ---
def visualize_zigzag(contour, title, spacing=10):
    zz = zigZag(contour.astype(np.float32), spacing)

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.set_xlim(-20, 250)
    ax.set_ylim(-20, 250)

    # Plot original contour
    c = np.vstack([contour, contour[0]])  # close loop
    ax.plot(c[:, 0], c[:, 1], 'k-', lw=2, label="Contour")

    # Plot zigzag
    if len(zz) > 1:
        ax.plot(zz[:, 0], zz[:, 1], 'r-', lw=1, label="ZigZag Lines")

    ax.legend()
    plt.show()


# --- run all tests ---
if __name__ == "__main__":
    np.random.seed(42)
    shapes = {
        "Rectangle": rectangle(),
        "Circle": circle(),
        "Irregular Polygon": irregular(),
        "Concave Shape": concave(),
        "Blobby Shape": blob(),
    }

    for name, contour in shapes.items():
        visualize_zigzag(contour, name, spacing=10)
