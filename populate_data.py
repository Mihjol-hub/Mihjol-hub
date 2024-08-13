#populate_data.py
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from contextlib import contextmanager
from passlib.context import CryptContext
import logging
import hashlib
import random
from datetime import timedelta, datetime
from faker import Faker
from app.models import db, User, Keyword, Post, Group, GroupMember, user_keyword, post_keyword, Reaction, Comment, Friendship, Notification
from sqlalchemy.sql import func
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError



# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


fake = Faker()

# Create an instance of CryptContext for password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuration
CONFIG = {
    'num_users': 100,
    'num_groups': 30,
    'num_posts': 195,
    'num_reactions': 200,
    'num_comments': 150,
    'num_friendships': 100,
    'num_notifications': 200,
    'num_keywords': 50,
    'num_members_per_group': 100,
}


# Create a database session
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Insert fictitious data into the users table
def create_users(num_users: int) -> List[User]:
    user_data = [
        {
            "username": "john",
            "email": "john@unige.com",
            "password": "user0",
            "workrole": "Developer Full-Stack",
            "entreprise": "Tech Corp",
            "biography": "I am a FullStack Developer with a passion for mobile telecommunication and IoT",
            "birthday": '1990-01-01'
        },
        {
            "username": "jane",
            "email": "jane@ecui.com",
            "password": "user1",
            "workrole": "Designer",
            "entreprise": "Creative Inc",
            "biography": "Jane is a creative designer UIX",
            "birthday": '1988-04-02'
        },
        {
            "username": "santiago",
            "email": "santiago@cui.com",
            "password": "password0",
            "workrole": "Software Engineer",
            "entreprise": "Entreprise1",
            "biography": "I am a software engineer with a passion for creating innovative solutions.",
            "birthday": '1999-07-05'
        },
        {
            "username":"diego",
            "email":"diego@university.com",
            "password":"password1",
            "workrole":"Data Scientist",
            "entreprise":"CUI",
            "biography":"I am a data scientist with a strong background in machine learning.",
            "birthday":'1995-11-03'
        },
        {
            "username":"carlos",
            "email":"carlos@tech.com",
            "password":"password2",
            "workrole":"Full Stack Developer",
            "entreprise":"Entreprise3",
            "biography":"I am a full stack developer with experience in both front-end and back-end technologies.",
            "birthday": '1992-09-07'
        },
        {
            "username":"maria",
            "email":"maria@datasci.com",
            "password":"password3",
            "workrole":"Data Analyst",
            "entreprise":"unige",
            "biography":"I am a data analyst with a knack for interpreting complex data and turning it into easy-to-understand reports.",
            "birthday": '1997-02-12'
        },
        {
            "username":"laura",
            "email":"laura@cybersec.com",
            "password":"password4",
            "workrole":"Cyber Security Analyst",
            "entreprise":"Security Corp",
            "biography":"I am a cyber security analyst specializing in network security and threat detection.",
            "birthday": '1996-05-19'
        },
        {
            "username":"fernando",
            "email":"fernando@blockchain.com",
            "password":"password5",
            "workrole":"Blockchain Developer",
            "entreprise":"Blockchain Innovations",
            "biography":"I am a blockchain developer passionate about creating decentralized applications.",
            "birthday":'1993-08-30'
        },
        {
            "username":"mike",
            "email":"miki@webdev.com",
            "password":"password6",
            "workrole":"Web Developer",
            "entreprise":"Web Solutions",
            "biography":"I am a web developer with expertise in HTML, CSS, and JavaScript.",
            "birthday":'1994-12-15'
        },
        {
            "username":"cloe",
            "email":"cloe@cloudcomp.com",
            "password":"password7",
            "workrole":"Cloud Computing Engineer",
            "entreprise":"Cloud Services Inc",
            "biography":"I am a cloud computing engineer focused on designing scalable and reliable cloud infrastructure.",
            "birthday":'1995-06-20'
        },
        {
            "username":"luisa",
            "email":"luisa@mobiledev.com",
            "password": "password8",
            "workrole":"Mobile App Developer",
            "entreprise":"Mobile Solutions Ltd",
            "biography":"I am a mobile app developer passionate about creating innovative mobile applications.",
            "birthday":'1992-11-10'
        },
        {
            "username":"soe",
            "email":"so@ai.com",
            "password":"password9",
            "workrole":"AI Researcher",
            "entreprise":"AI Technologies",
            "biography":"I am an AI researcher dedicated to advancing the field of artificial intelligence through innovative research.",
            "birthday":'1997-03-25'
        },
        {
            "username":"octavio",
            "email":"octavio@web3.com",
            "password":"password10",
            "workrole":"Web3 Developer",
            "entreprise":"Web3 Solutions",
            "biography":"I am a web3 developer building innovative applications on decentralized networks.",
            "birthday":'1996-09-18'
        },
        {
            "username":"terry",
            "email":"terry@blockchaindev.com",
            "password":"password11",
            "workrole":"Blockchain Developer",
            "entreprise":"Blockchain Inc.",
            "biography":"I am a blockchain developer specializing in smart contract development and DeFi applications.",
            "birthday":'1993-07-12'
        },
        {
            "username":"miki",
            "email":"mika@sql.com",
            "password":"password12",
            "workrole":"SQL Database Administrator",
            "entreprise":"Data Management",
            "biography":"I am a database administrator with expertise in managing and optimizing SQL databases.",
            "birthday":'1994-02-20'
        },
        {
            "username":"ivon",
            "email":"ivon@mongodb.com",
            "password":"password13",
            "workrole":"NoSQL Database Developer",
            "entreprise":"CloudDB Inc.",
            "biography":"I am a NoSQL database developer experienced in working with MongoDB and other document databases.",
            "birthday":'1995-11-05'
        },
        {
            "username":"valentina",
            "email":"valentina@datascience.com",
            "password":"password14",
            "workrole":"Data Scientist",
            "entreprise":"Research Labs",
            "biography":"I am a data scientist with a strong background in machine learning and natural language processing.",
            "birthday":'1992-08-19'
        },
        {
            "username":"matias",
            "email":"matias@mlengineer.com",
            "password":"password15",
            "workrole":"Machine Learning Engineer",
            "entreprise":"AI for Good",
            "biography":"I am a machine learning engineer developing AI solutions for social impact.",
            "birthday":'1993-05-30'
        },
        {
            "username":"camila",
            "email":"camila@devops.com",
            "password":"password16",
            "workrole":"DevOps Engineer",
            "entreprise":"DevOps Solutions",
            "biography":"I am a DevOps engineer with expertise in automating infrastructure and software delivery pipelines.",
            "birthday":'1994-12-07', 
        },
        {
            "username":"nicolas",
            "email":"nicolas@cloud.com",
            "password":"password17",
            "workrole":"Cloud Architect",
            "entreprise":"Cloud Technologies",
            "biography":"I am a cloud architect designing and implementing scalable cloud infrastructure solutions.",
            "birthday":'1995-03-15'
        },
        {
            "username":"gabriela",
            "email":"gabriela@softwaredev.com",
            "password":"password18",
            "workrole":"Software Developer",
            "entreprise":"Tech Solutions",
            "biography":"I am a software developer with experience in developing web applications and APIs.",
            "birthday":'1992-10-22'
        },
        {
            "username":"gaete",
            "email":"gaete@it.com",
            "password":"password19",
            "workrole":"IT Support Specialist",
            "entreprise":"Global IT Support",
            "biography":"I am an IT support specialist providing technical assistance to users.",
            "birthday":'1993-09-08',
        },
        {
            "username":"erika",
            "email":"erika@frontend.com",
            "password":"password20",
            "workrole":"Frontend Developer",
            "entreprise":"Frontend Innovations",
            "biography":"I am a frontend developer passionate about creating interactive and user-friendly interfaces.",
            "birthday":'1994-07-19'
        },
        {
            "username":"candy",
            "email":"candy@backend.com",
            "password":"password21",
            "workrole":"Backend Developer",
            "entreprise":"Backend Solutions",
            "biography":"I am a backend developer focused on building robust and scalable server-side applications.",
            "birthday":'1995-06-05'
        },
        {
            "username":"heidi",
            "email":"heidi@unige.com",
            "password":"password22",
            "workrole":"UniGE Developer",
            "entreprise":"UniGE Solutions",
            "biography":"I am a front-end developer with a passion for building beautiful and responsive user interfaces using React.",
            "birthday": '1992-12-03'
        },
        {
            "username":"esmeralda",
            "email":"esmeralda@cui.com",
            "password":"password23",
            "workrole":"CUI Developer",
            "entreprise":"CUI Solutions",
            "biography":"I am a full-stack developer with expertise in both front-end (HTML, CSS, JavaScript) and back-end development using Django.",
            "birthday":'1993-11-17'
        },
        {
            "username":"cruz",
            "email":"cruz@university.com",
            "password":"password24",
            "workrole":"Webify Developer",
            "entreprise":"Webify Inc.",
            "biography":"I am a Gamer programmer with a passion in Unity Unreal in mobile phone.",
            "birthday":'1994-08-30'
        },
        {
            "username":"martha",
            "email":"martha@gmai.com",
            "password":"password25",
            "workrole":"UI/UX Designer",
            "entreprise":"DesignCraft",
            "biography":"I'm a UI/UX designer with a focus on creating user-centered and aesthetically pleasing web applications.",
            "birthday":'1995-05-12'
        },
        {
            "username":"mariaeugenia",
            "email":"mariaeugenia@gmail.com",
            "password":"password26",
            "workrole":"Web Scraper Developer",
            "entreprise":"Data Acquisition Ltd",
            "biography":"I am a web scraper developer skilled in extracting and parsing data from websites.",
            "birthday":'1992-09-15'
        },
        {
            "username":"miguel",
            "email":"miguel@gmail.com",
            "password":"password27",
            "workrole":"IOS Developer (Swift)",
            "entreprise":"Banana Republic Inc.",
            "biography":"I'm an iOS developer with a strong grasp of Swift programming language for building native iOS applications. I like Kotlin, Java and C#.",
            "birthday":'1993-06-20'
        },
        {
            "username":"topacio",
            "email":"topaciocui.com",
            "password":"password28",
            "workrole":"Android Developer (Kotlin)",
            "entreprise":"Geneve Inc.",
            "biography":"I'm an Android developer with expertise in building native Android applications using Kotlin, Go and Java.",                 
            "birthday":'2000-07-07'
        },
        {
            "username":"opalo",
            "email":"opalo@unimail.com",
            "password":"password29",
            "workrole":"Flutter Mobile Developer",
            "entreprise":"Gross-Platform Solutions",
            "biography":"I'm a mobile developer specializing in building cross-platform applications with Flutter.",
            "birthday":'1985-08-01'
        },
        {
            "username":"rosa",
            "email":"rosa@cui.com",
            "password":"password30",
            "workrole":"Mobile QA Tester",
            "entreprise":"App Quality Inc.",
            "biography":"I am a mobile QA tester ensuring the quality and functionality of mobile applications.",
            "birthday":'1997-01-01'
        },
        {
            "username":"guadalupe",
            "email":"guadalupe@unige.com",
            "password":"password31",
            "workrole":"Backend Developer (Node.js)",
            "entreprise":"Node.js Solutions",
            "biography":"I am a backend developer with strong focus on building scalable and efficient APIs using Node.js.",
            "birthday":'1999-03-04'
        },
        {
            "username":"jean",
            "email":"jean@unige.com",
            "password":"password32",
            "workrole":"Frontend Developer (React)",
            "entreprise":"React Solutions",
            "biography":"I am a frontend developer with expertise in building user-friendly and responsive web applications using React.",
            "birthday":'1998-05-02'
        },
        {
            "username":"sebastian",
            "email":"sebastian@unige.com",
            "password":"password33",
            "workrole":"Backend Developer (Java)",
            "entreprise":"Enterprise Java Solutions",
            "biography":"I am a backend developer with experience in building enterprise applications using Java.",
            "birthday":'1996-07-08'
        },
        {
            "username":"mariano",
            "email":"mariano@unige.com",
            "password":"password34",
            "workrole":"DevOps Engineer",
            "entreprise":"DevSecOps Inc.",
            "biography":"I am a DevOps engineer with expertise in automating infrastructure and software delivery pipelines.",
            "birthday": '1997-09-01'
        },
        {
            "username":"enrique",
            "email":"enrique@unimail.com",
            "password":"password35",
            "workrole":"API Security Engineer",
            "entreprise":"Security Systems Inc.",
            "biography":"I am a security engineer specializing in protecting APIs from security vulnerabilities.",
            "birthday": '1995-11-05'
        },
        {
            "username":"tomy",
            "email":"tom@unimail.com",
            "password":"password36",
            "workrole":"Data Scientist",
            "entreprise":"Data Analysis Inc.",
            "biography":"I'm a data scientist with expertise in machine learning and statistical analysis.",
            "birthday":'1996-12-06'
        },
        {
            "username":"landaeta",
            "email":"landa@unimail.com",
            "password":"password38",
            "workrole":"Full Stack Developer",
            "entreprise":"Web Development Inc.",
            "biography":"I am a full stack developer with experience in both front-end and back-end technologies.",
            "birthday":'1997-08-07'
        },
        {
            "username":"natalia",
            "email":"natalia@cui.com",
            "password":"password37",
            "workrole":"UX Designer",
            "entreprise":"Design Solutions",
            "biography":"I am a UX designer creating intuitive and user-friendly designs for web and mobile applications.",
            "birthday":'1996-02-02'
        },
        {
            "username":"george",
            "email":"maria@unimail.com",
            "password":"password39",
            "workrole":"Data Scientist",
            "entreprise":"Data Analytics Co.",
            "biography":"I am a data scientist with expertise in machine learning and data visualization.",
            "birthday":'1997-03-03'
        },
        {
            "username":"dakota",
            "email":"lucas@unimail.com",
            "password":"password40",
            "workrole":"Mobile App Developer",
            "entreprise":"App Creators LLC",
            "biography":"I specialize in developing innovative mobile applications for iOS and Android.",
            "birthday":'1996-04-09'
        },
        {
            "username":"belgica",
            "email":"sofia@unimail.com",
            "password":"password41",
            "workrole":"UI/UX Designer",
            "entreprise":"Creative Designs",
            "biography":"I am a UI/UX designer passionate about creating user-friendly interfaces and experiences.",
            "birthday":'1997-05-10'
        },
        {
            "username":"francia",
            "email":"francia@unimail.com",
            "password":"password42",
            "workrole":"DevOps Engineer",
            "entreprise":"Cloud Solutions Inc.",
            "biography":"I am a DevOps engineer focused on continuous integration and deployment strategies.",
            "birthday": '1996-06-11'
        },
        {
            "username":"noelia",
            "email":"noe@unimail.com",
            "password":"password43",
            "workrole":"Project Manager",
            "entreprise":"Tech Management LLC",
            "biography":"I am a project manager with experience in leading software development projects.",
            "birthday":'1997-07-12'
        },
        {
            "username":"maldonado",
            "email":"fernando@unimail.com",
            "password":"password44",
            "workrole":"Cybersecurity Specialist",
            "entreprise":"Secure Networks",
            "biography":"I am a cybersecurity specialist with a focus on network security and threat analysis.",
            "birthday":'1996-08-13'
        },
        {
            "username":"katy",
            "email":"katy@unimail.com",
            "password":"password45",
            "workrole":"Database Administrator",
            "entreprise":"DB Solutions",
            "biography":"I manage and maintain databases, ensuring data integrity and performance.",
            "birthday":'1997-09-14'
        },
        {
            "username":"dosantos",
            "email":"miguel@unimail.com",
            "password":"password46",
            "workrole":"System Administrator",
            "entreprise":"IT Services Co.",
            "biography":"I am a system administrator with expertise in managing IT infrastructure.",
            "birthday":'1996-10-15'
        },
        {
            "username":"isis",
            "email":"valeria@unimail.com",
            "password":"password47",
            "workrole":"Software Tester",
            "entreprise":"Quality Assurance Ltd.",
            "biography":"I am a software tester ensuring the quality and functionality of software products.",
            "birthday":'1997-11-16', 
        },
        {
            "username":"cleopatra",
            "email":"cleopatra@unimail.com",
            "password":"password48",
            "workrole":"Network Engineer",
            "entreprise":"Network Solutions",
            "biography":"I design and implement network solutions to enhance connectivity and performance.",
            "birthday":'1996-12-17'
        },
        {
            "username":"cesar",
            "email":"cesar@unimail.com",
            "password":"password49",
            "workrole":"AI Researcher",
            "entreprise":"AI Innovations",
            "biography":"I am an AI researcher focused on developing advanced machine learning algorithms.",
            "birthday":'1997-01-18'
        },
        {
            "username":"meyer",
            "email":"diego@unimail.com",
            "password": "password50",
            "workrole":"Blockchain Developer",
            "entreprise":"Crypto Solutions",
            "biography":"I develop decentralized applications and smart contracts on blockchain platforms.",
            "birthday": '1996-02-11'
        },
        {
            "username":"vives",
            "email":"vives@unimail.com",
            "password":"password51",
            "workrole":"Game Developer",
            "entreprise":"Gaming World",
            "biography":"I am a game developer with experience in creating engaging and immersive games.",
            "birthday":'1997-03-20'
        },
        {
            "username":"patrick",
            "email":"patrick@unimail.com",
            "password":"password52",
            "workrole":"Cloud Architect",
            "entreprise":"Cloud Masters",
            "biography":"I design and manage scalable cloud infrastructure solutions.",
            "birthday":'1996-04-21'
        },
        {
            "username":"estefan",
            "email":"estefan@unimail.com",
            "password":"password53",
            "workrole":"Technical Writer",
            "entreprise":"TechDocs Inc.",
            "biography":"I create technical documentation and guides for software products.",
            "birthday": '1997-05-22'
        },
        {
            "username":"barbara",
            "email":"barbie@unimail.com",
            "password":"password54",
            "workrole":"Robotics Engineer",
            "entreprise":"Automation Robotics",
            "biography":"I design and develop robotic systems for various applications.",
            "birthday":'1996-06-23'
        },
        {
            "username":"mickimause",
            "email":"mikey@unimail.com",
            "password":"password55",
            "workrole":"IT Support Specialist",
            "entreprise":"Tech Support Ltd.",
            "biography":"I provide technical support and troubleshooting for IT systems.",
            "birthday": '1997-07-24'
        },
        {
            "username":"tuti",
            "email":"eltuti@unimail.com",
            "password":"password56",
            "workrole":"SEO Specialist",
            "entreprise":"Digital Marketing Co.",
            "biography":"I optimize websites to improve search engine rankings and visibility.",
            "birthday":'1996-08-25'
        },
        {
            "username":"chinchilla",
            "email":"chinchimelengue@unimail.com",
            "password":"password57",
            "workrole":"Content Strategist",
            "entreprise":"Content Creators",
            "biography":"I develop and execute content strategies to enhance brand presence.",
            "birthday":'1997-09-26'
        },
        {
            "username":"felix",
            "email":"felix@unimail.com",
            "password":"password58",
            "workrole":"Embedded Systems Engineer",
            "entreprise":"Embedded Solutions",
            "biography":"I design and program embedded systems for various electronic devices.",
            "birthday":'1996-10-27'
        },
        {
            "username":"mendelson",
            "email":"mendel@unimail.com",
            "password":"password59",
            "workrole":"Data Analyst",
            "entreprise":"Data Insights Ltd.",
            "biography":"I analyze data to extract valuable insights and drive business decisions.",
            "birthday":'1997-11-28'
        },
        {
            "username":"salvatore",
            "email":"salva@cui.com",
            "password":"password60",
            "workrole":"Machine Learning Engineer",
            "entreprise":"AI Solutions Co.",
            "biography":"I develop machine learning models to solve complex problems and improve processes.",
            "birthday":'1996-12-29'
        },
        {
            "username":"sandra",
            "email":"carolina@unige.com",
            "password":"password61",
            "workrole":"Product Manager",
            "entreprise":"Product Innovations",
            "biography":"I oversee the development and launch of new products, ensuring they meet market needs.",
            "birthday":'1997-01-30'
        },
        {
            "username":"toto",
            "email":"toti@scence.com",
            "password":"password62",
            "workrole":"Software Engineer",
            "entreprise":"Tech Solutions Corp.",
            "biography":"I develop software solutions to address specific business needs and challenges.",
            "birthday":'1996-09-09'
        },
        {
            "username":"guillermo",
            "email":"claudia@rectora.com",
            "password":"password63",
            "workrole":"UI Designer",
            "entreprise":"Design Innovations",
            "biography":"I design visually appealing and intuitive user interfaces for digital products.",
            "birthday":'1997-03-01'
        },
        {   
            "username":"timoteo",
            "email":"timoteo@unimail.com",
            "password":"password64",
            "workrole":"Business Analyst",
            "entreprise":"Business Insights Ltd.",
            "biography":"I analyze business processes and data to provide insights and recommendations for improvement.",
            "birthday":'1996-04-02'
        },
        {
            "username":"nadia",
            "email":"nadia@cui.com",
            "password":"password65",
            "workrole":"UX Researcher",
            "entreprise":"User Research Lab",
            "biography":"I conduct user research to understand behavior and inform design decisions.",
            "birthday":'1997-05-03'
        },
        {
            "username":"villa",
            "email":"ville@rectora.com",
            "password":"password66",
            "workrole":"System Analyst",
            "entreprise":"System Solutions Inc.",
            "biography":"I analyze and design information systems to meet organizational needs.",
            "birthday":'1996-06-04'
        },
        {
            "username":"yelitza",
            "email":"yeli@scence.com",
            "password":"password67",
            "workrole":"Technical Support Engineer",
            "entreprise":"Tech Solutions Support",
            "biography":"I provide technical assistance and troubleshooting for software and hardware issues.",
            "birthday":'1997-07-05'
        },
        {
            "username":"leonard",
            "email":"leo@unimail.com",
            "password":"password68",
            "workrole":"Network Administrator",
            "entreprise":"Network Management Services",
            "biography":"I manage and maintain computer networks to ensure smooth operation and security.",
            "birthday":'1996-08-06'
        }
    ]
    users = []
    for i in range(min(num_users, len(user_data))):
        data = user_data[i]
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            print(f"User with email {data['email']} already exists. Using existing user.")
            users.append(existing_user)
        else:
            user = User(
                username=data['username'],
                email=data['email'],
                password=pwd_context.hash(data['password']),
                workrole=data['workrole'],
                entreprise=data['entreprise'],
                biography=data['biography'],
                birthday=datetime.strptime(data['birthday'], '%Y-%m-%d'),
                role="user"
            )
            db.session.add(user)
            users.append(user)

    try:
        db.session.commit()
        print(f"Successfully processed {len(users)} users.")
        count = User.query.count()
        print(f"Total users in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while processing users: {str(e)}")
        raise

    return users

    

