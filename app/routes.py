#app/routes.py 
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, make_response, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, set_access_cookies, set_refresh_cookies, unset_jwt_cookies, get_jwt, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException
import traceback
from werkzeug.exceptions import HTTPException  
from . import db
from functools import wraps
from .models import User, TokenBlocklist, Group, GroupMember, Post, Keyword, Friendship, Notification, Reaction, Comment
from validate_email import validate_email
from datetime import datetime, timezone, timedelta
from sqlalchemy import or_
import logging
from .forms import SignupForm, LoginForm, ResetPasswordForm, ResetPasswordConfirmForm, ChangePasswordForm, ProfileForm, CreateGroupForm, CreatePostForm
from sqlalchemy.orm import joinedload
from collections import deque
import re




main = Blueprint('main', __name__)
logger = logging.getLogger(__name__)

# Routes definition
def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            if not user or not user.has_permission(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Error handling
    @app.errorhandler(Exception)
    def handle_exception(e):
        current_app.logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        return jsonify({"error": "An unexpected error occurred"}), 500

    # Log the full errror traceback for debugging
    app.logger.error(f"Unhandled exception: {str(e)}")
    app.logger.error(traceback.format_exc())
    return render_template("error.html", error="An unexpected error occurred"), 500


#Add a funtcion to get the current user, and use it consistently
def get_current_user():
    try:
        verify_jwt_in_request()  # Verifica el token JWT en la solicitud.
        current_user_id = get_jwt_identity()  # Obtiene la identidad del usuario desde el token JWT.
        logger.debug(f"get_current_user: JWT identity: {current_user_id}")
        if current_user_id is None:
            logger.warning("JWT identity is None")
            return None
        user = User.query.get(current_user_id)  # Busca el usuario en la base de datos.
        if user is None:
            logger.warning(f"No user found for id {current_user_id}")
        else:
            logger.debug(f"User found: {user.username}")
        return user
    except JWTExtendedException as e:
        logger.warning(f"JWT Exception: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error in get_current_user: {str(e)}", exc_info=True)
        return None


def get_friend_posts(user):
    # Here we are getting the posts of the user's friends 
    friend_ids = [friend.id for friend in user.friends]  # Assuming that user.friends is a list of Friendship objects
    return Post.query.filter(Post.user_id.in_(friend_ids)).order_by(Post.created_at.desc()).all()

# Suggested Users. 
def get_suggested_users(user, friend_ids):
    # Get users that are not friends with the current user and not the user themselves
    suggested_users = User.query.filter(
        User.id != user.id,
        ~User.id.in_(friend_ids)
    ).limit(5).all()
    return suggested_users


def get_user_groups(user):
    return Group.query.join(GroupMember).filter(GroupMember.user_id == user.id).all()


#BFS Algoritm
#BFS Friend Recommendation Function 
def bfs_friend_recommendations(user, max_depth=2, max_recommendations=5):
    visited = set([user.id])
    queue = deque([(user, 0)])
    recommendations = []

    while queue and len(recommendations) < max_recommendations:
        current_user, depth = queue.popleft()
        if depth > max_depth:
            break

        # Get all friends of the current user
        friends = current_user.friends

        for friend in friends:
            if friend.id not in visited:
                visited.add(friend.id)
                if depth > 0:  # Don't recommend direct friends
                    recommendations.append(friend)
                    if len(recommendations) == max_recommendations:
                        break
                queue.append((friend, depth + 1))

    return recommendations




def tokenize(text):
    # Convert to lowercase and split into words
    words = set(re.findall(r'\w+', text.lower()))
    return words

def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    return intersection / union if union != 0 else 0


# Helper function to generate group recommendations
def generate_group_recommendations(user):
    all_groups = Group.query.all()
    user_keywords = set(tokenize(user.biography))
    recommendations = []

    for group in all_groups:
        group_keywords = set(tokenize(group.description))
        similarity = jaccard_similarity(user_keywords, group_keywords)
        if similarity > 0.1:  # adjust
            recommendations.append((group, similarity))

    return sorted(recommendations, key=lambda x: x[1], reverse=True)[:5]  # Return top 5 recommendations


# Function to find common friends
def find_common_friends(user):
    common_friends = []
    for friend in user.friends:
        for friend_of_friend in friend.friends:
            if friend_of_friend not in user.friends and friend_of_friend != user:
                common_friends.append((friend, friend_of_friend))
    return common_friends


# Notification only for the people in biography 
def notify_users_for_new_group(group):
    group_keywords = tokenize(group.description)
    users = User.query.filter(User.id != group.creator_id).all()

    for user in users:
        user_keywords = tokenize(user.biography)
        similarity = jaccard_similarity(group_keywords, user_keywords)

        if similarity > 0.1:  # You can adjust this threshold
            notification = Notification(
                user_id=user.id,
                content=f"New group that might interest you: '{group.name}'",
                notification_type='group_recommendation',
                is_read=False
            )
            db.session.add(notification)

    db.session.commit()


# Function to create notifications for new posts
def notify_users_for_new_post(post):
    post_keywords = tokenize(post.content)
    users = User.query.filter(User.id != post.user_id).all()

    for user in users:
        user_keywords = tokenize(user.biography)
        similarity = jaccard_similarity(post_keywords, user_keywords)

        if similarity > 0.1:  # You can adjust this threshold
            notification = Notification(
                user_id=user.id,
                content=f"New post that might interest you: '{post.content[:50]}...'",
                notification_type='post_recommendation',
                is_read=False
            )
            db.session.add(notification)

    db.session.commit()


@main.app_template_filter('format_date')
def format_date(value, format='%B %Y'):
    if value is None:
        return 'Unknown'
    return value.strftime(format)

# Developper mode. 
@main.route('/dev_login/<int:user_id>')
def dev_login(user_id):
    if app.debug:
        user = User.query.get(user_id)
        if user:
            access_token = create_access_token(identity=user.id)
            resp = make_response(redirect(url_for('main.dashboard')))
            set_access_cookies(resp, access_token)
            flash(f"Logged in as {user.username}", "success")
            return resp
        else:
            flash("User not found", "error")
            return redirect(url_for('main.home'))
    else:
        return "Not available in production", 403



@main.route('/')
def home():
    logger.info("Entering home route")
    try:
        verify_jwt_in_request(optional=True)
        current_user_id = get_jwt_identity()
        logger.info(f"Current user ID: {current_user_id}")

        if current_user_id:
            user = User.query.get(current_user_id)
            if user:
                return redirect(url_for('main.dashboard'))
            else:
                # Clear invalid cookies and render home template
                resp = make_response(render_template('home.html'))
                unset_jwt_cookies(resp)
                return resp
        else:
            return render_template('home.html', app_debug=app.debug)
    except Exception as e:
        logger.error(f"Error in home route: {str(e)}")
        resp = make_response(render_template('home.html'))
        unset_jwt_cookies(resp)
        return resp

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

# Admin panel route. 
@main.route('/admin_panel')
@jwt_required()
@permission_required('admin')
def admin_panel():
    # Fetch summary statistics
    total_users = User.query.count()
    total_posts = Post.query.count()
    total_groups = Group.query.count()
    total_comments = Comment.query.count()
    total_reactions = Reaction.query.count()

    # Fetch recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()

    # Fetch recent posts
    recent_posts = Post.query.order_by(Post.created_at.desc()).limit(10).all()

    # Fetch recent groups
    recent_groups = Group.query.order_by(Group.created_at.desc()).limit(10).all()

    return render_template('admin_panel.html',
                           total_users=total_users,
                           total_posts=total_posts,
                           total_groups=total_groups,
                           total_comments=total_comments,
                           total_reactions=total_reactions,
                           recent_users=recent_users,
                           recent_posts=recent_posts,
                           recent_groups=recent_groups)

@main.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@jwt_required()
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.username} has been deleted.", "success")
    return redirect(url_for('main.admin_panel'))

