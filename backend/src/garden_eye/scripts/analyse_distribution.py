from collections.abc import Iterable

from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.artist import Artist

from garden_eye.api.database import Annotation, VideoFile, init_database
from garden_eye.helpers import WILDLIFE_COCO_LABELS, is_target_coco_annotation


def run() -> None:
    init_database()
    video_dist = get_video_distribution()
    annotation_dist = get_annotation_distribution()

    # Set up dark theme styling to match frontend
    plt.style.use("dark_background")

    # Set up the figure
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor("#0b0c10")
    ax.set_facecolor("#0b0c10")
    ax.axis("equal")

    # Define colors to match frontend theme
    colors = ["#30363d", "#4d5a6e", "#238636"]

    # Ensure both distributions have the same keys in the same order
    all_keys = ["Other", "Person", "Wildlife"]
    annotation_values = [float(annotation_dist.get(key, 0)) for key in all_keys]
    video_values = [float(video_dist.get(key, 0)) for key in all_keys]

    # Animation variables
    pause_frames = 60  # 1 second pause at start
    transition_frames = 120  # 2 seconds transition
    end_pause_frames = 60  # 1 second pause at end
    total_frames = pause_frames + transition_frames + end_pause_frames

    def animate(frame: int) -> Iterable[Artist]:
        ax.clear()
        ax.set_facecolor("#0b0c10")
        ax.axis("equal")

        if frame < pause_frames:
            # Show annotation distribution
            values = annotation_values
            title = "Annotations"
        elif frame < pause_frames + transition_frames:
            # Animate transition
            progress = (frame - pause_frames) / transition_frames
            # Cubic ease-in-out transition (slow-fast-slow)
            if progress < 0.5:
                title = "Annotations"
                # Ease in: slow start
                t = 4 * progress * progress * progress
            else:
                title = "Videos" if progress > 0.95 else "Annotations"
                # Ease out: slow end
                p = 2 * progress - 2
                t = 1 + p * p * p * 4
            values = [
                ann_val * (1 - t) + vid_val * t
                for ann_val, vid_val in zip(annotation_values, video_values, strict=False)
            ]
        else:
            # Show video distribution (hold at end)
            values = video_values
            title = "Videos"

        # Only plot if we have non-zero values
        if sum(values) > 0:
            ax.pie(
                values,
                labels=all_keys,
                autopct="%1.1f%%",
                colors=colors[: len(all_keys)],
                textprops={"color": "#e6e6e6", "fontsize": 10},
                startangle=0,
            )

        # Ensure title is always visible
        ax.set_title(title, color="#e6e6e6", fontsize=14)
        return []

    # Create animation
    anim = FuncAnimation(fig, animate, frames=total_frames, interval=33, repeat=True, blit=False)  # noqa: F841

    plt.tight_layout()
    plt.subplots_adjust(bottom=0, top=0.89)
    plt.show()


def get_video_distribution() -> dict[str, int]:
    """
    Counts the number of videos that contain:
    1. Any wildlife annotation in WILDLIFE_COCO_LABELS ("Wildlife") - the number of "Person" annotations.
    2. Only a "person" annotation ("Person").
    3. No wildlife annotations ("None").
    """
    # Count total videos
    total_count = VideoFile.select().count()

    # Count videos with target annotations (wildlife/people from WILDLIFE_COCO_LABELS)
    wildlife = (
        VideoFile.select()
        .join(Annotation)
        .where(Annotation.name.in_(list(WILDLIFE_COCO_LABELS.values())))
        .distinct()
        .count()
    )

    # Count videos with only "person" annotations
    # First get videos that have person annotations
    videos_with_person = VideoFile.select().join(Annotation).where(Annotation.name == "person").distinct()

    # Then filter to only those that have ONLY person annotations
    person_only_count = 0
    for video in videos_with_person:
        unique_annotations = Annotation.select(Annotation.name).where(Annotation.video_file == video).distinct()
        annotation_names = [ann.name for ann in unique_annotations if is_target_coco_annotation(ann.name)]
        if annotation_names == ["person"]:
            person_only_count += 1

    wildlife -= person_only_count
    none_count = total_count - wildlife - person_only_count

    return {
        "Other": none_count,
        "Person": person_only_count,
        "Wildlife": wildlife,
    }


def get_annotation_distribution() -> dict[str, int]:
    """
    Counts the number of annotations by category:
    1. Wildlife annotations (non-person animals from WILDLIFE_COCO_LABELS) ("Wildlife").
    2. Person annotations ("Person").
    3. Other annotations not in WILDLIFE_COCO_LABELS ("Other").
    """
    # Count person annotations
    person_count = Annotation.select().where(Annotation.name == "person").count()

    # Count wildlife annotations (all target annotations except person)
    wildlife_labels = [label for label in WILDLIFE_COCO_LABELS.values() if label != "person"]
    wildlife_count = Annotation.select().where(Annotation.name.in_(wildlife_labels)).count()

    # Count other annotations (not in WILDLIFE_COCO_LABELS)
    all_wildlife_labels = list(WILDLIFE_COCO_LABELS.values())
    other_count = Annotation.select().where(Annotation.name.not_in(all_wildlife_labels)).count()

    return {
        "Other": other_count,
        "Person": person_count,
        "Wildlife": wildlife_count,
    }


if __name__ == "__main__":
    run()