def create_groups(num_groups: int) -> List[Group]:
    group_data = [
        {
            "name": "Tech Enthusiasts",
            "description": "A group for discussing the latest in technology"
        },
        {
            "name": "Web Developers",
            "description": "For web developers to share ideas and best practices"
        },
        {
            "name": "Data Science Club",
            "description": "Exploring the world of data science and machine learning"
        },
        {
            "name": "Git", 
            "description": "Group focused on Git version control."
        },
        {
            "name": "Linux",
            "description": "Group focused on Linux and open source"
        },
        {
            "name": "Docker",
            "description": "Group focused on containerization with Docker."
        },
        {
            "name": "Blockchain", 
            "description": "Group focused on Blockchain technology."
        },
        {
            "name": "Internet of Things",
            "description": "Group focused on IoT devices and applications."
        },
        {
            "name": "Front-end Development",
            "description": "Group focused on front-end development technologies and frameworks."
        },
        {
            "name": "Back-end Development",
            "description": "Group focused on back-end development technologies and frameworks."
        },
        {
            "name": "Cybersecurity",
            "description": "Group focused on cybersecurity practices and technologies."
        },
        {
            "name": "AI & Machine Learning",
            "description": "Group focused on artificial intelligence and machine learning."
        },
        {
            "name": "DevOps",
            "description": "Group focused on DevOps practices and tools."
        }
    ]

    groups = []
    for i in range(min(num_groups, len(group_data))):
        data = group_data[i]   
        existing_group = Group.query.filter_by(name=data['name']).first()
        if existing_group:
            print(f"Group '{data['name']}' already exists. Using existing group.")
            groups.append(existing_group)
        else:
            group = Group(
                name=data['name'],
                description=data['description']
            )
            db.session.add(group)
            groups.append(group)

    try:
        db.session.commit()
        print(f"Successfully processed {len(groups)} groups.")
        count = Group.query.count()
        print(f"Total groups in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while processing groups: {str(e)}")
        raise

    return groups
    
