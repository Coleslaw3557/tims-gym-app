"""
Migration: Restructure mobility placement and remove Hammer Curl

Changes:
- Remove Hammer Curl from Day 3
- Day 1: 90/90 pre-workout, Hip Flexor + Ankle post-workout
- Day 2: T-spine + Shoulder Dislocates pre-workout, Dead Hang post-workout
- Day 3: T-spine + Shoulder Dislocates pre-workout, Dead Hang post-workout
"""

from sqlalchemy import text
from database import SessionLocal, engine

# New sort order mapping: (day, exercise_name) -> sort_order
NEW_SORT_ORDER = {
    # Day 1 - Lower Body
    (1, "90/90 Hip Switch"): 0,       # Dynamic pre-workout
    (1, "Back Squat"): 1,
    (1, "Romanian Deadlift"): 2,
    (1, "Leg Press"): 3,
    (1, "Lying Leg Curl"): 4,
    (1, "Standing Calf Raise"): 5,
    (1, "Plank"): 6,
    (1, "Hip Flexor Stretch"): 7,     # Static post-workout
    (1, "Ankle Mobility Drill"): 8,   # Static post-workout

    # Day 2 - Upper Push
    (2, "Thoracic Spine Rotation"): 0,  # Dynamic pre-workout
    (2, "Shoulder Dislocates"): 1,      # Dynamic pre-workout
    (2, "Bench Press"): 2,
    (2, "Overhead Press"): 3,
    (2, "Incline Dumbbell Press"): 4,
    (2, "Dips"): 5,
    (2, "Lateral Raise"): 6,
    (2, "Tricep Pushdown"): 7,
    (2, "Cable Crunch"): 8,
    (2, "Dead Hang"): 9,                # Static post-workout

    # Day 3 - Upper Pull
    (3, "Thoracic Spine Rotation"): 0,  # Dynamic pre-workout
    (3, "Shoulder Dislocates"): 1,      # Dynamic pre-workout
    (3, "Deadlift"): 2,
    (3, "Pull-ups"): 3,
    (3, "Barbell Row"): 4,
    (3, "Lat Pulldown"): 5,
    (3, "Face Pull"): 6,
    (3, "Barbell Curl"): 7,
    (3, "Hanging Leg Raise"): 8,
    (3, "Dead Hang"): 9,                # Static post-workout
}


def migrate():
    db = SessionLocal()
    try:
        # 1. Delete Hammer Curl exercise and its program_exercise entry
        print("Removing Hammer Curl...")

        # First delete from program_exercises (foreign key constraint)
        db.execute(text("""
            DELETE FROM program_exercises
            WHERE exercise_id = (SELECT id FROM exercises WHERE name = 'Hammer Curl')
        """))

        # Then delete from exercises
        db.execute(text("DELETE FROM exercises WHERE name = 'Hammer Curl'"))

        # 2. Update sort_order for all program exercises
        print("Updating exercise order...")

        for (day, exercise_name), sort_order in NEW_SORT_ORDER.items():
            db.execute(text("""
                UPDATE program_exercises
                SET sort_order = :sort_order
                WHERE day = :day
                AND exercise_id = (SELECT id FROM exercises WHERE name = :name)
            """), {"sort_order": sort_order, "day": day, "name": exercise_name})

        db.commit()
        print("Migration complete!")

        # Verify changes
        result = db.execute(text("""
            SELECT pe.day, e.name, pe.sort_order
            FROM program_exercises pe
            JOIN exercises e ON pe.exercise_id = e.id
            ORDER BY pe.day, pe.sort_order
        """))

        print("\nNew exercise order:")
        current_day = 0
        for row in result:
            if row[0] != current_day:
                current_day = row[0]
                print(f"\n--- Day {current_day} ---")
            print(f"  {row[2]:2d}. {row[1]}")

    except Exception as e:
        print(f"Migration failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
