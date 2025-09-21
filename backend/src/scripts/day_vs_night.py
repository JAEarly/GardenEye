import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backend_bases import Event, MouseEvent
from PIL import Image

from garden_eye.api.database import VideoFile, get_thumbnail_path, init_database


def run() -> None:
    init_database()
    mean_rgbs_list = []
    for vf in VideoFile.select():
        thumbnail_path = get_thumbnail_path(vf)
        thumbnail = np.asarray(Image.open(thumbnail_path))
        mean_rgb = thumbnail.mean(axis=(0, 1))
        mean_rgbs_list.append(mean_rgb)

    # 3D plot of RGB values
    mean_rgbs = np.array(mean_rgbs_list)

    # Set up dark theme styling to match frontend
    plt.style.use("dark_background")

    fig = plt.figure(figsize=(10, 8))
    fig.patch.set_facecolor("#0b0c10")
    ax = fig.add_subplot(111, projection="3d")
    ax.set_facecolor("#0b0c10")

    # Extract R, G, B channels
    r_values = mean_rgbs[:, 0]
    g_values = mean_rgbs[:, 1]
    b_values = mean_rgbs[:, 2]

    # Create scatter plot with colors based on actual RGB values (normalized)
    colors = mean_rgbs / 255.0  # Normalize to 0-1 for matplotlib
    ax.scatter(r_values, g_values, b_values, c=colors, s=100, alpha=0.7)

    # Draw line where red == green == blue (grayscale line)
    min_val = min(r_values.min(), g_values.min(), b_values.min())
    max_val = max(r_values.max(), g_values.max(), b_values.max())
    line_coords = np.linspace(min_val, max_val, 100)

    # Create the grayscale line where R=G=B
    ax.plot(line_coords, line_coords, line_coords, color="gray", linewidth=3, alpha=0.7)

    ax.set_xlabel("Red", color="#e6e6e6")
    ax.set_ylabel("Green", color="#e6e6e6")
    ax.set_zlabel("Blue", color="#e6e6e6")

    # Set tick colors to match theme
    ax.tick_params(colors="#e6e6e6")

    # Set 3D axes panes to white
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.xaxis.pane.set_edgecolor("white")
    ax.yaxis.pane.set_edgecolor("white")
    ax.zaxis.pane.set_edgecolor("white")
    ax.xaxis.pane.set_alpha(1)
    ax.yaxis.pane.set_alpha(1)
    ax.zaxis.pane.set_alpha(1)

    ax.view_init(elev=11, roll=0)

    # Lock elevation and roll, only allow azimuth changes
    def on_move(event: Event) -> None:
        if isinstance(event, MouseEvent) and event.inaxes == ax:
            ax.view_init(elev=11, azim=ax.azim, roll=0)
            fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", on_move)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run()