# create group members
def create_group_members(users, groups, num_members_per_group=5):
    group_member_instances = []

    try:
        for group in groups:
            num_members = min(num_members_per_group, len(users))
            members = random.sample(users, num_members)
            for user in members:
                group_member = GroupMember(
                    user_id=user.id,
                    group_id=group.id,
                    joined_at=datetime.utcnow()
                )
                db.session.add(group_member)
                group_member_instances.append(group_member)

        db.session.commit()
        print(f"Successfully added {len(group_member_instances)} group members.")
        count = GroupMember.query.count()
        print(f"Total group members in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while adding group members: {str(e)}")
        raise

    return group_member_instances

#Create Posts
def create_posts(users, groups, num_posts=195):
    posts = []
    specific_posts = [
        {
            "post_title": "Looking for a junior",
            "content": "I am looking for a junior programmer as a developer. The skills include Angular javascript and react"
        },
        {
            "post_title": "Hiring developers",
            "content": "We are hiring developers for our team. Requirements include, SQL, docker and c#"
        },
        {
            "post_title": "Upcoming event",
            "content": "Don't miss our upcoming tech event on April for data sciences"
        },
        {
            "post_title": "Tech discussion",
            "content": "What do you think about the latest developments in Python"
        },
        {
            "post_title": "Project collaboration",
            "content": "I'm starting a new project and looking for collaborators with experience in Docker, GitHub, Kotlin and Java, mobile apps"
        }
    ]
    try:
        # Add specific posts
        for post_data in specific_posts:
            user = random.choice(users)
            group = random.choice(groups)
            post = Post(
                user_id=user.id,
                group_id=group.id,
                post_title=post_data["post_title"],
                content=post_data["content"],
                created_at=datetime.utcnow(),
                visibility='public',
                is_deleted=False
            )
            db.session.add(post)
            posts.append(post)

        # Add additional random posts
        num_additional_posts = max(0, num_posts - len(specific_posts))
        for _ in range(num_additional_posts):
            user = random.choice(users)
            group = random.choice(groups)
            post = Post(
                user_id=user.id,
                group_id=group.id,
                post_title=fake.sentence(),
                content=fake.paragraph(),
                created_at=fake.date_time_this_year(),
                visibility='public',
                is_deleted=False
            )
            db.session.add(post)
            posts.append(post)

        db.session.commit()
        print(f"Successfully added {len(posts)} posts.")
        count = Post.query.count()
        print(f"Total posts in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while adding posts: {str(e)}")
        raise

    return posts