@main.route('/admin/delete_post/<int:post_id>', methods=['POST'])
@jwt_required()
@admin_required
def admin_delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash(f"Post has been deleted.", "success")
    return redirect(url_for('main.admin_panel'))

@main.route('/admin/delete_group/<int:group_id>', methods=['POST'])
@jwt_required()
@admin_required
def admin_delete_group(group_id):
    group = Group.query.get_or_404(group_id)
    db.session.delete(group)
    db.session.commit()
    flash(f"Group {group.name} has been deleted.", "success")
    return redirect(url_for('main.admin_panel'))


@main.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        workrole = form.workrole.data
        entreprise = form.entreprise.data
        biography = form.biography.data
        birthday = form.birthday.data
        logger.info(f"Signup attempt for username: {username}, email: {email}")

        if User.query.filter_by(username=username).first():
            flash("Username already exists", "error")
        elif User.query.filter_by(email=email).first():
            flash("Email already exists", "error")
        else:
            try:
                user = User(
                    username=username, 
                    email=email,
                    workrole=workrole,
                    entreprise=entreprise,
                    biography=biography,
                    birthday=birthday
                )
                user.set_password(password)
                db.session.add(user)
                db.session.commit()
                flash("User registered successfully", "success")
                logger.info(f"User registered successfully: {username}")
                return redirect(url_for('main.login'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "error")
                logger.warning(f"User registration failed for username: {username}")
    return render_template('signup.html', form=form)



@main.route('/login', methods=['GET', 'POST'])
def login():
    logger.info("Entering login route")

    try:
        force_login = request.args.get('force_login', 'false').lower() == 'true'
        if force_login:
            logger.info("Forcing login")
            # Remember Add logic for force login here Because
            # This could include setting a specific user as logged in or similar logic.

            verify_jwt_in_request()
            return redirect(url_for('main.dashboard'))
    except Exception as e:
        logger.error(f"Error during forced login: {e}")
        pass  # The user is not logged in, continue with the login process

    form = LoginForm()

    if form.validate_on_submit():
        logger.info("Form validated")
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        logger.info(f"Login attempt for user: {username}")

        if user:
            logger.info(f"User found: {user.username}")

            if user.check_password(password):
                logger.info("Password check successful")
                access_token = create_access_token(identity=user.id)
                refresh_token = create_refresh_token(identity=user.id)
                logger.info(f"Login successful for user: {username} (ID: {user.id})")
                logger.debug(f"Access token created: {access_token[:20]}...")
                logger.debug(f"Refresh token created: {refresh_token[:20]}...")

                resp = make_response(redirect(url_for('main.dashboard')))
                set_access_cookies(resp, access_token)
                set_refresh_cookies(resp, refresh_token)
                logger.info(f"Access and refresh tokens set in cookies for user: {username}")
                flash("Logged in successfully", "success")
                logger.info("Redirecting to dashboard")
                return resp
            else:
                logger.warning(f"Password check failed for username: {username}")
                flash("Invalid username or password", "error")
        else:
            logger.warning(f"No user found for username: {username}")
            flash("Invalid username or password", "error")
    else:
        logger.info("Form validation failed")
        logger.debug(f"Form errors: {form.errors}")

    logger.info("Rendering login template")
    return render_template('login.html', form=form)




@main.route('/protected')
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return f'Hello, {user.username}! This is a protected route.'

@main.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@main.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500





# Dashboard route (endpoint)
# Dashboard route
@main.route('/dashboard')
@jwt_required()
def dashboard():
    current_app.logger.info("Entering dashboard route")
    try:
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"Got user ID: {current_user_id}")

        user = User.query.get(current_user_id)
        if not user:
            current_app.logger.error(f"User not found for ID: {current_user_id}")
            return jsonify({"msg": "User not found"}), 404

        current_app.logger.info(f"Fetched user: {user}")

        # Fetch accepted friendships
        friendships = Friendship.query.filter(
            ((Friendship.user_id == current_user_id) | (Friendship.friend_id == current_user_id)) &
            (Friendship.status == 'accepted')
        ).all()

        friend_ids = [f.friend_id if f.user_id == current_user_id else f.user_id for f in friendships]
        friends = User.query.filter(User.id.in_(friend_ids)).all()
        current_app.logger.info(f"User has {len(friends)} friends")

        friend_recommendations = bfs_friend_recommendations(user)
        current_app.logger.info(f"Generated {len(friend_recommendations)} friend recommendations")

        # Implement pagination
        page = request.args.get('page', 1, type=int)  # Página actual
        per_page = 10  # Número de publicaciones por página

        # Fetch posts (including friends' posts) with eager loading and pagination
        posts_pagination = Post.query.options(
            joinedload(Post.author),
            joinedload(Post.group)
        ).filter(
            or_(Post.user_id == current_user_id, Post.user_id.in_(friend_ids))
        ).order_by(Post.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

        current_app.logger.info(f"Fetched {len(posts_pagination.items)} posts for page {page}")

        # Log details of first 5 posts
        for post in posts_pagination.items[:5]:  # Aquí se utiliza `items` para obtener los posts de la página actual
            current_app.logger.info(f"Post ID: {post.id}, User ID: {post.user_id}, Content: {post.content[:50]}...")

        # Fetch user's groups
        user_groups = Group.query.join(GroupMember).filter(GroupMember.user_id == current_user_id).all()

        # Fetch pending friend requests
        pending_requests = Friendship.query.filter_by(friend_id=current_user_id, status='pending').all()

        # Fetch notifications
        notifications = Notification.query.filter_by(user_id=current_user_id, is_read=False).order_by(Notification.created_at.desc()).all()

        # Generate group recommendations using Jaccard similarity
        group_recommendations = generate_group_recommendations(user)

        current_app.logger.info("About to render template")
        return render_template('dashboard.html', 
                               user=user, 
                               friends=friends,
                               posts=posts_pagination.items,  # Se pasa `items` en lugar de `posts`
                               pagination=posts_pagination,  # Se pasa el objeto de paginación
                               friend_recommendations=friend_recommendations, 
                               user_groups=user_groups,
                               pending_requests=pending_requests,
                               notifications=notifications,
                               group_recommendations=group_recommendations)
    except Exception as e:
        current_app.logger.error(f"Error in dashboard route: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while loading the dashboard"}), 500


