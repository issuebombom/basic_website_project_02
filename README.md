# Javascript 와 Flask를 활용한 미니 웹개발 프로젝트 정리 2

![Alt text](static/images/main.png)

## 프로젝트 목표

본인 소개 페이지와 하단에 코멘트를 남길 수 있는 개인 페이지를 만든다.

## 구현 내용

### Pagination

1. 한 페이지 당 보여질 코멘트의 개수를 지정하고 `limit = 5`와 같은 형태로 변수 지정한다.
1. 페이지 수가 많을 것을 대비하여 n개 단위로만 페이지 번호가 보여지도록 한다.  
   예를 들어 5개 단위로 페이지를 그룹지을 경우 최초 1 ~ 5페이지 번호만 보여지며  
   6페이지로 이동할 경우 6 ~ 10 페이지 번호가 보여지게 한다.  
   페이지번호 노출 범위에 대한 정보를 `page_set = 5`와 같은 형태로 변수 지정한다.
1. Previous와 Next 버튼은 다음 페이지 그룹이 노출되도록 하는 기능이다.  
   가령 현재 페이지가 1 ~ 5페이지 내 있는 경우 Next 버튼을 클릭하면 6페이지로 이동하고,  
   6 ~ 10페이지 내 속한 경우 Next 버튼을 클릭 시 11 페이지로 이동한다.
1. 현재 페이지에 해당하는 페이지 번호는 텍스트 색깔을 달리 한다.
1. Previous와 Next 버튼이 불필요한 경우 숨긴다.

#### 백엔드 구현

```python
@app.route("/pmy/comments", methods=["GET"])
def get_comments():
    """코멘트를 가져옵니다."""
    page = int(request.args.get("page"))
    limit = int(request.args.get("limit"))
    limit = limit if limit <= 20 else 20

    count = db.comments.count_documents({})

    page_set = 5
    page_group_num = (page - 1) // page_set
    start_page = page_group_num * page_set + 1
    end_page = (page_group_num + 1) * page_set
    # MongoDB에서 코멘트 데이터 가져오기
    comments = list(
        db.comments.find({}, {"_id": False})
        .skip((page - 1) * limit)
        .limit(limit)
        .sort("upload_time", DESCENDING)

    )

    return jsonify(
        {
            "count": count,
            "start_page": start_page,
            "end_page": end_page,
            "page_set": page_set,
            "comments": comments,
        }
    )
```

1. 현재 페이지에 따른 페이지네이션 구현하기
   > 만약 코멘트의 총 개수가 100개이며, 한 페이지 당 5개씩 보여진다고 했을 때 1 ~ 20페이지의 범위를 갖게 된다.  
   > 하지만 페이지 번호를 1에서 20까지 전부 노출시키지 않고 1 ~ 5, 6 ~ 10, 11 ~ 15...이렇게 페이지 다섯개씩 한 묶음으로 보여준다면 좀 더 깔끔하게 페이지네이션을 구현할 수 있다.  
   > 예를 들어 < 1 2 3 4 5 6 7....> 이렇게 나열하지 않고 처음에는 <1 2 3 4 5>만 보여줬다가 ">"버튼을 클릭하면 <6 7 8 9 10> 페이지가 보여지도록 하는 것이다.

먼저 아래 간단한 공식을 살펴보자

```python
page_set = 5 # 페이지 묶음 단위
page_group_num = (page - 1) // page_set
start_page = page_group_num * page_set + 1
end_page = (page_group_num + 1) * page_set
```

- page_group_num에 적용된 공식을 보면 page 값이 1 ~ 5일 때는 0, 6 ~ 10일 때는 1, 11 ~ 15일 때는 2가 구해지는 것을 확인할 수 있다. 이를 통해 각 page번호마다 그룹 번호를 부여할 수 있게 된다.
- 각 페이지번호의 그룹 번호를 알 수 있다면 page_set과의 연산을 통해 해당 그룹의 최소, 최대 페이지 번호를 구할 수 있게 된다.

정리하자면 만약 현재 page가 8페이지라면 html상에서 페이지네이션은 < 6 7 8 9 10 >으로 표현되어야 할텐데 이를 구현하기 위해 6과 10을 구했다고 볼 수 있다.

2. MongoDB에서 필요한 만큼 데이터 가져오기

```python
comments = list(
    db.comments.find({}, {"_id": False})
    .skip((page - 1) * limit)
    .limit(limit)
    .sort("upload_time", DESCENDING)
)
```

- mongoDB의 skip과 limit 메소드를 통해 데이터 인덱싱이 가능하다. 현재 보여줄 page가 8번이라고 가정한다면 8페이지의 첫번째 코멘트부터 limit만큼만 가져오면 된다.
- skip 메소드는 이름 그대로 n번째 데이터까지는 건너뜀을 의미한다.
- limit 메소드는 수집 시작 부분부터 n개까지만 수집함을 의미한다.

3. 페이지네이션 구현
   백엔드에서 받은 response로 아래와 같이 프론트를 구현했다.