# Create keywords functions
# Keyword functions
def get_or_create_keyword(name: str) -> Keyword:
    try:
        keyword = Keyword(name=name.lower())
        db.session.add(keyword)
        db.session.flush()
        return keyword
    except IntegrityError:
        db.session.rollback()
        return Keyword.query.filter_by(name=name.lower()).first()

def create_keywords(num_keywords: int = 23) -> List[Keyword]:
    keyword_names: List[str] = [
        'programmer', 'java', 'junior', 'senior', 'backend', 'frontend', 'cybersecurity',
        'devops', 'datascience', 'machinelearning', 'React', 'Node.js', 'Python', 'Docker',
        'Blockchain', 'IoT', 'SQL', 'NoSQL', 'Gamer', 'javascript', 'C', 'C++', 'Flutter'
    ]
    keywords: List[Keyword] = []
    for name in set(keyword_names[:num_keywords]):
        keywords.append(get_or_create_keyword(name))
    db.session.commit()
    print(f"Successfully created or retrieved {len(keywords)} keywords.")
    return keywords

def insert_keywords_and_associate(users: List[User], posts: List[Post], num_keywords: int = 22, keywords_per_post: int = 3) -> List[Keyword]:
    keyword_names: List[str] = [
        'java', 'python', 'frontend', 'cybersecurity', 'devops', 'datascience', 'machinelearning',
        'react', 'junior', 'docker', 'blockchain', 'iot', 'sql', 'nosql', 'gamer', 'backend',
        'senior', 'programmer', 'javascript', 'c', 'c++', 'flutter'
    ]
    keywords: List[Keyword] = []
    try:
        # Insert or retrieve keywords
        for name in set(keyword_names[:num_keywords]):
            keywords.append(get_or_create_keyword(name))

        # Associate keywords with users
        user_keyword_pairs: List[tuple] = [
            (1, 'java'), (2, 'python'), (3, 'frontend'), (4, 'cybersecurity'),
            (5, 'devops'), (6, 'datascience'), (7, 'react'), (8, 'docker')
            # Add more pairs as needed
        ]
        for user_id, keyword_name in user_keyword_pairs:
            user = User.query.get(user_id)
            keyword = Keyword.query.filter_by(name=keyword_name.lower()).first()
            if user and keyword and keyword not in user.keywords:
                user.keywords.append(keyword)

        # Associate keywords with posts
        for post in posts:
            post_keywords = random.sample(keywords, random.randint(1, min(keywords_per_post, len(keywords))))
            for keyword in post_keywords:
                if keyword not in post.keywords:
                    post.keywords.append(keyword)

        db.session.commit()
        print(f"Successfully added or retrieved {len(keywords)} keywords and associated them with users and posts.")

        # Verification
        keyword_count = Keyword.query.count()
        user_keyword_count = db.session.query(user_keyword).count()
        post_keyword_count = db.session.query(post_keyword).count()
        print(f"Database contains: {keyword_count} keywords, {user_keyword_count} user-keyword associations, "
              f"and {post_keyword_count} post-keyword associations.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while adding keywords: {str(e)}")
        raise
    return keywords

