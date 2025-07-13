from django.core.management.base import BaseCommand
from marketplace.models import Subject, Account, UserProfile, Note
from django.contrib.auth.hashers import make_password
import random

class Command(BaseCommand):
    help = 'Populate database with sample data for NotesHub'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create subjects
        subjects_data = [
            {'name': 'Computer Science', 'code': 'CS101', 'description': 'Introduction to Computer Science'},
            {'name': 'Data Structures', 'code': 'CS201', 'description': 'Fundamental data structures and algorithms'},
            {'name': 'Database Systems', 'code': 'CS301', 'description': 'Database design and management'},
            {'name': 'Web Development', 'code': 'CS401', 'description': 'Modern web development technologies'},
            {'name': 'Machine Learning', 'code': 'CS501', 'description': 'Introduction to machine learning'},
            {'name': 'Software Engineering', 'code': 'CS601', 'description': 'Software development methodologies'},
            {'name': 'Computer Networks', 'code': 'CS701', 'description': 'Network protocols and architecture'},
            {'name': 'Operating Systems', 'code': 'CS801', 'description': 'OS concepts and implementation'},
            {'name': 'Mathematics', 'code': 'MATH101', 'description': 'Calculus and linear algebra'},
            {'name': 'Physics', 'code': 'PHY101', 'description': 'Classical mechanics and thermodynamics'},
            {'name': 'Chemistry', 'code': 'CHEM101', 'description': 'General chemistry principles'},
            {'name': 'Biology', 'code': 'BIO101', 'description': 'Cell biology and genetics'},
            {'name': 'Economics', 'code': 'ECO101', 'description': 'Micro and macroeconomics'},
            {'name': 'Business Management', 'code': 'BUS101', 'description': 'Business administration fundamentals'},
            {'name': 'Marketing', 'code': 'MKT101', 'description': 'Marketing strategies and consumer behavior'},
        ]
        
        subjects = []
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                code=subject_data['code'],
                defaults=subject_data
            )
            subjects.append(subject)
            if created:
                self.stdout.write(f'Created subject: {subject.name}')
        
        # Create sample users
        users_data = [
            {'phone': '9876543210', 'name': 'Rahul Sharma', 'student_id': 'CS2024001'},
            {'phone': '9876543211', 'name': 'Priya Patel', 'student_id': 'CS2024002'},
            {'phone': '9876543212', 'name': 'Amit Kumar', 'student_id': 'CS2024003'},
            {'phone': '9876543213', 'name': 'Neha Singh', 'student_id': 'CS2024004'},
            {'phone': '9876543214', 'name': 'Vikram Malhotra', 'student_id': 'CS2024005'},
        ]
        
        users = []
        for user_data in users_data:
            user, created = Account.objects.get_or_create(
                phone=user_data['phone'],
                defaults={
                    'name': user_data['name'],
                    'password': make_password('password123')
                }
            )
            users.append(user)
            if created:
                self.stdout.write(f'Created user: {user.name}')
        
        # Create user profiles
        colleges = ['IIT Delhi', 'IIT Bombay', 'IIT Madras', 'IIT Kanpur', 'BITS Pilani']
        departments = ['Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil']
        
        for i, user in enumerate(users):
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'student_id': users_data[i]['student_id'],
                    'college': colleges[i % len(colleges)],
                    'department': departments[i % len(departments)],
                    'year': random.randint(1, 4),
                    'phone': user.phone,
                    'bio': f'I am a student at {colleges[i % len(colleges)]} studying {departments[i % len(departments)]}.'
                }
            )
            if created:
                self.stdout.write(f'Created profile for: {user.name}')
        
        # Create sample notes
        note_titles = [
            'Complete Data Structures Notes',
            'Database Systems Study Guide',
            'Web Development Fundamentals',
            'Machine Learning Algorithms',
            'Software Engineering Best Practices',
            'Computer Networks Protocols',
            'Operating Systems Concepts',
            'Calculus Complete Notes',
            'Physics Lab Manual',
            'Chemistry Practical Guide',
            'Biology Cell Structure Notes',
            'Economics Market Analysis',
            'Business Management Strategies',
            'Marketing Case Studies',
            'Advanced Programming Concepts'
        ]
        
        descriptions = [
            'Comprehensive notes covering all data structures including arrays, linked lists, trees, graphs, and algorithms.',
            'Complete study material for database systems including SQL, normalization, and database design.',
            'Fundamental concepts of web development including HTML, CSS, JavaScript, and modern frameworks.',
            'Detailed notes on machine learning algorithms, neural networks, and deep learning concepts.',
            'Best practices in software engineering including agile methodologies and design patterns.',
            'Complete guide to computer network protocols, TCP/IP, and network architecture.',
            'Operating system concepts including process management, memory management, and file systems.',
            'Comprehensive calculus notes covering differentiation, integration, and applications.',
            'Complete physics lab manual with experiments and theoretical background.',
            'Chemistry practical guide with laboratory procedures and safety protocols.',
            'Detailed notes on cell biology, genetics, and molecular biology.',
            'Market analysis and economic theories with real-world examples.',
            'Business management strategies and organizational behavior concepts.',
            'Marketing case studies and consumer behavior analysis.',
            'Advanced programming concepts including design patterns and software architecture.'
        ]
        
        for i in range(20):
            user = random.choice(users)
            subject = random.choice(subjects)
            title = random.choice(note_titles)
            description = random.choice(descriptions)
            
            note = Note.objects.create(
                seller=user,
                subject=subject,
                title=title,
                description=description,
                price=random.choice([0, 50, 100, 150, 200, 250, 300]),
                semester=random.randint(1, 8),
                year=random.randint(2020, 2024),
                tags=f'{subject.name}, {user.profile.department}, Semester {random.randint(1, 8)}',
                contact_info=f'WhatsApp: {user.phone}',
                is_free=random.choice([True, False]),
                views=random.randint(10, 500),
                downloads=random.randint(0, 50),
                is_approved=True
            )
            self.stdout.write(f'Created note: {note.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample data!')
        )
        self.stdout.write(f'Created {len(subjects)} subjects')
        self.stdout.write(f'Created {len(users)} users')
        self.stdout.write('Created 20 sample notes') 