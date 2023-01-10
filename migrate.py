from main import db,VideoList,Users,app

with app.app_context():
    db.drop_all()
    db.create_all()
    
    new_url = VideoList(urllink = 'https://www.youtube.com/embed/YQHsXMglC9A', subject = 'tester')
    new_user = Users(username = 'username')
    new_user.set_password('password')
    
    db.session.add(new_user)
    db.session.add(new_url)

    db.session.commit()