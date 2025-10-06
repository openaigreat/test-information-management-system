from datetime import datetime
from app import db
from app.models.user import User

class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(64))
    level = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    ip_address = db.Column(db.String(64))
    operation = db.Column(db.String(255))
    details = db.Column(db.Text)
    
    user = db.relationship('User', backref=db.backref('logs', lazy='dynamic'))
    
    def __repr__(self):
        return f'<SystemLog {self.id}>'

class SystemSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(64), unique=True)
    value = db.Column(db.Text)
    description = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemSettings {self.key}>'

class Backup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255))
    path = db.Column(db.String(255))
    size = db.Column(db.Integer)
    type = db.Column(db.String(64))
    format = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    user = db.relationship('User', backref=db.backref('backups', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Backup {self.filename}>'

class Restore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    backup_id = db.Column(db.Integer, db.ForeignKey('backup.id'))
    type = db.Column(db.String(64))
    status = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    backup = db.relationship('Backup', backref=db.backref('restores', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('restores', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Restore {self.id}>'