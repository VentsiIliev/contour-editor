import numpy as np
import cv2
from shapely.geometry import Polygon, LineString
import matplotlib.pyplot as plt
from visualize_and_save import visualize_and_save
import numpy as np
import cv2

from create_shapes import create_shapes
# --- Function under test ---
def zigZag(contour, spacing):
    contour_poly = Polygon(contour.squeeze())
    if not contour_poly.is_valid:
        contour_poly = contour_poly.buffer(0)

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

    lines = []
    num_lines = int(np.floor(shorter_dim / spacing)) + 1

    for n in range(num_lines):
        offset = n * spacing

        if vertical:
            x = -shorter_dim / 2 + offset
            pt1 = [x, -longer_dim / 2]
            pt2 = [x, longer_dim / 2]
        else:
            y = -shorter_dim / 2 + offset
            pt1 = [-longer_dim / 2, y]
            pt2 = [longer_dim / 2, y]

        lines.append((pt1, pt2))

    theta = np.radians(angle)
    rot_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    final_coords = []
    for pt1, pt2 in lines:
        pt1_rot = rot_matrix @ np.array(pt1) + center
        pt2_rot = rot_matrix @ np.array(pt2) + center
        line = LineString([pt1_rot, pt2_rot])
        clipped = line.intersection(contour_poly)

        if clipped.is_empty:
            continue
        elif clipped.geom_type == "LineString":
            final_coords.extend(list(clipped.coords))
        elif clipped.geom_type == "MultiLineString":
            for part in clipped.geoms:
                final_coords.extend(list(part.coords))

    return np.array(final_coords)


# --- Visualization & Saving ---
def visualize_and_save(shape_name, contour, result_coords, spacing):
    plt.figure(figsize=(5,5))
    plt.plot(contour[:,0], contour[:,1], 'k-', linewidth=2, label='Contour')
    if len(result_coords) > 0:
        plt.plot(result_coords[:,0], result_coords[:,1], 'r-', linewidth=1, label='ZigZag')
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.legend()
    plt.title(f"{shape_name} (spacing={spacing})")
    plt.savefig(f"zigzag_{shape_name}_s{spacing}.png", dpi=150, bbox_inches='tight')
    plt.close()


# --- Run Tests ---
if __name__ == "__main__":
    shapes = create_shapes()
    spacings = [10, 20, 40]

    for name, contour in shapes.items():
        contour = contour.astype(np.float32)
        for s in spacings:
            result = zigZag(contour, s)
            # Spray pattern

            visualize_and_save(name, contour, result, s)
            print(f"Saved zigzag_{name}_s{s}.png")



