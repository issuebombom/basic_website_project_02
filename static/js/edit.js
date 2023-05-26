const urlParams = new URLSearchParams(window.location.search);
let page = Number(urlParams.get("page"));
let limit = Number(urlParams.get("limit"));
let comment_id = urlParams.get("comment_id");

$(document).ready(function () {
  searchComment();
});

async function searchComment() {
  const response = await fetch(`/comments?comment_id=${comment_id}`);
  const resource = await response.json();
  const data = resource["info"];

  $(".body-container").empty();
  temp_html = `<h2>코멘트 수정</h2>
                <div class="mypost" id="post-box">
                  <div class="input-group mb-3">
                    <input type="text" id="nickname" class="form-control" placeholder="닉네임 (최대 10자)" value=${data["nick_name"]}
                      aria-label="nickname" maxlength="10">
                    <input type="password" id="password" class="form-control" placeholder="비밀번호" aria-label="password">
                  </div>

                  <div class="input-group">
                    <textarea id="comment" class="form-control" placeholder="코멘트를 남겨주세요. (최대 400자)" aria-label="With textarea"
                      maxlength="400">${data["comment"]}</textarea>
                  </div>
                  <div class="mybtns">
                    <button onclick="editing()" type="button" class="btn btn-dark">수정</button>
                  </div>
                </div>`;
  $(".body-container").append(temp_html);
}

async function editing() {
  let formData = new FormData();
  formData.append("nickname", inputChecker("닉네임", $("#nickname").val()));
  formData.append("password", inputChecker("비밀번호", $("#password").val()));
  formData.append("comment", inputChecker("코멘트", $("#comment").val()));

  const response = await fetch(`/comments?comment_id=${comment_id}`, {
    method: "PUT",
    body: formData,
  });
  const data = await response.json();
  alert(data["msg"]);

  (() => {
    window.location.href = `/?page=${page}&limit=${limit}`;
  })();
}

function inputChecker(target, content) {
  const trimString = content.trim();
  if (trimString.length === 0) {
    alert(`${target}을(를) 입력하세요.`);
    throw new Error(`${target}을(를) 입력하지 않았습니다.`);
  } else {
    return content;
  }
}