```javascript
// pagination
$(".pagination").empty();
let total_page = Math.ceil(count / limit);

// previous button
if (page > page_set) {
  let previous = `<li class="page-item">
                    <a class="page-link" href="/pmy?page=${
                      start_page - page_set
                    }&limit=${limit}" aria-label="Previous">
                      <span aria-hidden="true">&laquo;</span>
                    </a>
                  </li>`;
  $(".pagination").append(previous);
}

// pages
let page_list;
for (let i = start_page; i <= end_page; i++) {
  let color;
  let url = `/pmy?page=${i}&limit=${limit}`;
  if (i > total_page) {
    break;
  } else {
    if (page === i) {
      color = "red";
    }
    page_list = `<li class="page-item"><a class="page-link" style="color: ${color};"href="${url}">${i}</a></li>`;
  }
  $(".pagination").append(page_list);
}

// next button
if (page <= total_page - (total_page % page_set) && total_page > page_set) {
  let next = `<li class="page-item">
                <a class="page-link" href="/pmy?page=${
                  start_page + page_set
                }&limit=${limit}" aria-label="Next">
                  <span aria-hidden="true">&raquo;</span>
                </a>
              </li>`;
  $(".pagination").append(next);
}
```

먼저 Previous 버튼 구현을 보자

```javascript
// previous button
if (page > page_set) {
  let previous = `<li class="page-item">
                    <a class="page-link" href="/pmy?page=${
                      start_page - page_set
                    }&limit=${limit}" aria-label="Previous">
                      <span aria-hidden="true">&laquo;</span>
                    </a>
                  </li>`;
  $(".pagination").append(previous);
}
```

- Previous 버튼은 이전 페이지 그룹으로 넘어가도록 하는 기능이다. 페이지 그룹에 대해 다시 한 번 설명하자면 (1 ~ 5) 페이지를 그룹 0, (6 ~ 10)페이지를 그룹 1로 정의함을 뜻하며 만약 현재 7페이지에 머물고 있다면 Previous 버튼 클릭 시 1페이지로 이동해야 하며, 13페이지에 머물고 있다면 6페이지로 이동해야 한다.
- 추가적으로 그룹 0에 해당하는 (1 ~ 5) 페이지가 노출될 경우 Previous 버튼은 필요없기에 숨겨야 한다. 이를 if 문으로 적용했다.

다음으로 각 page 번호 구현을 보자

```javascript
// pages
let page_list;
for (let i = start_page; i <= end_page; i++) {
  let color;
  let url = `/pmy?page=${i}&limit=${limit}`;
  if (i > total_page) {
    break;
  } else {
    if (page === i) {
      color = "red";
    }
    page_list = `<li class="page-item"><a class="page-link" style="color: ${color};"href="${url}">${i}</a></li>`;
  }
  $(".pagination").append(page_list);
}
```

- 리스폰 받았던 start_page와 end_page 정보를 통해 for문의 범위를 정해주고 정해진 범위가 곧 프론트에 페이지네이션 번호로 출력된다. 이렇게 for문을 적용하는 이유는 각 페이지 번호마다 해당하는 url 링크를 적용해야 하기 때문이다.
- color 변수를 통해 현재 머물고 있는 페이지 번호는 빨간색으로 표시되도록 했다.
- 마지막으로 start와 end 페이지 번호는 현재 머물고 있는 페이지가 속한 페이지 그룹의 시작과 끝 번호를 출력하는 단순한 계산이므로 마지막 페이지 그룹에 대한 대책이 필요하다.  
  가령 8페이지가 마지막 페이지라고 한다면 6 ~ 8 페이지 번호가 프론트에 노출되어야 할텐데 대책이 없다면 6 ~ 10 페이지 번호가 노출될 것이다. 이를 방지하기 위해 for문에서 i가 마지막 페이지보다 클 경우 break하도록 적용했다.

마지막으로 Next 버튼 구현을 보자

```javascript
// next button
if (page <= total_page - (total_page % page_set) && total_page > page_set) {
  let next = `<li class="page-item">
                <a class="page-link" href="/pmy?page=${
                  start_page + page_set
                }&limit=${limit}" aria-label="Next">
                  <span aria-hidden="true">&raquo;</span>
                </a>
              </li>`;
  $(".pagination").append(next);
}
```

- next 버튼이 존재하지 않아야 되는 상황이 두 가지 있다.
- 첫번째로 코멘트량이 많지 않아 총 5페이지 분량을 넘지 못한다면 next 버튼은 필요없다. 두번째로 마지막 페이지 그룹에 도달한다면 next 버튼은 필요없다.
- 위 if문은 위 두가지 조건을 만족하지 않는다면 버튼이 생성되도록 도와준다. 참고로 모듈러 연산(%)은 나머지 값을 출력한다.

### 코멘트 수정 기능 구현

각 코멘트마다 '수정'이라는 a 태그에 해당 코멘트 id와 연결되는 링크를 담았고, 이를 클릭 시 아래 백엔드로 이동한다.