# Reaction function
def create_reactions(num_reactions: int = 100) -> List[Reaction]:
    reactions: List[Reaction] = []
    try:
        users = User.query.all()
        posts = Post.query.all()
        reaction_types = ['like', 'love', 'haha', 'wow', 'sad', 'angry']

        for _ in range(num_reactions):
            user = random.choice(users)
            post = random.choice(posts)
            reaction_type = random.choice(reaction_types)
            reaction = Reaction(
                user_id=user.id,
                post_id=post.id,
                reaction_type=reaction_type
            )
            db.session.add(reaction)
            reactions.append(reaction)

        db.session.commit()
        print(f"Successfully added {len(reactions)} reactions.")
        count = Reaction.query.count()
        print(f"Total reactions in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while adding reactions: {str(e)}")
        raise
    return reactions

# Comment function
def create_comments(users: List[User], posts: List[Post], num_comments: int = 30) -> List[Comment]:
    comment_contents = [
        "Great post!", "Interesting perspective.", "I disagree with this.",
        "Thanks for sharing!", "Could you elaborate more?", "This is very helpful.",
        "I have a question about this.", "Well said!", "I'm not sure about this.",
        "Looking forward to more information.", "Thank you for the feedback."
    ]
    comments: List[Comment] = []
    try:
        for _ in range(num_comments):
            user = random.choice(users)
            post = random.choice(posts)
            content = random.choice(comment_contents)
            timestamp = post.created_at + timedelta(minutes=random.randint(1, 2880))  # Random time within 48 hours after post creation
            comment = Comment(
                user_id=user.id,
                post_id=post.id,
                content=content,
                timestamp=timestamp
            )
            db.session.add(comment)
            comments.append(comment)

        db.session.commit()
        print(f"Successfully added {num_comments} comments.")
        count = Comment.query.count()
        print(f"Total comments in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while adding comments: {str(e)}")
        raise
    return comments





