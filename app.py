from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash
import os
import json
import uuid
import shutil

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

DATA_DIR = os.environ.get("DATA_DIR")

if DATA_DIR:
    # Render：使用 Persistent Disk
    os.makedirs(DATA_DIR, exist_ok=True)

    persistent_upload_folder = os.path.join(DATA_DIR, "uploads")
    os.makedirs(persistent_upload_folder, exist_ok=True)

    local_upload_folder = os.path.join(
        app.root_path,
        "static",
        "images",
        "uploads"
    )

    # 第一次部署时，把现在已有的图片复制到 Persistent Disk
    if os.path.isdir(local_upload_folder) and not os.path.islink(local_upload_folder):
        for filename in os.listdir(local_upload_folder):
            source = os.path.join(local_upload_folder, filename)
            destination = os.path.join(
                persistent_upload_folder,
                filename
            )

            if os.path.isfile(source) and not os.path.exists(destination):
                shutil.copy2(source, destination)

        shutil.rmtree(local_upload_folder)

    # 保持现有 /static/images/uploads/... 地址继续能用
    if not os.path.lexists(local_upload_folder):
        os.symlink(
            persistent_upload_folder,
            local_upload_folder
        )

    # 数据库
    persistent_db = os.path.join(DATA_DIR, "posts.db")
    local_db = os.path.join(
        app.instance_path,
        "posts.db"
    )

    # 第一次部署时，把现在已有数据库复制进去
    if not os.path.exists(persistent_db) and os.path.exists(local_db):
        shutil.copy2(local_db, persistent_db)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///" + persistent_db
    )

    app.config["UPLOAD_FOLDER"] = persistent_upload_folder

else:
    # Mac 本地运行
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
    app.config["UPLOAD_FOLDER"] = "static/images/uploads"

db = SQLAlchemy(app)

INTERNAL_USERS = {
    "Shien": os.environ.get("SHIEN_PASSWORD_HASH"),
    "Shien2": os.environ.get("SHIEN2_PASSWORD_HASH")
}


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    country = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    categories = db.Column(db.String(200), nullable=False)
    images = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=True)


with app.app_context():
    db.create_all()

countries = [
    {
        "name": "Iran",
        "image": "iran.jpeg",
        "url": "/country/iran",
        "region": "west-asia",
    },
    {
        "name": "Armenia",
        "image": "armenia.jpeg",
        "url": "/country/armenia",
        "region": "west-asia",
    },
    {
        "name": "Georgia",
        "image": "georgia.jpeg",
        "url": "/country/georgia",
        "region": "west-asia",
    },
    {
        "name": "Azerbaijan",
        "image": "azerbaijan.jpeg",
        "url": "/country/azerbaijan",
        "region": "west-asia",
    },
    {
        "name": "Kazakhstan",
        "image": "kazakhstan.jpeg",
        "url": "/country/kazakhstan",
        "region": "central-asia",
    },
    {
        "name": "Uzbekistan",
        "image": "uzbekistan.jpeg",
        "url": "/country/uzbekistan",
        "region": "central-asia",
    },
    {
        "name": "Japan",
        "image": "japan.jpeg",
        "url": "/country/japan",
        "region": "east-southeast-asia",
    },
    {
        "name": "Thailand",
        "image": "thailand.jpeg",
        "url": "/country/thailand",
        "region": "east-southeast-asia",
    },
    {
        "name": "Cambodia",
        "image": "cambodia.jpeg",
        "url": "/country/cambodia",
        "region": "east-southeast-asia",
    },
    {
        "name": "Malaysia",
        "image": "malaysia.jpeg",
        "url": "/country/malaysia",
        "region": "east-southeast-asia",
    },
    {
        "name": "Egypt",
        "image": "egypt.jpeg",
        "url": "/country/egypt",
        "region": "africa",
    },
]


@app.route("/")
def home():
    return render_template("index.html", countries=countries)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/country/iran")
