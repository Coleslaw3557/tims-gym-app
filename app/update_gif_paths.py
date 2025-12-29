"""
Update exercises with local GIF paths and add GIFs to images array.
"""
from sqlalchemy.orm.attributes import flag_modified
from database import SessionLocal
from models import Exercise
import json
import copy

# Mapping of exercise names to their local GIF filename
GIF_FILENAMES = {
    "Back Squat": "back-squat.gif",
    "Romanian Deadlift": "romanian-deadlift.gif",
    "Leg Press": "leg-press.gif",
    "Lying Leg Curl": "lying-leg-curl.gif",
    "Standing Calf Raise": "standing-calf-raise.gif",
    "Plank": "plank.gif",
    "Bench Press": "bench-press.gif",
    "Overhead Press": "overhead-press.gif",
    "Incline Dumbbell Press": "incline-dumbbell-press.gif",
    "Dips": "dips.gif",
    "Lateral Raise": "lateral-raise.gif",
    "Tricep Pushdown": "tricep-pushdown.gif",
    "Cable Crunch": "cable-crunch.gif",
    "Deadlift": "deadlift.gif",
    "Pull-ups": "pull-ups.gif",
    "Barbell Row": "barbell-row.gif",
    "Lat Pulldown": "lat-pulldown.gif",
    "Face Pull": "face-pull.gif",
    "Barbell Curl": "barbell-curl.gif",
    "Hammer Curl": "hammer-curl.gif",
    "Hanging Leg Raise": "hanging-leg-raise.gif",
}


def update_gif_paths():
    """Update exercises with local GIF paths and add to images array."""
    db = SessionLocal()
    try:
        exercises = db.query(Exercise).all()
        updated = 0

        for exercise in exercises:
            if exercise.name in GIF_FILENAMES:
                gif_filename = GIF_FILENAMES[exercise.name]
                local_gif_path = f"/static/images/gifs/{gif_filename}"

                # Update gif_url to local path
                exercise.gif_url = local_gif_path

                # Get current images array - make a deep copy to ensure SQLAlchemy detects change
                current_images = copy.deepcopy(exercise.images) if exercise.images else []
                if isinstance(current_images, str):
                    current_images = json.loads(current_images) if current_images else []

                # Check if GIF is already in the images array
                gif_exists = any(img.get('url') == local_gif_path for img in current_images)

                if not gif_exists:
                    # Add GIF as the first item in images array
                    gif_entry = {
                        "url": local_gif_path,
                        "caption": f"{exercise.name} - Animated demonstration"
                    }
                    current_images.insert(0, gif_entry)

                # Reassign to trigger SQLAlchemy change detection
                exercise.images = current_images
                flag_modified(exercise, "images")

                updated += 1
                print(f"Updated: {exercise.name} -> {local_gif_path}")
            else:
                print(f"No GIF mapping for: {exercise.name}")

        db.commit()
        print(f"\nUpdated {updated} exercises with local GIF paths")

    except Exception as e:
        print(f"Error updating exercises: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    update_gif_paths()
