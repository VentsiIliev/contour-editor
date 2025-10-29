import numpy as np
import cv2
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, LineString


# ==========================================================
# CLIPPING FUNCTION
# ==========================================================
def clip_segments_to_contour(segments, contour_poly):
    """
    Clip a list of 2-point segments to fit inside a given contour polygon.

    Parameters
    ----------
    segments : list of [[x1, y1], [x2, y2]]
        Line segments to clip.
    contour_poly : shapely.geometry.Polygon
        Polygon used for clipping.

    Returns
    -------
    np.ndarray
        Array of clipped segments of shape (N, 2, 2)
    """
    clipped_segments = []

    for seg in segments:
        line = LineString(seg)
        intersection = line.intersection(contour_poly)

        if intersection.is_empty:
            continue

        if intersection.geom_type == "LineString":
            coords = list(intersection.coords)
            if len(coords) == 2:
                clipped_segments.append(coords)

        elif intersection.geom_type == "MultiLineString":
            for part in intersection.geoms:
                coords = list(part.coords)
                if len(coords) == 2:
                    clipped_segments.append(coords)

    return np.array(clipped_segments)


# ==========================================================
# SPRAY PATTERN GENERATOR
# ==========================================================
def generate_spray_pattern(contour, spacing):
    """
    Generate short line segments ('spray pattern') along the longest side
    of the contour's minimum bounding rectangle, aligned with its orientation,
    clipped so they stay inside the contour.
    """
    contour_poly = Polygon(contour.squeeze())
    if not contour_poly.is_valid:
        contour_poly = contour_poly.buffer(0)

    # --- Get minimum bounding rectangle ---
    bbox = cv2.minAreaRect(contour)
    box = cv2.boxPoints(bbox)
    center = np.mean(box, axis=0)
    width, height = bbox[1]
    angle = bbox[2]

    # --- Determine orientation ---
    if width < height:
        longer_dim = height
        shorter_dim = width
        vertical = True
    else:
        longer_dim = width
        shorter_dim = height
        vertical = False

    # --- Generate initial line segments along the longest side ---
    num_segments = int(np.floor(longer_dim / spacing)) + 1
    segments = []

    for n in range(num_segments):
        offset = -longer_dim / 2 + n * spacing

        if vertical:
            pt1 = [-shorter_dim / 2, offset]
            pt2 = [shorter_dim / 2, offset]
        else:
            pt1 = [offset, -shorter_dim / 2]
            pt2 = [offset, shorter_dim / 2]

        segments.append([pt1, pt2])

    # --- Rotate and translate to match contour orientation ---
    theta = np.radians(angle)
    rot_matrix = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    transformed_segments = []
    for seg in segments:
        pt1, pt2 = seg
        pt1_rot = rot_matrix @ np.array(pt1) + center
        pt2_rot = rot_matrix @ np.array(pt2) + center
        transformed_segments.append([pt1_rot, pt2_rot])

    # --- Clip the rotated segments to stay within the contour ---
    clipped_segments = clip_segments_to_contour(transformed_segments, contour_poly)

    return clipped_segments


# ==========================================================
# TEST SHAPES
# ==========================================================
def create_shapes():
    shapes = {}
    rect = np.array([[100, 100], [400, 100], [400, 300], [100, 300]])
    shapes["rectangle"] = rect

    tri = np.array([[250, 100], [400, 400], [100, 400]])
    shapes["triangle"] = tri

    t = np.linspace(0, 2 * np.pi, 100)
    circle = np.column_stack([250 + 150 * np.cos(t), 250 + 150 * np.sin(t)])
    shapes["circle"] = circle

    t = np.linspace(0, 2 * np.pi, 6)[:-1]
    pent = np.column_stack([250 + 120 * np.cos(t), 250 + 120 * np.sin(t)])
    shapes["pentagon"] = pent

    return shapes


# ==========================================================
# VISUALIZATION FUNCTIONS
# ==========================================================
def visualize_opencv(shape_name, contour, spray_segments, spacing):
    """Draw contour and spray segments using OpenCV."""
    img = np.ones((600, 600, 3), dtype=np.uint8) * 255

    contour_int = contour.astype(np.int32).reshape((-1, 1, 2))
    cv2.drawContours(img, [contour_int], -1, (0, 0, 0), 2)

    if len(spray_segments) > 0:
        for seg in spray_segments:
            pt1, pt2 = seg
            cv2.line(
                img,
                tuple(np.int32(pt1)),
                tuple(np.int32(pt2)),
                (0, 0, 255),
                1,
                cv2.LINE_AA,
            )

    filename = f"spray_{shape_name}_cv2_s{spacing}.png"
    cv2.imwrite(filename, img)
    print(f"Saved {filename}")


def visualize_matplotlib(shape_name, contour, spray_segments, spacing):
    """Plot contour and spray segments using Matplotlib."""
    plt.figure(figsize=(5, 5))
    plt.plot(contour[:, 0], contour[:, 1], "k-", linewidth=2, label="Contour")

    if len(spray_segments) > 0:
        for seg in spray_segments:
            seg = np.array(seg)
            plt.plot(seg[:, 0], seg[:, 1], "r-", linewidth=1)

    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.title(f"{shape_name} (spacing={spacing})")
    plt.legend()
    plt.savefig(f"spray_{shape_name}_plt_s{spacing}.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved spray_{shape_name}_plt_s{spacing}.png")


# ==========================================================
# MAIN TEST EXECUTION
# ==========================================================
if __name__ == "__main__":
    shapes = create_shapes()
    spacings = [10, 20, 40]

    for name, contour in shapes.items():
        contour = contour.astype(np.float32)
        for s in spacings:
            # --- Spray pattern (clipped inside contour) ---
            spray_segments = generate_spray_pattern(contour, s)
            if len(spray_segments) > 0:
                visualize_opencv(name, contour, spray_segments, s)
                visualize_matplotlib(name, contour, spray_segments, s)
