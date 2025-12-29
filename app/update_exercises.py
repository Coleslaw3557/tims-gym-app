"""
Update script to add gif_url and form_notes to existing exercises.
Run this after updating the model to add the new columns.
"""
from sqlalchemy import text
from database import SessionLocal, engine
from models import Exercise

# GIF URLs and form notes for each exercise
EXERCISE_DATA = {
    "Back Squat": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/10/Squat.gif",
        "form_notes": """Bar on upper traps, not neck
Feet shoulder-width, toes slightly out (15-30 degrees)
Brace core hard before descent
Break at hips and knees together
Descend until hip crease below knee (parallel or deeper)
Knees track over toes, don't cave inward
Drive through whole foot, not just heels
Keep chest up throughout"""
    },
    "Romanian Deadlift": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/11/Romanian-deadlift.gif",
        "form_notes": """Stand tall with slight knee bend (15-20 degrees)
Keep knee angle locked throughout movement
Push hips back, not down
Bar slides down thighs, stays close to legs
Lower until hamstring stretch (not back rounding)
Squeeze glutes hard to stand up
Head stays neutral, don't look up"""
    },
    "Leg Press": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/12/Leg-press.gif",
        "form_notes": """Feet shoulder-width on platform
Lower weight until knees at 90 degrees
Don't let lower back round off pad
Press through heels and midfoot
Don't lock knees completely at top
Higher foot placement = more glutes/hams
Lower foot placement = more quads"""
    },
    "Lying Leg Curl": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/Lying-Leg-Curl.gif",
        "form_notes": """Pad positioned just above heels
Curl heels toward glutes
Squeeze hard at top for 1 second
Lower with control (3 sec negative)
Keep hips pressed into pad throughout
Don't let hips rise during curl"""
    },
    "Standing Calf Raise": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/standing-calf-raise-exercise.gif",
        "form_notes": """Balls of feet on edge of platform
Full stretch at bottom (2 sec pause)
Rise as high as possible
Squeeze at top (1 sec pause)
Slow controlled negative
Keep legs straight, slight knee bend OK
No bouncing at bottom"""
    },
    "Plank": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2022/02/Plank.gif",
        "form_notes": """Forearms flat on floor, elbows under shoulders
Body forms straight line from head to heels
Squeeze glutes tight
Brace abs like bracing for a punch
Don't let hips sag or pike up
Breathe normally, don't hold breath
Stop set when form breaks"""
    },
    "Bench Press": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/12/Bench-press.gif",
        "form_notes": """Grip 1.5x shoulder width
Retract shoulder blades, squeeze together
Slight arch in upper back
Feet flat on floor, driving into ground
Lower bar to mid-chest (nipple line)
Touch chest, then press
Elbows at 45 degree angle from body
Lock out over shoulders, not face"""
    },
    "Overhead Press": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/12/Overhead-press-exercise.gif",
        "form_notes": """Bar at rack, chest height
Grip slightly wider than shoulders
Unrack, bar rests on front delts
Brace core, squeeze glutes
Press straight up to lockout
Lower with control to shoulders
No leg drive (that's push press)
Head moves back as bar passes, forward once clear"""
    },
    "Incline Dumbbell Press": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/Incline-Dumbbell-Press.gif",
        "form_notes": """Bench at 30-45 degree angle
Start with dumbbells at shoulder level
Palms facing forward
Press up and slightly inward
Don't clang dumbbells at top
Lower with control until stretch in chest
Elbows at 45 degrees from body"""
    },
    "Dips": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/Dip.gif",
        "form_notes": """Grip parallel bars, arms straight
Lean torso forward 30 degrees for chest focus
Lower until upper arms parallel to floor
Keep elbows tucked, not flared
Press back up, don't lock elbows hard
Add weight with belt when 12 reps easy"""
    },
    "Lateral Raise": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/11/Dumbbell-lateral-raise.gif",
        "form_notes": """Slight bend in elbows, maintain throughout
Raise arms to sides until parallel to floor
Lead with elbows, not hands
Slight pinky-up rotation at top
Lower with control
Light weight, strict form
No swinging or shrugging"""
    },
    "Tricep Pushdown": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/11/Tricep-pushdown-exercise.gif",
        "form_notes": """Elbows pinned at sides throughout
Press handle down until arms straight
Squeeze triceps hard at bottom
Control the return to start
Stop when forearms parallel to floor
Elbows moving = cheating"""
    },
    "Cable Crunch": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/cable-crunch.gif",
        "form_notes": """Kneel facing high cable pulley with rope
Hold rope at sides of head
Contract abs to curl torso toward floor
Crunch with abs, not arms
Hold contraction 1 second
Return with control
Hips stay fixed - movement from spine flexion only"""
    },
    "Deadlift": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/12/Deadlift.gif",
        "form_notes": """Bar over mid-foot (1 inch from shins)
Hip-width stance, toes slightly out
Grip just outside legs
Chest up, back flat, shoulders over bar
Push floor away with legs
Bar drags up legs (wear long pants/socks)
Lock hips and knees together at top
Reset each rep, no bouncing"""
    },
    "Pull-ups": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/11/Pull-up.gif",
        "form_notes": """Overhand grip, just outside shoulder width
Start from dead hang, arms fully extended
Pull until chin clears bar
Drive elbows down and back
Lower with control to full extension
No kipping or swinging
Add weight when hitting 8+ reps all sets"""
    },
    "Barbell Row": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/Barbell-row-exercise.gif",
        "form_notes": """Hinge at hips, back at 45 degrees to floor
Let arms hang straight down
Pull bar to lower chest/upper abs
Squeeze shoulder blades together at top
Lower with control
Torso stays still, only arms move
Don't jerk or use momentum"""
    },
    "Lat Pulldown": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/11/lat-pulldown-exercise.gif",
        "form_notes": """Grip 1.5x shoulder width
Lean back slightly (10-15 degrees)
Pull bar to upper chest
Drive elbows down toward hips
Squeeze lats at bottom
Control the return, full stretch at top
Never pull behind neck"""
    },
    "Face Pull": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/11/Face-pull-exercise.gif",
        "form_notes": """Rope attachment at face height
Pull rope toward face, separating ends
Elbows high throughout
Externally rotate at finish (hands beside ears)
Squeeze rear delts hard
Light weight, high reps
Great for shoulder health"""
    },
    "Barbell Curl": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/barbell-biceps-curl.gif",
        "form_notes": """Shoulder-width grip, arms at sides
Curl bar up, keeping elbows pinned
Squeeze biceps hard at top
Lower with control (3 sec negative)
Full extension at bottom
No swinging or body English
Ego check the weight"""
    },
    "Hammer Curl": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/11/Hammer-Curl.gif",
        "form_notes": """Neutral grip (palms facing each other)
Keep wrist position fixed throughout
Upper arms stay still
Curl up, squeeze at top
Slow controlled negative
Builds forearm and outer bicep
Can alternate or do both together"""
    },
    "Hanging Leg Raise": {
        "gif_url": "https://www.strengthlog.com/wp-content/uploads/2020/03/hanging-leg-raise-exercise.gif",
        "form_notes": """Dead hang from bar, arms straight
Raise legs until thighs parallel to floor (or higher)
Lower with control
Minimize swing and momentum
Bend knees if straight legs too hard
Exhale on the way up
Great for lower abs"""
    },
}