# Search End Point.
@main.route('/search')
@jwt_required()
def search():
    query = request.args.get('q', '')
    groups = Group.query.filter(Group.name.ilike(f'%{query}%')).all()
    users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    posts = Post.query.filter(Post.content.ilike(f'%{query}%')).all()
    return render_template('search_results.html', groups=groups, users=users, posts=posts, query=query)




@main.route('/logout')
@jwt_required()
def logout():
    jti = get_jwt()['jti']
    now = datetime.now(timezone.utc)
    token = TokenBlocklist(jti=jti, created_at=now)
    db.session.add(token)
    db.session.commit()
    logger.info(f"Token blacklisted: {jti}")
    resp = make_response(redirect(url_for('main.home')))
    unset_jwt_cookies(resp)
    resp.delete_cookie('csrf_access_token')
    resp.delete_cookie('csrf_refresh_token')
    flash("Successfully logged out", "success")
    return resp


@main.route('/clear_cookies')
def clear_cookies():
    if app.debug:  # Solo permite esto en modo debug
        resp = make_response(redirect(url_for('main.home')))
        unset_jwt_cookies(resp)
        resp.delete_cookie('csrf_access_token')
        resp.delete_cookie('csrf_refresh_token')
        flash("Cookies cleared", "info")
        return resp
    else:
        return "Not available in production", 403


