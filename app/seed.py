from database import SessionLocal
from models import Exercise, ProgramExercise

EXERCISES = [
    # Day 1 - Lower Body
    {
        "name": "Back Squat",
        "description": "Bar on upper traps. Feet shoulder-width, toes slightly out. Brace core, break at hips and knees together. Descend until hip crease below knee. Knees track over toes. Drive through whole foot.",
        "target_muscles": "Quads, glutes, hamstrings, core",
        "image_url": "/static/images/back-squat.png",
        "images": [
            {"url": "/static/images/back-squat.png", "caption": "Setup with bar on traps"},
            {"url": "/static/images/back-squat-2.jpg", "caption": "Descent phase"},
            {"url": "/static/images/back-squat-3.jpg", "caption": "Bottom position"},
        ],
        "guide_url": None,
        "default_rest_sec": 180,
        "day": 1,
        "sets": 4,
        "reps_min": 5,
        "reps_max": None,
        "notes": "Add 5lbs/week when all reps complete with good form.",
    },
    {
        "name": "Romanian Deadlift",
        "description": "Stand tall, slight knee bend (15-20°), keep locked throughout. Push hips back, bar slides down thighs. Lower until hamstring stretch or back starts to round. Squeeze glutes to stand.",
        "target_muscles": "Hamstrings, glutes, lower back",
        "image_url": "/static/images/romanian-deadlift.png",
        "images": [
            {"url": "/static/images/romanian-deadlift.png", "caption": "Starting position"},
            {"url": "/static/images/romanian-deadlift-2.jpg", "caption": "Hip hinge descent"},
            {"url": "/static/images/romanian-deadlift-3.jpg", "caption": "Bottom stretch position"},
        ],
        "guide_url": None,
        "default_rest_sec": 180,
        "day": 1,
        "sets": 4,
        "reps_min": 5,
        "reps_max": None,
        "notes": "Feel stretch in hamstrings. Bar stays close to legs.",
    },
    {
        "name": "Leg Press",
        "description": "Feet shoulder-width, mid-platform. Lower weight until knees at 90°. Press through heels. Don't lock knees at top. Keep lower back flat against pad.",
        "target_muscles": "Quads, glutes",
        "image_url": "/static/images/leg-press.png",
        "images": [
            {"url": "/static/images/leg-press.png", "caption": "Foot placement setup"},
            {"url": "/static/images/leg-press-2.jpg", "caption": "Lowering phase"},
            {"url": "/static/images/leg-press-3.jpg", "caption": "Bottom position at 90°"},
        ],
        "guide_url": None,
        "default_rest_sec": 120,
        "day": 1,
        "sets": 3,
        "reps_min": 8,
        "reps_max": 12,
        "notes": "Higher feet = more glutes/hams. Lower feet = more quads.",
    },
    {
        "name": "Lying Leg Curl",
        "description": "Pad just above heels. Curl heels toward glutes, squeeze hard at top. Lower with control (3 sec negative). Keep hips pressed into pad.",
        "target_muscles": "Hamstrings",
        "image_url": "/static/images/lying-leg-curl.png",
        "images": [
            {"url": "/static/images/lying-leg-curl.png", "caption": "Starting position"},
            {"url": "/static/images/lying-leg-curl-2.jpg", "caption": "Mid curl"},
            {"url": "/static/images/lying-leg-curl-3.jpg", "caption": "Full contraction"},
        ],
        "guide_url": None,
        "default_rest_sec": 90,
        "day": 1,
        "sets": 3,
        "reps_min": 10,
        "reps_max": 15,
        "notes": "Don't let hips rise. Slow negative builds muscle.",
    },
    {
        "name": "Standing Calf Raise",
        "description": "Balls of feet on edge. Full stretch at bottom (2 sec). Rise as high as possible, squeeze at top (1 sec). Slow negative.",
        "target_muscles": "Calves",
        "image_url": "/static/images/standing-calf-raise.png",
        "images": [
            {"url": "/static/images/standing-calf-raise.png", "caption": "Machine setup"},
            {"url": "/static/images/standing-calf-raise-2.jpg", "caption": "Bottom stretch"},
            {"url": "/static/images/standing-calf-raise-3.jpg", "caption": "Top contraction"},
        ],
        "guide_url": None,
        "default_rest_sec": 90,
        "day": 1,
        "sets": 4,
        "reps_min": 12,
        "reps_max": 15,
        "notes": "Full ROM is key. No bouncing.",
    },
    {
        "name": "Plank",
        "description": "Forearms on floor, elbows under shoulders. Body straight line from head to heels. Squeeze glutes, brace abs like taking a punch. Breathe normally.",
        "target_muscles": "Core",
        "image_url": "/static/images/plank.jpg",
        "images": [
            {"url": "/static/images/plank.jpg", "caption": "Proper plank position"},
            {"url": "/static/images/plank-2.jpg", "caption": "Side view alignment"},
            {"url": "/static/images/plank-3.jpg", "caption": "Full body tension"},
        ],
        "guide_url": None,
        "default_rest_sec": 60,
        "day": 1,
        "sets": 3,
        "reps_min": 30,
        "reps_max": 60,
        "notes": "Reps = seconds. Hips sagging = stop the set.",
    },
    # Day 2 - Upper Push
    {
        "name": "Bench Press",
        "description": "Grip 1.5x shoulder width. Retract scapula, arch upper back, feet flat. Unrack, lower to mid-chest (nipple line). Touch and press, elbows 45° from body. Lock out over shoulders.",
        "target_muscles": "Chest, triceps, front delts",
        "image_url": "/static/images/bench-press.png",
        "images": [
            {"url": "/static/images/bench-press.png", "caption": "Setup and grip"},
            {"url": "/static/images/bench-press-2.jpg", "caption": "Lowering to chest"},
            {"url": "/static/images/bench-press-3.jpg", "caption": "Press phase"},
        ],
        "guide_url": None,
        "default_rest_sec": 180,
        "day": 2,
        "sets": 4,
        "reps_min": 5,
        "reps_max": None,
        "notes": "Add 5lbs/week. Squeeze bar hard, drive feet into floor.",
    },
    {
        "name": "Overhead Press",
        "description": "Grip just outside shoulders. Bar rests on front delts. Brace core, squeeze glutes. Press straight up, move head back then forward as bar passes. Lock out with bar over mid-foot.",
        "target_muscles": "Shoulders, triceps",
        "image_url": "/static/images/overhead-press.jpg",
        "images": [
            {"url": "/static/images/overhead-press.jpg", "caption": "Starting position"},
            {"url": "/static/images/overhead-press-2.jpg", "caption": "Mid-press"},
            {"url": "/static/images/overhead-press-3.jpg", "caption": "Lockout position"},
        ],
        "guide_url": None,
        "default_rest_sec": 180,
        "day": 2,
        "sets": 4,
        "reps_min": 5,
        "reps_max": None,
        "notes": "Strict form. No leg drive or back lean.",
    },
    {
        "name": "Incline Dumbbell Press",
        "description": "Bench 30-45°. Start with DBs at shoulder level, palms forward. Press up and slightly in. Lower with control until stretch in chest. Elbows 45° from body.",
        "target_muscles": "Upper chest, front delts, triceps",
        "image_url": "/static/images/incline-dumbbell-press.png",
        "images": [
            {"url": "/static/images/incline-dumbbell-press.png", "caption": "Setup on incline"},
            {"url": "/static/images/incline-dumbbell-press-2.jpg", "caption": "Bottom position"},
            {"url": "/static/images/incline-dumbbell-press-3.jpg", "caption": "Press to top"},
        ],
        "guide_url": None,
        "default_rest_sec": 120,
        "day": 2,
        "sets": 3,
        "reps_min": 8,
        "reps_max": 12,
        "notes": "Don't clang DBs at top. Control the weight.",
    },
    {
        "name": "Dips",
        "description": "Grip bars, arms straight. Lean torso forward 30° for chest focus. Lower until upper arms parallel to floor. Press back up, don't lock elbows hard.",
        "target_muscles": "Chest, triceps, front delts",
        "image_url": "/static/images/dips.png",
        "images": [
            {"url": "/static/images/dips.png", "caption": "Starting position"},
            {"url": "/static/images/dips-2.jpg", "caption": "Lowering phase"},
            {"url": "/static/images/dips-3.jpg", "caption": "Bottom position"},
        ],
        "guide_url": None,
        "default_rest_sec": 120,
        "day": 2,
        "sets": 3,
        "reps_min": 8,
        "reps_max": 12,
        "notes": "Add weight with belt when hitting 12 reps easy.",
    },
    {
        "name": "Lateral Raise",
        "description": "Slight bend in elbows, maintain throughout. Raise arms to side until parallel to floor. Lead with elbows, pinkies slightly higher than thumbs. Lower with control.",
        "target_muscles": "Side delts",
        "image_url": "/static/images/lateral-raise.jpg",
        "images": [
            {"url": "/static/images/lateral-raise.jpg", "caption": "Starting position"},
            {"url": "/static/images/lateral-raise-2.jpg", "caption": "Mid raise"},
            {"url": "/static/images/lateral-raise-3.jpg", "caption": "Top position"},
        ],
        "guide_url": None,
        "default_rest_sec": 90,
        "day": 2,
        "sets": 3,
        "reps_min": 12,
        "reps_max": 15,
        "notes": "Light weight, strict form. No swinging or shrugging.",
    },
    {
        "name": "Tricep Pushdown",
        "description": "Elbows pinned at sides throughout. Press handle down until arms straight, squeeze triceps hard. Control the return, stop when forearms parallel to floor.",
        "target_muscles": "Triceps",
        "image_url": "/static/images/tricep-pushdown.png",
        "images": [
            {"url": "/static/images/tricep-pushdown.png", "caption": "Setup position"},
            {"url": "/static/images/tricep-pushdown-2.jpg", "caption": "Mid movement"},
            {"url": "/static/images/tricep-pushdown-3.jpg", "caption": "Full extension"},
        ],
        "guide_url": None,
        "default_rest_sec": 90,
        "day": 2,
        "sets": 3,
        "reps_min": 12,
        "reps_max": 15,
        "notes": "Elbows move = cheating. Keep them locked in place.",
    },
    {
        "name": "Cable Crunch",
        "description": "Kneel facing cable, rope behind head. Curl spine down, bringing elbows toward knees. Crunch with abs, not arms. Hold contraction 1 sec. Slow return.",
        "target_muscles": "Abs",
        "image_url": "/static/images/cable-crunch.png",
        "images": [
            {"url": "/static/images/cable-crunch.png", "caption": "Starting position"},
            {"url": "/static/images/cable-crunch-2.jpg", "caption": "Crunch movement"},
            {"url": "/static/images/cable-crunch-3.jpg", "caption": "Full contraction"},
        ],
        "guide_url": None,
        "default_rest_sec": 60,
        "day": 2,
        "sets": 3,
        "reps_min": 15,
        "reps_max": 20,
        "notes": "Hip angle stays fixed. Only spine moves.",
    },
    # Day 3 - Upper Pull
    {
        "name": "Deadlift",
        "description": "Bar over mid-foot. Hip-width stance, toes out slightly. Grip just outside legs. Chest up, back flat, shoulders over bar. Push floor away, bar drags up legs. Lock hips and knees together at top.",
        "target_muscles": "Posterior chain, back, traps, core",
        "image_url": "/static/images/deadlift.png",
        "images": [
            {"url": "/static/images/deadlift.png", "caption": "Setup position"},
            {"url": "/static/images/deadlift-2.jpg", "caption": "Lift initiation"},
            {"url": "/static/images/deadlift-3.jpg", "caption": "Lockout"},
        ],
        "guide_url": None,
        "default_rest_sec": 210,
        "day": 3,
        "sets": 4,
        "reps_min": 5,
        "reps_max": None,
        "notes": "Add 5-10lbs/week. Reset each rep. No bounce.",
    },
    {
        "name": "Pull-ups",
        "description": "Overhand grip, just outside shoulders. Dead hang to start. Pull until chin over bar, driving elbows down and back. Lower with control to full extension.",
        "target_muscles": "Lats, biceps, upper back",
        "image_url": "/static/images/pull-ups.png",
        "images": [
            {"url": "/static/images/pull-ups.png", "caption": "Dead hang start"},
            {"url": "/static/images/pull-ups-2.jpg", "caption": "Pull phase"},
            {"url": "/static/images/pull-ups-3.jpg", "caption": "Top position"},
        ],
        "guide_url": None,
        "default_rest_sec": 180,
        "day": 3,
        "sets": 4,
        "reps_min": 5,
        "reps_max": 8,
        "notes": "No kipping. Add weight when hitting 8 reps all sets.",
    },
    {
        "name": "Barbell Row",
        "description": "Hinge at hips, back 45° to floor. Arms hang straight. Pull bar to lower chest/upper abs. Squeeze shoulder blades together at top. Lower with control.",
        "target_muscles": "Lats, rhomboids, traps, biceps",
        "image_url": "/static/images/barbell-row.png",
        "images": [
            {"url": "/static/images/barbell-row.png", "caption": "Bent over position"},
            {"url": "/static/images/barbell-row-2.jpg", "caption": "Row initiation"},
            {"url": "/static/images/barbell-row-3.jpg", "caption": "Top contraction"},
        ],
        "guide_url": None,
        "default_rest_sec": 120,
        "day": 3,
        "sets": 4,
        "reps_min": 8,
        "reps_max": 10,
        "notes": "Torso stays still. Only arms move.",
    },
    {
        "name": "Lat Pulldown",
        "description": "Grip 1.5x shoulder width. Lean back slightly. Pull bar to upper chest, driving elbows down toward hips. Squeeze lats at bottom. Control the return.",
        "target_muscles": "Lats, biceps",
        "image_url": "/static/images/lat-pulldown.png",
        "images": [
            {"url": "/static/images/lat-pulldown.png", "caption": "Wide grip setup"},
            {"url": "/static/images/lat-pulldown-2.jpg", "caption": "Pull phase"},
            {"url": "/static/images/lat-pulldown-3.jpg", "caption": "Full contraction"},
        ],
        "guide_url": None,
        "default_rest_sec": 120,
        "day": 3,
        "sets": 3,
        "reps_min": 10,
        "reps_max": 12,
        "notes": "Don't pull behind neck. Chest to bar.",
    },
    {
        "name": "Face Pull",
        "description": "Rope at face height. Pull toward face, separating rope ends. Elbows high, externally rotate at finish (hands end up beside ears). Squeeze rear delts.",
        "target_muscles": "Rear delts, upper back, rotator cuff",
        "image_url": "/static/images/face-pull.jpg",
        "images": [
            {"url": "/static/images/face-pull.jpg", "caption": "Starting position"},
            {"url": "/static/images/face-pull-2.jpg", "caption": "Pull to face"},
            {"url": "/static/images/face-pull-3.jpg", "caption": "External rotation finish"},
        ],
        "guide_url": None,
        "default_rest_sec": 90,
        "day": 3,
        "sets": 3,
        "reps_min": 15,
        "reps_max": 20,
        "notes": "Great for shoulder health. Light weight, high reps.",
    },
    {
        "name": "Barbell Curl",
        "description": "Shoulder-width grip, arms at sides. Curl bar up keeping elbows pinned. Squeeze biceps at top. Lower with control (3 sec). Full extension at bottom.",
        "target_muscles": "Biceps",
        "image_url": "/static/images/barbell-curl.png",
        "images": [
            {"url": "/static/images/barbell-curl.png", "caption": "Starting position"},
            {"url": "/static/images/barbell-curl-2.jpg", "caption": "Curl phase"},
            {"url": "/static/images/barbell-curl-3.jpg", "caption": "Top contraction"},
        ],
        "guide_url": None,
        "default_rest_sec": 90,
        "day": 3,
        "sets": 3,
        "reps_min": 10,
        "reps_max": 12,
        "notes": "No swinging. Ego check the weight.",
    },
    {
        "name": "Hammer Curl",
        "description": "Neutral grip (palms facing each other). Curl up keeping wrist position fixed. Upper arms stay still. Squeeze at top, slow negative.",
        "target_muscles": "Biceps, brachialis, forearms",
        "image_url": "/static/images/hammer-curl.png",
        "images": [
            {"url": "/static/images/hammer-curl.png", "caption": "Neutral grip start"},
            {"url": "/static/images/hammer-curl-2.jpg", "caption": "Curl phase"},
            {"url": "/static/images/hammer-curl-3.jpg", "caption": "Top position"},
        ],
        "guide_url": None,
        "default_rest_sec": 90,
        "day": 3,
        "sets": 3,
        "reps_min": 12,
        "reps_max": 15,
        "notes": "Builds forearm and outer bicep thickness.",
    },
    {
        "name": "Hanging Leg Raise",
        "description": "Dead hang, arms straight. Raise legs until thighs parallel to floor (or higher). Lower with control. Minimize swing.",
        "target_muscles": "Abs, hip flexors",
        "image_url": "/static/images/hanging-leg-raise.jpg",
        "images": [
            {"url": "/static/images/hanging-leg-raise.jpg", "caption": "Dead hang start"},
            {"url": "/static/images/hanging-leg-raise-2.jpg", "caption": "Leg raise"},
            {"url": "/static/images/hanging-leg-raise-3.jpg", "caption": "Top position"},
        ],
        "guide_url": None,
        "default_rest_sec": 60,
        "day": 3,
        "sets": 3,
        "reps_min": 10,
        "reps_max": 15,
        "notes": "Bend knees if straight legs too hard. Control the swing.",
    },
]


def seed_database():
    """Seed the database with exercises and program data."""
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Exercise).count() > 0:
            return

        print("Seeding database...")

        for i, ex_data in enumerate(EXERCISES):
            # Create exercise
            exercise = Exercise(
                name=ex_data["name"],
                description=ex_data["description"],
                target_muscles=ex_data["target_muscles"],
                image_url=ex_data["image_url"],
                images=ex_data.get("images", []),
                guide_url=ex_data["guide_url"],
                default_rest_sec=ex_data["default_rest_sec"],
            )
            db.add(exercise)
            db.flush()  # Get the ID

            # Create program exercise
            program_exercise = ProgramExercise(
                exercise_id=exercise.id,
                day=ex_data["day"],
                sets=ex_data["sets"],
                reps_min=ex_data["reps_min"],
                reps_max=ex_data["reps_max"],
                rest_override=None,
                notes=ex_data["notes"],
                sort_order=i,
            )
            db.add(program_exercise)

        db.commit()
        print(f"Seeded {len(EXERCISES)} exercises")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    from database import engine, Base
    Base.metadata.create_all(bind=engine)
    seed_database()
