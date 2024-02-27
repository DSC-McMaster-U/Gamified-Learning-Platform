import os
from .models import db, Course, Module, Topic, Lesson, Subject, User

def create_file_paths(course_id, module_id, topic_id):
    # This creates the file path for the video/thumbnails of a given course, still need to manually add in the video/
    # thumbnails into the created directory

    script_dir = os.path.dirname(os.path.abspath(__file__))

    lesson_video_path = os.path.join(script_dir, f"static/vendor/lesson-videos/{course_id}-{module_id}-{topic_id}")
    textbook_path = os.path.join(script_dir, f"static/vendor/textbooks/{course_id}")
    
    print("Lesson Video Path:", lesson_video_path)
    print("Textbook Path:", textbook_path)

    os.makedirs(lesson_video_path, exist_ok=True)
    os.makedirs(textbook_path, exist_ok=True)

def load_database():
    most_recent_user = User.query.order_by(User.registration_date.desc()).first()
    pre_algebra_course = Course.query.filter_by(name="Pre-Algebra").first()

    # Since this function will run inside of app.py everytime Flask is run, we want to ensure that the database only gets populated by this script
    # if the course does not already exist

    if not pre_algebra_course:
        course = Course(name="Pre-Algebra", subject_type=Subject.BIOLOGY)
        db.session.add(course)
        db.session.commit()

        print(f"Course ID: {course.id}")
        most_recent_user.courses.append(pre_algebra_course)
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
            video_filename="video.mp4",
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
            video_filename="video.mp4",
            thumbnail_filename="thumbnail.png",
            textbook_name="sample.pdf",
            textbook_pages="<li>Chapter 3 - Read Pages 44 to 66</li><li>Complete Exercises 1-10</li>",
            practice_content="Spaced repetition learning here, maybe through some mini interactable question module here (for no marks, just practice)?",
            topic_id=module1_topic3.id
        )
        db.session.add(module1_topic3_lesson)
        db.session.commit()

        create_file_paths(course.id, module1.id, module1_topic1.id)

        module2 = Module(name="Patterns", course_id=course.id)
        db.session.add(module2)
        db.session.commit()

        module3 = Module(name="Ratios and Rates", course_id=course.id)
        db.session.add(module3)
        db.session.commit()

        module4 = Module(name="Percentages", course_id=course.id)
        db.session.add(module4)
        db.session.commit()

        module5 = Module(name="Exponents Intro & Order of Operations", course_id=course.id)
        db.session.add(module5)
        db.session.commit()

        module6 = Module(name="Variables & Expressions", course_id=course.id)
        db.session.add(module6)
        db.session.commit()

        module7 = Module(name="Equations & Inequalities", course_id=course.id)
        db.session.add(module7)
        db.session.commit()

        module8 = Module(name="Proportional Relationships", course_id=course.id)
        db.session.add(module8)
        db.session.commit()

        print("Database populated.")
    else:
        if pre_algebra_course not in most_recent_user.courses:
            most_recent_user.courses.append(pre_algebra_course)
            db.session.commit()
        print("The Pre-Algebra course already exists in the database.")

if __name__ == "__main__":
    load_database()