@main.route('/profile', methods=['GET', 'POST'])
@main.route('/profile/<username>', methods=['GET'])
@jwt_required()
def profile(username=None):
    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if username:
        user = User.query.filter_by(username=username).first_or_404()
    else:
        user = current_user

    if not user:
        flash("User not found", "error")
        return redirect(url_for('main.home'))

    is_own_profile = user.id == current_user.id

    form = ProfileForm(obj=user)

    if request.method == 'POST' and is_own_profile:
        if form.validate_on_submit():
            form.populate_obj(user)
            db.session.commit()
            flash("Profile updated successfully", "success")
            return redirect(url_for('main.profile'))

    # Fetch user posts and friends using Post model
    user_posts = Post.query.filter_by(user_id=user.id).order_by(Post.created_at.desc()).limit(5).all()
    user_friends = user.friends

    return render_template('profile.html', user=user, current_user=current_user, 
                           is_own_profile=is_own_profile, user_posts=user_posts, 
                           user_friends=user_friends, form=form)




@main.route('/react/<int:post_id>', methods=['POST'])
@jwt_required()
def react_to_post(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)
    reaction_type = request.json.get('reaction_type')

    if not reaction_type:
        return jsonify({'status': 'error', 'message': 'Reaction type is required'}), 400

    existing_reaction = Reaction.query.filter_by(user_id=current_user_id, post_id=post_id).first()

    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            db.session.delete(existing_reaction)
            db.session.commit()
            return jsonify({'status': 'removed', 'reactions': post.reactions.count()}), 200
        else:
            existing_reaction.reaction_type = reaction_type
            db.session.commit()
            return jsonify({'status': 'changed', 'reactions': post.reactions.count()}), 200
    else:
        new_reaction = Reaction(user_id=current_user_id, post_id=post_id, reaction_type=reaction_type)
        db.session.add(new_reaction)
        db.session.commit()
        return jsonify({'status': 'added', 'reactions': post.reactions.count()}), 200