def iran():
    regions = [
        "Tehran",
        "Isfahan",
        "Shiraz",
        "Tabriz",
        "Mashhad",
        "Yazd",
        "Kerman",
        "Qom",
        "Kashan",
    ]
    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Iran")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Iran",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="iran_hero.jpeg",
        hero_tagline="Where ancient Persia meets the spirit of Islam",
    )


@app.route("/country/armenia")
def armenia():
    regions = ["Yerevan", "Gyumri", "Goris"]

    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Armenia")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Armenia",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="armenia_hero.jpeg",
        hero_tagline="Mountains, monasteries, and quiet roads through the Caucasus",
    )


@app.route("/country/georgia")
def georgia():
    regions = ["Tbilisi", "Sighnaghi", "Kutaisi", "Zugdidi", "Batumi", "Mestia"]

    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Georgia")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Georgia",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="georgia_hero.jpeg",
        hero_tagline="Caucasus peaks, wine, and roads less traveled",
    )


@app.route("/country/azerbaijan")
def azerbaijan():
    regions = ["Baku", "Ganja", "Sheki"]

    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Azerbaijan")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Azerbaijan",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="azerbaijan_hero.jpeg",
        hero_tagline="Fire above, black gold below",
    )


@app.route("/country/kazakhstan")
def kazakhstan():
    regions = ["Almaty", "Astana", "Shymkent", "Turkistan", "Atyrau", "Aktau"]

    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Kazakhstan")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Kazakhstan",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="kazakhstan_hero.jpeg",
        hero_tagline="Endless steppes, ancient nomads, open skies",
    )


@app.route("/country/uzbekistan")
def uzbekistan():
    regions = [
        "Tashkent",
        "Samarkand",
        "Bukhara",
        "Khiva",
        "Nukus",
        "Fergana",
        "Urgench",
        "Shahrisabz",
    ]

    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Uzbekistan")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Uzbekistan",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="uzbekistan_hero.jpeg",
        hero_tagline="Blue domes, ancient cities, and Silk Road stories",
    )


@app.route("/country/japan")
def japan():
    regions = [
        "Hokkaido",
        "Akita",
        "Niigata",
        "Nagano",
        "Tokyo",
        "Ishikawa",
        "Aichi",
        "Kyoto",
        "Nara",
        "Osaka",
        "Hyogo",
        "Okayama",
        "Hiroshima",
        "Fukuoka",
        "Oita",
        "Kumamoto",
        "Miyazaki",
        "Okinawa",
    ]
    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Japan")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Japan",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="japan_hero.jpeg",
        hero_tagline="A harmony of tradition, nature, and modern life",
    )


@app.route("/country/thailand")
def thailand():
    regions = [
        "Bangkok",
        "Chiang Mai",
        "Chiang Rai",
        "Ayutthaya",
        "Chumphon",
        "Krabi",
        "Hat Yai",
        "Betong",
    ]
    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Thailand")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()
    return render_template(
        "country.html",
        country_name="Thailand",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="thailand_hero.jpeg",
        hero_tagline="Buddhism woven into everyday life",
    )


@app.route("/country/cambodia")
def cambodia():
    regions = ["Phnom Penh", "Siem Reap", "Battambang", "Kampot", "Sihanoukville"]

    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Cambodia")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Cambodia",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="cambodia_hero.jpeg",
        hero_tagline="The timeless heart of Khmer civilization",
    )


@app.route("/country/malaysia")
def malaysia():
    regions = [
        "Kuala Lumpur",
        "Penang",
        "Ipoh",
        "Malacca",
        "Johor Bahru",
        "Kota Bharu",
        "Kuching",
        "Kota Kinabalu",
    ]
    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Malaysia")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Malaysia",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="malaysia_hero.jpeg",
        hero_tagline="Different cultures, shared streets, one Malaysia",
    )