def migrate_database():
    """Add new columns to exercises table if they don't exist."""
    with engine.connect() as conn:
        # Check if columns exist
        result = conn.execute(text("PRAGMA table_info(exercises)"))
        columns = [row[1] for row in result.fetchall()]

        if 'gif_url' not in columns:
            conn.execute(text("ALTER TABLE exercises ADD COLUMN gif_url VARCHAR(500)"))
            print("Added gif_url column")

        if 'form_notes' not in columns:
            conn.execute(text("ALTER TABLE exercises ADD COLUMN form_notes TEXT"))
            print("Added form_notes column")

        conn.commit()


def update_exercises():
    """Update existing exercises with GIF URLs and form notes."""
    db = SessionLocal()
    try:
        exercises = db.query(Exercise).all()
        updated = 0

        for exercise in exercises:
            if exercise.name in EXERCISE_DATA:
                data = EXERCISE_DATA[exercise.name]
                exercise.gif_url = data["gif_url"]
                exercise.form_notes = data["form_notes"]
                updated += 1
                print(f"Updated: {exercise.name}")
            else:
                print(f"No data for: {exercise.name}")

        db.commit()
        print(f"\nUpdated {updated} exercises")

    except Exception as e:
        print(f"Error updating exercises: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Migrating database...")
    migrate_database()
    print("\nUpdating exercises...")
    update_exercises()
    print("\nDone!")