# Comments Endpoint
@main.route('/comment/<int:post_id>', methods=['POST'])
@jwt_required()
def add_comment(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)
    content = request.json.get('content')
    if content:
        new_comment = Comment(content=content, user_id=current_user_id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'status': 'success', 'comment': {
            'id': new_comment.id,
            'content': new_comment.content,
            'timestamp': new_comment.timestamp.isoformat(),
            'user_id': new_comment.user_id
        }}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Comment cannot be empty'}), 400

    
# Create post
@main.route('/create_post', methods=['POST'])
@jwt_required()
def create_post():
    current_user_id = get_jwt_identity()
    content = request.form.get('content')

    if content:
        new_post = Post(user_id=current_user_id, content=content)
        db.session.add(new_post)
        db.session.commit()

        # Create notifications for interested users
        notify_users_for_new_post(new_post)

        flash("Post created successfully", "success")
    else:
        flash("Post content cannot be empty", "error")

    return redirect(url_for('main.dashboard'))

    
# Notifications endpoint
@main.route('/get_notifications')
@jwt_required(optional=True)
def get_notifications():
    current_app.logger.info("Entering get_notifications route")
    try:
        current_user_id = get_jwt_identity()
        current_app.logger.info(f"Got user ID: {current_user_id}")
        if current_user_id is None:
            current_app.logger.info("No valid JWT token found")
            return jsonify([]), 200

        current_app.logger.info(f"Querying notifications for user {current_user_id}")
        notifications = Notification.query.filter_by(user_id=current_user_id, is_read=False).order_by(Notification.created_at.desc()).limit(5).all()
        current_app.logger.info(f"Fetched {len(notifications)} notifications from database")

        notifications_data = []
        for notification in notifications:
            current_app.logger.debug(f"Processing notification: {notification.id}")
            notifications_data.append({
                'id': notification.id,
                'content': notification.content,
                'created_at': notification.created_at.isoformat(),
                'notification_type': notification.notification_type
            })
        current_app.logger.info(f"Processed {len(notifications_data)} notifications for user {current_user_id}")
        return jsonify(notifications_data)
    except Exception as e:
        current_app.logger.error(f"Error in get_notifications route: {str(e)}", exc_info=True)
        return jsonify({"error": "An error occurred while fetching notifications"}), 500




# End Point when a user joins a group
@main.route('/join_group/<int:group_id>', methods=['POST'])
@jwt_required()
def join_group(group_id):
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    group = Group.query.get_or_404(group_id)

    if user not in group.members:
        group.members.append(user)
        db.session.commit()

        # Notify friends
        notify_friends_bfs(user, group)

        # Notify group creator
        notification = Notification(
            user_id=group.creator_id,
            content=f"{user.username} has joined your group '{group.name}'",
            notification_type='new_group_member',
            is_read=False
        )
        db.session.add(notification)
        db.session.commit()

        flash("You have successfully joined the group", "success")
    else:
        flash("You are already a member of this group", "info")

    return redirect(url_for('main.view_group', group_id=group_id))


@main.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
@jwt_required()
def mark_notification_read(notification_id):
    current_user_id = get_jwt_identity()
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user_id).first()
    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error", "message": "Notification not found"}), 404



@main.route('/verify_db')
def verify_db():
    users = User.query.all()

    return jsonify([user.to_dict() for user in users])