@app.route("/country/egypt")
def egypt():
    regions = [
        "Cairo",
        "Alexandria",
        "Marsa Matruh",
        "Luxor",
        "Aswan",
        "Hurghada",
        "Dahab",
    ]

    city = request.args.get("city")
    category = request.args.get("category")

    query = Post.query.filter_by(country="Egypt")

    if city:
        query = query.filter_by(city=city)

    if category:
        query = query.filter(Post.categories.contains(category))

    posts = query.all()

    return render_template(
        "country.html",
        country_name="Egypt",
        regions=regions,
        posts=posts,
        selected_city=city,
        selected_category=category,
        hero_image="egypt_hero.jpeg",
        hero_tagline="Land of pharaohs, shaped by the Nile",
    )


@app.route("/post/<int:post_id>")
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template("post_detail.html", post=post)


@app.route("/admin/new-post", methods=["GET", "POST"])
def admin_new_post():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")
        country = request.form.get("country")
        city = request.form.get("city")
        categories = request.form.getlist("categories")
        images = request.files.getlist("images")

        image_filenames = []

        for image in images:
            if image and image.filename:
                original_filename = secure_filename(image.filename)

                extension = os.path.splitext(original_filename)[1]

                image_filename = uuid.uuid4().hex + extension

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        image_filename
                    )
                )

                image_filenames.append(image_filename)

        new_post = Post(
            title=title,
            content=content,
            country=country,
            city=city,
            categories=",".join(categories),
            images=",".join(image_filenames),
            author=session.get("username"),
        )

        db.session.add(new_post)
        db.session.commit()

        return redirect(url_for("admin_new_post"))
    return render_template("admin_new_post.html")

@app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id):
    if "username" not in session:
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)

    if post.author != session["username"]:
        return "You cannot edit this post.", 403

    if request.method == "POST":
        post.title = request.form.get("title")
        post.content = request.form.get("content")
        post.country = request.form.get("country")
        post.city = request.form.get("city")
        post.categories = ",".join(request.form.getlist("categories"))

        images = request.files.getlist("images")

        new_image_filenames = []

        for image in images:
            if image and image.filename:
                original_filename = secure_filename(image.filename)

                extension = os.path.splitext(original_filename)[1]

                image_filename = uuid.uuid4().hex + extension

                image.save(
                    os.path.join(
                        app.config["UPLOAD_FOLDER"],
                        image_filename
                    )
                )

                new_image_filenames.append(image_filename)


        photo_order_text = request.form.get("photo_order", "[]")

        try:
            photo_order = json.loads(photo_order_text)
        except json.JSONDecodeError:
            photo_order = []


        final_image_filenames = []

        for item in photo_order:

            if item["type"] == "old":

                final_image_filenames.append(
                    item["filename"]
                )

            elif item["type"] == "new":

                new_index = item["index"]

                if 0 <= new_index < len(new_image_filenames):

                    final_image_filenames.append(
                        new_image_filenames[new_index]
                    )


        post.images = ",".join(final_image_filenames)

        db.session.commit()

        return redirect(url_for("home"))

    return render_template("edit_post.html", post=post)

@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    if "username" not in session:
        return redirect(url_for("login"))

    post = Post.query.get_or_404(post_id)

    if post.author != session["username"]:
        return "You cannot delete this post.", 403

    db.session.delete(post)
    db.session.commit()

    return redirect(url_for("home"))

@app.route("/manage-posts")
def manage_posts():
    if "username" not in session:
        return redirect(url_for("login"))

    posts = Post.query.filter_by(
        author=session["username"]
    ).all()

    return render_template("manage_posts.html", posts=posts)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if (
            username in INTERNAL_USERS
            and INTERNAL_USERS[username]
            and check_password_hash(INTERNAL_USERS[username], password)
        ):
            session["username"] = username
            return redirect(url_for("home"))

        error = "Username or password is incorrect."

    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
