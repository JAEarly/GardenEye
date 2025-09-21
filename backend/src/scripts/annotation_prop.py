import numpy as np
from matplotlib import pyplot as plt

from garden_eye.api.database import VideoFile, init_database


def run() -> None:
    init_database()

    # Get all videos with wildlife proportions
    videos = VideoFile.select().where(VideoFile.wildlife_prop.is_null(False))
    proportions = [video.wildlife_prop for video in videos if video.wildlife_prop > 0]

    if not proportions:
        print("No videos with wildlife proportions found in database")
        return

    # Set up dark theme styling to match frontend
    plt.style.use("dark_background")

    # Set up the figure for phone layout (9:16 aspect ratio)
    fig, ax = plt.subplots(figsize=(6, 8))
    fig.patch.set_facecolor("#0b0c10")
    ax.set_facecolor("#0b0c10")

    # Create horizontal histogram
    bins = np.linspace(0, 1, 21).tolist()  # 20 bins from 0 to 1
    n, bins, patches = ax.hist(proportions, bins=bins, orientation="horizontal", edgecolor="#e6e6e6", alpha=0.8)

    # Color bars based on proportion value - gradient from grey to green
    for i, patch in enumerate(patches):  # type: ignore[arg-type]
        # Calculate proportion for this bin (use bin center)
        bin_center = (bins[i] + bins[i + 1]) / 2
        # Interpolate color from grey (#30363d) to green (#238636)
        if bin_center == 0:
            color = "#30363d"  # Grey for 0 proportion
        else:
            # Blend from grey to green based on proportion
            color = "#238636"  # Green for any wildlife
        patch.set_facecolor(color)

    # Styling to match analyse_distribution.py
    ax.set_xlabel("Number of Videos", color="#e6e6e6", fontsize=12)
    ax.set_ylabel("Wildlife Proportion", color="#e6e6e6", fontsize=12)

    # Invert y-axis so 1 is at top and 0 at bottom
    ax.invert_yaxis()
    # ax.set_title("Distribution of Non-Zero Wildlife Annotation Proportions", color="#e6e6e6", fontsize=14)
    ax.tick_params(colors="#e6e6e6")
    ax.grid(True, alpha=0.3, color="#4d5a6e")

    ax.set_ylim(0, 1)

    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    run()
