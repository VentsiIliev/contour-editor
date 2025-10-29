from matplotlib import pyplot as plt


def visualize_and_save(shape_name, contour, result_coords, spacing):
    plt.figure(figsize=(5,5))
    plt.plot(contour[:,0], contour[:,1], 'k-', linewidth=2, label='Contour')
    if len(result_coords) > 0 and result_coords.ndim == 2:
        plt.plot(result_coords[:,0], result_coords[:,1], 'r-', linewidth=1, label='Pattern')
    plt.gca().invert_yaxis()
    plt.axis("equal")
    plt.legend()
    plt.title(f"{shape_name} (spacing={spacing})")
    plt.savefig(f"zigzag_{shape_name}_s{spacing}.png", dpi=150, bbox_inches='tight')
    plt.close()