```python
@app.route("/comments/<string:id>", methods=["GET"])
def get_comment_with_id(id):
    result = db.comments.find_one({"_id": ObjectId(id)})
    result["_id"] = str(result["_id"])

    return render_template("edit.html", result=result)
```

수정 버튼을 누르면 우선 기존 코멘트 id에 기록된 내용들을 가져와 edit.html에 함께 전송한다.

```html
<!-- edit.html -->
<div class="mypost" id="post-box">
  <div class="input-group mb-3">
    <input type="text" id="nickname" class="form-control" placeholder="닉네임
    (최대 10자)" value={{ result["nick_name"] }} aria-label="nickname"
    maxlength="10">
    <input
      type="password"
      id="password"
      class="form-control"
      placeholder="비밀번호"
      aria-label="password"
    />
  </div>

  <div class="input-group">
    <textarea
      id="comment"
      class="form-control"
      placeholder="코멘트를 남겨주세요. (최대 400자)"
      aria-label="With textarea"
      maxlength="400"
    >
{{ result['comment'] }}</textarea
    >
  </div>
  <div class="mybtns">
    <button
      onclick="editing('{{ result['_id'] }}')"
      type="button"
      class="btn btn-dark"
    >
      수정
    </button>
  </div>
</div>
```

기존에 사용했던 코멘트 등록 틀만 따로 가져와 edit.html에 저장했다.  
그리고 기존에 작성되었던 닉네임, 코멘트를 가져와 수정 틀에 미리 담기도록 했다.  
간단히 말해서 코멘트 수정 창으로 이동하고, 기존에 작성한 정보가 이미 빈칸에 채워진 상태이도록 했다.

'수정' 버튼을 누르면 아래 editing 함수가 실행된다.

```javascript
async function editing(id) {
  let formData = new FormData();
  formData.append("nickname", inputChecker("닉네임", $("#nickname").val()));
  formData.append("password", inputChecker("비밀번호", $("#password").val()));
  formData.append("comment", inputChecker("코멘트", $("#comment").val()));

  const response = await fetch(`/pmy/comments/${id}`, {
    method: "PUT",
    body: formData,
  });
  const data = await response.json();
  alert(data["msg"]);

  (() => {
    window.location.href = "/comments";
  })();
}
```

코멘트 포스팅 함수와 크게 차이가 없으며 딱 두 가지 차이가 있는데 코멘트 id를 백엔드에 넘겨준다는 점, 수정 요청이 fulfilled가 되면 /comments 페이지로 이동하도록 즉시 실행 함수를 추가한 점이다.

mongoDB 메소드로 특정 코멘트를 불러와 수정하도록 했다.

```python
@app.route("/pmy/comments/<string:id>", methods=["PUT"])
def edit_comment_with_id(id):
    nickname = request.form["nickname"]
    password = request.form["password"]
    comment = request.form["comment"]

    kst = timezone(timedelta(hours=9))
    last_edit_time = datetime.now(tz=kst)

    # 데이터 업데이트
    filter = {"_id": ObjectId(id)}
    update = {"$set": {"nick_name": nickname, "password": password, "comment": comment, "last_edit_time": last_edit_time}}
    db.comments.find_one_and_update(filter, update, return_document=False)

    return jsonify({"msg": "수정을 완료했습니다."})
```

코멘트가 수정된 시간이 새로운 데이터로 등록되도록 last_edit_time 변수를 생성했다.

### 보완이 필요한 점

1. 코멘트 수정 시 비밀번호 인증 과정을 추가해야 한다.
2. 모든 비동기 함수에 rejected 상황에 대한 코드 구현이 빠져있다.
3. MongoDB 메소드로 데이터를 수정하는게 아닌 PUT 요청으로 적용할 수는 없을까?

### 어려웠던 점, 의문점

1. 코멘트 수정 버튼 구현 시 href를 통해 url의 쿼리형태로 필요한 데이터를 전달하는 것과 path에 담아 전달하는 것의 차이는 무엇인가?
2. 메인 페이지에 있는 코멘트의 수정 버튼(a 태그)을 클릭하면 edit.html로 랜더링하면서 코멘트 관련 정보를 함께 보내는 방식을 취했다. 여기서 의문점은 edit.html 파일에서 pmy.css와 pmy.js 파일과 이어주기 위한 경로를 지정할 때 아래와 같이 해야 정상적으로 연결이 되었다.

```html
<link href="../../static/css/pmy.css" rel="stylesheet" />
<script src="../../static/js/pmy.js"></script>
```

edit.html와 index.html(메인페이지) 파일의 위치는 같다. 하지만 edit.html파일은 상대경로 지정에서 상위폴더 이동을 두번이나 해야 정상작동 하였다. index.html은 한번만 해도 되었는데 말이다. 이부분도 쉽게 이해되지 않는다. 3. 전형적인 수정 기능 구현이 무엇인지 궁금하다. 개인적으로 위와 같은 방식이 정석적인 방식이 아닐거라는 의구심이 든다.
