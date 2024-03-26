import os
from shutil import copyfile
from .models import db, Course, Module, Topic, Lesson, Subject, User, Points, UserProgress, GradeEnum

VIDEO_PLACEHOLDER = "static/vendor/lesson-videos/placeholder/video.mp4"
THUMBNAIL_PLACEHOLDER = "static/vendor/lesson-videos/placeholder/thumbnail.png"
TEXTBOOK_PLACEHOLDER = "static/vendor/textbooks/placeholder/sample.pdf"

def create_file_paths(course_id, module_id, topic_id, is_video_lesson=True, videoFileName=""):
    # This creates the file path for the video/thumbnails of a given course, still need to manually add in the video/
    # thumbnails into the created directory
    script_dir = os.path.dirname(os.path.abspath(__file__))

    lesson_video_path = os.path.join(script_dir, f"static/vendor/lesson-videos/{course_id}-{module_id}-{topic_id}")
    textbook_path = os.path.join(script_dir, f"static/vendor/textbooks/{course_id}")
    
    # print("Lesson Video Path:", lesson_video_path)
    # print("Textbook Path:", textbook_path)

    os.makedirs(textbook_path, exist_ok=True)
    copyfile(os.path.join(script_dir, TEXTBOOK_PLACEHOLDER), os.path.join(textbook_path, "sample.pdf"))

    if is_video_lesson and videoFileName[:8] != "youtube:":
        os.makedirs(lesson_video_path, exist_ok=True)
        copyfile(os.path.join(script_dir, VIDEO_PLACEHOLDER), os.path.join(lesson_video_path, "video.mp4"))
        copyfile(os.path.join(script_dir, THUMBNAIL_PLACEHOLDER), os.path.join(lesson_video_path, "thumbnail.png"))