# Now, let's add a function to create friendships:

def create_friendships(users: List[User], num_friendships: int = 20) -> List[Friendship]:
    friendship_statuses = ['pending', 'accepted', 'rejected']
    friendships = []

    try:
        for _ in range(num_friendships):
            user1 = random.choice(users)
            user2 = random.choice(users)

            if user1 != user2 and not Friendship.query.filter(
                ((Friendship.user_id == user1.id) & (Friendship.friend_id == user2.id)) |
                ((Friendship.user_id == user2.id) & (Friendship.friend_id == user1.id))
            ).first():
                status = random.choice(friendship_statuses)
                created_at = datetime.utcnow() - timedelta(days=random.randint(1, 365))
                updated_at = created_at + timedelta(days=random.randint(1, 30))

                friendship = Friendship(
                    user_id=user1.id,
                    friend_id=user2.id,
                    status=status,
                    created_at=created_at,
                    updated_at=updated_at
                )
                db.session.add(friendship)
                friendships.append(friendship)

        db.session.commit()
        print(f"Successfully added {len(friendships)} friendships.")
        count = Friendship.query.count()
        print(f"Total friendships in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while adding friendships: {str(e)}")
        raise

    return friendships

def create_notifications(num_notifications: int = 50) -> List[Notification]:
    notifications = []
    notification_types = ['new_comment', 'new_reaction', 'friend_request', 'post_mention']

    try:
        users = User.query.all()
        comments = Comment.query.all()
        reactions = Reaction.query.all()
        friendships = Friendship.query.all()
        posts = Post.query.all()

        for _ in range(num_notifications):
            user = random.choice(users)
            notification_type = random.choice(notification_types)
            created_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))

            content = None

            if notification_type == 'new_comment' and comments:
                comment = random.choice(comments)
                content = f"{comment.author.username} commented on your post: '{comment.content[:20]}...'"
            elif notification_type == 'new_reaction' and reactions:
                reaction = random.choice(reactions)
                content = f"{reaction.user.username} reacted to your post with {reaction.reaction_type}"
            elif notification_type == 'friend_request' and friendships:
                friendship = random.choice(friendships)
                content = f"{friendship.user.username} sent you a friend request"
            elif notification_type == 'post_mention' and posts:
                post = random.choice(posts)
                content = f"{post.author.username} mentioned you in a post: '{post.content[:20]}...'"

            if content:
                notification = Notification(
                    user_id=user.id,
                    content=content,
                    notification_type=notification_type,
                    is_read=random.choice([True, False]),
                    created_at=created_at
                )
                db.session.add(notification)
                notifications.append(notification)

        db.session.commit()
        print(f"Successfully added {len(notifications)} notifications.")
        count = Notification.query.count()
        print(f"Total notifications in database: {count}")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"An error occurred while adding notifications: {str(e)}")
        raise

    return notifications

