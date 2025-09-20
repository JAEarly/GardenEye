from matplotlib import pyplot as plt

from garden_eye.api.database import Annotation, VideoFile, init_database
from garden_eye.helpers import WILDLIFE_COCO_LABELS, is_target_coco_annotation


def run() -> None:
    init_database()
    video_dist = get_video_distribution()
    annotation_dist = get_annotation_distribution()

    # Set up dark theme styling to match frontend
    plt.style.use("dark_background")

    scale = 0.6
    fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(9 * scale, 16 * scale))
    fig.patch.set_facecolor("#0b0c10")  # Match frontend background

    # Define colors to match frontend theme
    colors = ["#30363d", "#4d5a6e", "#238636"]  # Green, gray-blue, dark gray

    # Video distribution pie chart
    axes[1].pie(
        video_dist.values(),
        labels=video_dist.keys(),
        autopct="%1.1f%%",
        colors=colors[: len(video_dist)],
        textprops={"color": "#e6e6e6", "fontsize": 10},
        startangle=0,
    )
    axes[1].set_title("Video Distribution", color="#e6e6e6", fontsize=12, pad=0)
    axes[1].set_facecolor("#0b0c10")

    # Annotation distribution pie chart
    axes[0].pie(
        annotation_dist.values(),
        labels=annotation_dist.keys(),
        autopct="%1.1f%%",
        colors=colors[: len(annotation_dist)],
        textprops={"color": "#e6e6e6", "fontsize": 10},
        startangle=0,
    )
    axes[0].set_title("Annotation Distribution", color="#e6e6e6", fontsize=12, pad=0)
    axes[0].set_facecolor("#0b0c10")

    plt.tight_layout()
    plt.subplots_adjust(hspace=0.35, top=0.92, bottom=0.04)  # Increase space between subplots
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
        "None": none_count,
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
