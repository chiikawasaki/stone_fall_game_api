from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # フロントエンドからのアクセスを許可

# SQLite3のデータベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///scores.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# スコア管理用のデータベースモデル
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    score = db.Column(db.Integer, nullable=False)

    def as_dict(self):
        return {"id": self.id, "username": self.username, "score": self.score}

# GETエンドポイント：全スコアの取得
@app.route('/scores', methods=['GET'])
def get_scores():
    scores = Score.query.all()
    return jsonify([s.as_dict() for s in scores]), 200

# POSTエンドポイント：スコアの登録
@app.route('/score', methods=['POST'])
def add_score():
    data = request.get_json()
    username = data.get('username')
    score_value = data.get('score')
    if not username or score_value is None:
        return jsonify({"error": "username と score を含む正しいデータを送信してください"}), 400

    new_score = Score(username=username, score=score_value)
    db.session.add(new_score)
    db.session.commit()
    return jsonify({"message": "スコアが追加されました", "score": new_score.as_dict()}), 201

@app.route('/scores', methods=['DELETE'])
def delete_all_scores():
    try:
        num_deleted = Score.query.delete()
        db.session.commit()
        return jsonify({"message": f"Deleted {num_deleted} scores"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 初回実行時にテーブルを作成（※開発中のみ）
    with app.app_context():
        db.create_all()
    app.run(debug=True)
