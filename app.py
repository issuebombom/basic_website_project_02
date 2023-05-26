from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient, DESCENDING
from bson.objectid import ObjectId
from datetime import datetime, timezone, timedelta

client = MongoClient(
    "mongodb+srv://issuebombom:test@testcluster.bcnelb9.mongodb.net/?retryWrites=true&w=majority"
)
db = client.dbspartaproject01
app = Flask(__name__)


@app.route("/")
def home():
    return render_template("minyoung.html")


@app.route("/edit")
def edit():
    return render_template("edit.html")


@app.route("/comments", methods=["GET"])
def get_comments():
    # 코멘트 하나만 조회할 경우
    if request.args.get("comment_id"):
        comment_id = request.args.get("comment_id")
        comment = db.comments.find_one({"_id": ObjectId(comment_id)}, {"_id": False})
        return jsonify({"info": comment})

    else:
        page = int(request.args.get("page"))
        limit = int(request.args.get("limit"))
        limit = limit if limit <= 20 else 20  # limit는 20 이상을 부여할 수 없습니다.

        count = db.comments.count_documents({})

        # 페이지네이션 작동에 사용될 변수입니다.
        # 만약 현재 3페이지에 머물고 있다면 페이지네이션은 <1 2 3 4 5>까지만 보여집니다.
        # 만약 7페이지에 머물고 있다면 페이지네이션은 <6 7 8 9 10>까지만 보여집니다.
        page_set = 5  # 페이지네이션의 페이지 숫자를 5개 단위로 보여지도록 합니다.
        page_group_num = (page - 1) // page_set
        start_page = page_group_num * page_set + 1
        end_page = (page_group_num + 1) * page_set

        # MongoDB에서 코멘트 데이터 가져오기
        # skip과 limit 메소드를 사용하면 가져올 데이터의 범위를 설정할 수 있습니다.
        comments = list(
            db.comments.find({})
            .skip((page - 1) * limit)
            .limit(limit)
            .sort("_id", DESCENDING)
        )
        for obj in comments:
            obj["_id"] = str(obj["_id"])

        # 페이지네이션 구현에 필요한 정보를 프론트에 전달합니다.
        return jsonify(
            {
                "count": count,
                "start_page": start_page,
                "end_page": end_page,
                "page_set": page_set,
                "comments": comments,
            }
        )


@app.route("/comments", methods=["POST"])
def post_comments():
    data = {}

    for key, value in request.form.items():
        data[key] = value

    kst = timezone(timedelta(hours=9))
    now = datetime.now(tz=kst)  # 한국 기준 현재시각을 출력합니다.
    data["upload_time"] = now
    db.comments.insert_one(data)

    return jsonify({"msg": "방명록 작성 완료!"})


@app.route("/comments", methods=["PUT"])
def put_comments():
    _id = request.args.get("comment_id")
    data = {}
    for key, value in request.form.items():
        data[key] = value

    kst = timezone(timedelta(hours=9))
    now = datetime.now(tz=kst)  # 한국 기준 현재시각을 출력합니다.
    data["edit_time"] = now

    filter = {"_id": ObjectId(_id)}
    update = {"$set": data}
    db.comments.update_one(filter, update)

    return jsonify({"msg": "수정 완료!"})


@app.route("/comments", methods=["DELETE"])
def delete_comments():
    _id = request.args.get("comment_id")
    db.comments.delete_one({"_id": ObjectId(_id)})
    return jsonify({"msg": "삭제 완료!"})


if __name__ == "__main__":
    app.run("0.0.0.0", port=5000, debug=True)