def verify_data_integrity():
    orphan_posts = Post.query.filter(Post.author == None).count()
    if orphan_posts > 0:
        logger.warning(f"Found {orphan_posts} posts without an author")
    # Add more checks as needed

def main():
    try:
        logger.info("Creating users...")
        users = create_users(CONFIG['num_users'])

        logger.info("Creating groups...")
        groups = create_groups(CONFIG['num_groups'])

        logger.info("Creating group members...")
        group_members = create_group_members(users, groups, CONFIG['num_members_per_group'])

        logger.info("Creating posts...")
        posts = create_posts(users, groups, CONFIG['num_posts'])

        logger.info("Inserting keywords and associating with users and posts...")
        keywords = insert_keywords_and_associate(users, posts, CONFIG['num_keywords'])

        logger.info("Creating reactions...")
        reactions = create_reactions(CONFIG['num_reactions'])

        logger.info("Creating comments...")
        comments = create_comments(users, posts, CONFIG['num_comments'])

        logger.info("Creating friendships...")
        friendships = create_friendships(users, CONFIG['num_friendships'])

        logger.info("Creating notifications...")
        notifications = create_notifications(CONFIG['num_notifications'])

        logger.info("Verifying data integrity...")
        verify_data_integrity()

        # Final verification 
        counts = {
            'users': User.query.count(),
            'groups': Group.query.count(),
            'members': GroupMember.query.count(),
            'posts': Post.query.count(),
            'keywords': Keyword.query.count(),
            'reactions': Reaction.query.count(),
            'comments': Comment.query.count(),
            'friendships': Friendship.query.count(),
            'notifications': Notification.query.count()
        }
        logger.info(
            f"Database contains: {counts['users']} users, {counts['groups']} groups, "
            f"{counts['members']} group members, {counts['posts']} posts, {counts['keywords']} keywords, "
            f"{counts['reactions']} reactions, {counts['comments']} comments, {counts['friendships']} friendships, "
            f"and {counts['notifications']} notifications."
        )

        logger.info("All operations completed successfully.")

    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"An integrity error occurred: {str(e)}")
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"A database error occurred: {str(e)}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"An unexpected error occurred: {str(e)}")

# Main execution
if __name__ == "__main__":
    from app import create_app

    app = create_app()
    with app.app_context():
        main()

    print("Data population complete!")