def init_db(app):
    with app.app_context():
        if not User.query.filter_by(username='testuser').first():
            new_user = User(
                username='testuser', 
                email='test@example.com',
                workrole='Software Developer',
                entreprise='Tech Corp',
                biography='I am a test user with a passion for coding.',
                birthday=datetime(1990, 1, 1).date()
            )
            new_user.set_password('testpassword')
            db.session.add(new_user)
            db.session.commit()
            print("Test user created successfully")
        else:
            print("Test user already exists")

@main.route('/users')
def list_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


@main.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        resp = jsonify({'refresh': True})
        set_access_cookies(resp, access_token)
        logger.info(f"Token refreshed for user_id: {current_user_id}")
        return resp, 200
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}")
        return jsonify({"msg": "Token refresh failed"}), 401



@main.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            set_access_cookies(response, access_token)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@main.route('/debug_token')
@jwt_required()
def debug_token():
    current_user_id = get_jwt_identity()
    logger.info(f"Debug route - current user id: {current_user_id}")
    return jsonify(logged_in_as=current_user_id), 200


# Additional Post CRUD Routes.
@main.route('/update_post/<int:post_id>', methods=['GET', 'POST'])
@jwt_required()
def update_post(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user_id:
        flash("You can only edit your own posts", "error")
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            post.content = content
            db.session.commit()
            flash("Post updated successfully", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Post content cannot be empty", "error")

    return render_template('edit_post.html', post=post)

@main.route('/delete_post/<int:post_id>', methods=['POST'])
@jwt_required()
def delete_post(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user_id:
        flash("You can only delete your own posts", "error")
        return redirect(url_for('main.dashboard'))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully", "success")
    return redirect(url_for('main.dashboard'))

# Group CRUD Operations.. 
# Create gruop function
@main.route('/create_group', methods=['GET', 'POST'])
@jwt_required()
def create_group():
    form = CreateGroupForm()
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data
        current_user_id = get_jwt_identity()

        new_group = Group(name=name, description=description, creator_id=current_user_id)
        db.session.add(new_group)
        db.session.commit()

        # Create notifications for interested users
        notify_users_for_new_group(new_group)

        flash("Group created successfully", "success")
        return redirect(url_for('main.dashboard'))

    return render_template('create_group.html', form=form)



# Debug route notification 
@main.route('/debug_notification')
@jwt_required()
def debug_notification():
    current_user_id = get_jwt_identity()
    notifications = Notifications.query.filter_by(user_id=current_user_id).all()
    return jsonify([{
        'id': n.id,
        'created_at': n.created_at.isoformat(),
        'content': n.content,
        'notification_type': n.notification_type,
        'is_read': n.is_read
    } for n in notifications])

#test route to create a notification 
@main.route('/create_test_notification')
@jwt_required()
def create_test_notification():
    current_user_id = get_jwt_identity()
    notification = Notification(
        user_id=current_user_id,
        content="This is a test notification",
        notification_type='test',
        is_read=False
    )
    db.session.add(notification)
    db.session.commit()
    return jsonify({"message": "Test notification created"})



# View group function
@main.route('/group/<int:group_id>')
@jwt_required()
def view_group(group_id):
    group = Group.query.get_or_404(group_id)
    return render_template('view_group.html', group=group, current_user=get_current_user())

# Update group function
@main.route('/update_group/<int:group_id>', methods=['GET', 'POST'])
@jwt_required()
def update_group(group_id):
    group = Group.query.get_or_404(group_id)
    current_user = get_current_user()
    if current_user.id != group.creator_id:
        flash("You don't have permission to edit this group.", "error")
        return redirect(url_for('main.view_group', group_id=group.id))

    if request.method == 'POST':
        group.name = request.form.get('name')
        group.description = request.form.get('description')
        db.session.commit()
        flash("Group updated successfully", "success")
        return redirect(url_for('main.view_group', group_id=group.id))

    return render_template('update_group.html', group=group)


# Delete group function
@main.route('/delete_group/<int:group_id>', methods=['POST'])
@jwt_required()
def delete_group(group_id):
    current_user_id = get_jwt_identity()
    group = Group.query.get_or_404(group_id)

    if group.creator_id != current_user_id:
        flash("You can only delete groups you've created", "error")
        return redirect(url_for('main.view_group', group_id=group_id))

    db.session.delete(group)
    db.session.commit()
    flash("Group deleted successfully", "success")
    return redirect(url_for('main.dashboard'))



# Comment CRUD Operations:
@main.route('/comment/<int:post_id>', methods=['POST'])
@jwt_required()
def create_comment(post_id):
    current_user_id = get_jwt_identity()
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if content:
        new_comment = comment(content=content, user_id=current_user_id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash("Comment added successfully", "success")
    else:
        flash("Comment content cannot be empty", "error")
    return redirect(url_for('main.view_post', post_id=post_id))

@main.route('/update_comment/<int:comment_id>', methods=['GET', 'POST'])
@jwt_required()
def update_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user_id:
        flash("You can only edit your own comments", "error")
        return redirect(url_for('main.view_post', post_id=comment.post_id))

    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            comment.content = content
            db.session.commit()
            flash("Comment updated successfully", "success")
            return redirect(url_for('main.view_post', post_id=comment.post_id))
        else:
            flash("Comment content cannot be empty", "error")

    return render_template('edit_comment.html', comment=comment)

@main.route('/delete_comment/<int:comment_id>', methods=['POST'])
@jwt_required()
def delete_comment(comment_id):
    current_user_id = get_jwt_identity()
    comment = Comment.query.get_or_404(comment_id)

    if comment.user_id != current_user_id:
        flash("You can only delete your own comments", "error")
        return redirect(url_for('main.view_post', post_id=comment.post_id))

    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted successfully", "success")
    return redirect(url_for('main.view_post', post_id=comment.post_id))

# USer Deletion:
@main.route('/delete_account', methods=['GET', 'POST'])
@jwt_required()
def delete_account():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)

    if request.method == 'POST':
        password = request.form.get('password')
        if user.check_password(password):
            # Delete user's posts, comments, etc.
            Post.query.filter_by(user_id=current_user_id).delete()
            Comment.query.filter_by(user_id=current_user_id).delete()
            Reaction.query.filter_by(user_id=current_user_id).delete()

            # Delete user's friendships
            Friendship.query.filter((Friendship.user_id == current_user_id) | (Friendship.friend_id == current_user_id)).delete()

            # Delete user's group memberships
            GroupMember.query.filter_by(user_id=current_user_id).delete()

            # Delete the user
            db.session.delete(user)
            db.session.commit()

            flash("Your account has been deleted", "success")
            return redirect(url_for('main.home'))
        else:
            flash("Incorrect password", "error")

    return render_template('delete_account.html')



#Friendship CRUD Routes
@main.route('/send_friend_request/<int:user_id>', methods=['POST'])
@jwt_required()
def send_friend_request(user_id):
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        flash("You can't send a friend request to yourself", "error")
        return redirect(url_for('main.dashboard'))

    existing_request = Friendship.query.filter_by(user_id=current_user_id, friend_id=user_id).first()
    if existing_request:
        flash("Friend request already sent", "info")
        return redirect(url_for('main.dashboard'))

    new_request = Friendship(user_id=current_user_id, friend_id=user_id, status='pending')
    db.session.add(new_request)
    db.session.commit()
    flash("Friend request sent", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/accept_friend_request/<int:request_id>', methods=['POST'])
@jwt_required()
def accept_friend_request(request_id):
    current_user_id = get_jwt_identity()
    friend_request = Friendship.query.get_or_404(request_id)

    if friend_request.friend_id != current_user_id:
        flash("Invalid friend request", "error")
        return redirect(url_for('main.dashboard'))

    friend_request.status = 'accepted'
    db.session.commit()
    flash("Friend request accepted", "success")
    return redirect(url_for('main.dashboard'))

@main.route('/reject_friend_request/<int:request_id>', methods=['POST'])
@jwt_required()
def reject_friend_request(request_id):
    current_user_id = get_jwt_identity()
    friend_request = Friendship.query.get_or_404(request_id)

    if friend_request.friend_id != current_user_id:
        flash("Invalid friend request", "error")
        return redirect(url_for('main.dashboard'))

    db.session.delete(friend_request)
    db.session.commit()
    flash("Friend request rejected", "success")
    return redirect(url_for('main.dashboard'))