def load_database():
    most_recent_user = User.query.order_by(User.registration_date.desc()).first()
    pre_algebra_course = Course.query.filter_by(name="Pre-Algebra").first()

    # Keep track of user whose courses attribute we want to update, whether it is an existing user or a new test user
    user_to_update = most_recent_user

    # Create a test user if no user exists in the database, which will allow us to test functionality of features without having to create new user
    if not most_recent_user:
        new_user = User(
            email="johndoe@gmail.com",
            username="johndoe",
            name="John Doe",
            grade=GradeEnum.NINTH,
            age=14
        )

        password = "John@123"
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
            
        new_user_points = Points(user_id=new_user.id)

        db.session.add(new_user_points)
        db.session.commit()
            
        new_user_progress = UserProgress(
            user_id=new_user.id,
            xp=0,
            level=1,
            next_level_xp=1000,
            current_streak=0,
            longest_streak=0
        )
    
        db.session.add(new_user_progress)
        db.session.commit()

        user_to_update = new_user
        
    # Since this function will run inside of app.py everytime Flask is run, we want to ensure that the database only gets populated by this script
    # if the course does not already exist
    if not pre_algebra_course:
        course = Course(name="Pre-Algebra", subject_type=Subject.BIOLOGY)
        db.session.add(course)
        db.session.commit()

        module1 = Module(name="Factors & Multiples", course_id=course.id)
        db.session.add(module1)
        db.session.commit()

        module1_topic1 = Topic(name="Factors & Multiples", module_id=module1.id)
        db.session.add(module1_topic1)
        db.session.commit()

        module1_topic1_lesson = Lesson(
            title="Factors & Multiples",
            learning_objective="<li>Understand and Identify Factors</li><li>Apply factorization in real world contexts</li><li>Utilize factors to Simplify Fractions</li><li>Explore and apply prime factorization</li>",
            video_filename="youtube:5xe-6GPR_qQ",
            thumbnail_filename="thumbnail.png",
            textbook_name="sample.pdf",
            textbook_pages="<li>Chapter 3 - Read Pages 44 to 66</li><li>Complete Exercises 1-10</li>",
            practice_content="Spaced repetition learning here, maybe through some mini interactable question module here (for no marks, just practice)?",
            topic_id=module1_topic1.id
        )
        db.session.add(module1_topic1_lesson)
        db.session.commit()

        module1_topic2 = Topic(name="Prime & Composite Numbers", module_id=module1.id)
        db.session.add(module1_topic2)
        db.session.commit()

        module1_topic2_lesson = Lesson(
            title="Prime & Composite Numbers",
            learning_objective="<li>Understand and Identify Factors</li><li>Apply factorization in real world contexts</li><li>Utilize factors to Simplify Fractions</li><li>Explore and apply prime factorization</li>",
            lesson_content="""
                            <p>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent lobortis maximus ex, sit amet 
                                eleifend ante. Nam nec urna faucibus, sagittis leo eget, consequat tortor. Morbi sagittis congue 
                                augue, vitae ornare tortor. Proin in turpis sit amet metus pulvinar pulvinar. Sed justo purus, 
                                efficitur nec dolor in, iaculis rutrum augue. In eget vulputate tellus. Pellentesque vitae faucibus 
                                augue, sit amet rhoncus turpis. Aliquam risus sem, sollicitudin vitae posuere eu, ultricies in purus. 
                                Sed dictum viverra facilisis. Maecenas facilisis nisl leo, commodo blandit dui finibus vel.
                            </p>

                            <p>
                                Sed varius felis eget tellus pulvinar sodales. Quisque ullamcorper enim et lectus pretium, vitae
                                maximus ante scelerisque. Nulla ex elit, dignissim elementum rhoncus nec, efficitur eget sem. 
                                Sed maximus vulputate tortor, in cursus dui rutrum nec. Nulla rutrum turpis vel lorem congue, 
                                nec aliquam nunc pretium. Fusce at arcu eget neque volutpat tincidunt non vitae nibh. Cras fringilla 
                                eros quis sapien viverra, quis scelerisque augue dictum. Sed dapibus hendrerit turpis. Sed rutrum 
                                sed risus et gravida. Curabitur sodales id dolor vel interdum.
                            </p>

                            <p>
                                Vestibulum scelerisque mattis consequat. In eget urna tellus. Morbi velit nunc, hendrerit vel lorem 
                                quis, tincidunt gravida neque. Pellentesque egestas enim nec lacus tempor, sed bibendum felis lobortis. 
                                Aenean vestibulum vel leo in semper. Integer gravida luctus ornare. Nullam magna tellus, sagittis sed 
                                dapibus sed, congue quis turpis. Quisque id enim in arcu faucibus scelerisque. Suspendisse odio massa, 
                                imperdiet et urna a, aliquam aliquet neque. Phasellus suscipit ex quis libero finibus, porta efficitur 
                                augue gravida. Etiam ac pretium urna. Pellentesque posuere hendrerit turpis sed suscipit. Suspendisse 
                                ultrices, augue in tristique ultricies, ligula diam facilisis justo, eget consequat mauris ipsum sit 
                                amet nunc. Etiam non nisl justo. Donec dignissim ullamcorper maximus. Fusce rhoncus volutpat augue.  
                            </p>
                            """,
            textbook_name="sample.pdf",
            textbook_pages="<li>Chapter 3 - Read Pages 44 to 66</li><li>Complete Exercises 1-10</li>",
            practice_content="Spaced repetition learning here, maybe through some mini interactable question module here (for no marks, just practice)?",
            topic_id=module1_topic2.id
        )
        db.session.add(module1_topic2_lesson)
        db.session.commit()

        module1_topic3 = Topic(name="Prime Factorization", module_id=module1.id)
        db.session.add(module1_topic3)
        db.session.commit()

        module1_topic3_lesson = Lesson(
            title="Factors & Multiples",
            learning_objective="<li>Understand and Identify Factors</li><li>Apply factorization in real world contexts</li><li>Utilize factors to Simplify Fractions</li><li>Explore and apply prime factorization</li>",
            video_filename="youtube:ZKKDTfHcsG0",
            thumbnail_filename="thumbnail.png",
            textbook_name="sample.pdf",
            textbook_pages="<li>Chapter 3 - Read Pages 44 to 66</li><li>Complete Exercises 1-10</li>",
            practice_content="Spaced repetition learning here, maybe through some mini interactable question module here (for no marks, just practice)?",
            topic_id=module1_topic3.id
        )
        db.session.add(module1_topic3_lesson)
        db.session.commit()

        create_file_paths(course.id, module1.id, module1_topic1.id, videoFileName=module1_topic1_lesson.video_filename)
        create_file_paths(course.id, module1.id, module1_topic2.id, is_video_lesson=False)
        create_file_paths(course.id, module1.id, module1_topic3.id, videoFileName=module1_topic3_lesson.video_filename)

        module2 = Module(name="Patterns", course_id=course.id)
        db.session.add(module2)
        db.session.commit()

        module2_topic1 = Topic(name="Pattern Rules", module_id=module2.id)
        db.session.add(module2_topic1)
        db.session.commit()

        module2_topic1_lesson = Lesson(
            title="Pattern Rules",
            learning_objective="<li>Understand and Identify Factors</li><li>Apply factorization in real world contexts</li><li>Utilize factors to Simplify Fractions</li><li>Explore and apply prime factorization</li>",
            video_filename="video.mp4",
            thumbnail_filename="thumbnail.png",
            textbook_name="sample.pdf",
            textbook_pages="<li>Chapter 3 - Read Pages 44 to 66</li><li>Complete Exercises 1-10</li>",
            practice_content="Spaced repetition learning here, maybe through some mini interactable question module here (for no marks, just practice)?",
            topic_id=module2_topic1.id
        )
        db.session.add(module2_topic1_lesson)
        db.session.commit()

        create_file_paths(course.id, module2.id, module2_topic1.id, videoFileName=module2_topic1_lesson.video_filename)

        # View Course ID in console for testing purposes, can also use flask shell command created in run_app.py
        # print(f"Course ID: {course.id}")
        user_to_update.courses.append(course)
        db.session.commit()

        print("Database populated.")
    else:
        if pre_algebra_course not in user_to_update.courses:
            user_to_update.courses.append(pre_algebra_course)
            db.session.commit()
        print("The Pre-Algebra course already exists in the database.")

if __name__ == "__main__":
    load_database()


