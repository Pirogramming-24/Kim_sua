// 0~9 랜덤
function makeRandomNumbers() {
  const numbers = [];
  while (numbers.length < 3) {
    const n = Math.floor(Math.random() * 10);
    if (!numbers.includes(n)) numbers.push(n);
  }
  return numbers;
}

let answer = makeRandomNumbers();
console.log("answer:", answer);

let attempts = 9;
let gameOver = false;

// DOM
const $n1 = document.getElementById("number1");
const $n2 = document.getElementById("number2");
const $n3 = document.getElementById("number3");
const $attempts = document.getElementById("attempts");
const $btn = document.getElementsByClassName("submit-button")[0];
const $img = document.getElementById("game-result-img");
const $resultDiv = document.getElementById("results");
const $resultDisplay = document.querySelector(".result-display");

$attempts.textContent = attempts;

const footer = document.querySelector("#container .footer");
if (footer) footer.style.display = "none";

// Enter키
document.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !gameOver && attempts > 0) {
    $btn.click();
  }
});

// 한 칸 입력 -> 다음 칸 이동
const moveFocus = (current, next) => {
  if (current.value.length === 1) next.focus();
};
$n1.addEventListener("input", () => moveFocus($n1, $n2));
$n2.addEventListener("input", () => moveFocus($n2, $n3));

// 입력칸 비우기
function clearInputsAndFocus() {
  $n1.value = "";
  $n2.value = "";
  $n3.value = "";
  $n1.focus();
}

// 결과 맨 아래로
function appendResultLine(html) {
  const row = document.createElement("div");
  row.classList.add("check-result");
  row.innerHTML = html;
  $resultDiv.appendChild(row);

  setTimeout(() => {
    $resultDisplay.scrollTop = $resultDisplay.scrollHeight;
  }, 0);
}

// 승, 패
function endGame(imgSrc) {
  gameOver = true;
  $img.src = imgSrc;
  $btn.disabled = true;         
  $btn.style.cursor = "not-allowed";
}

function check_numbers() {
  if (gameOver) return;

  const v1 = $n1.value.trim();
  const v2 = $n2.value.trim();
  const v3 = $n3.value.trim();

  if (v1 === "" || v2 === "" || v3 === "") {
    clearInputsAndFocus();
    return;
  }

  const inputs = [Number(v1), Number(v2), Number(v3)];

  // S, B
  let strike = 0;
  let ball = 0;

  for (let i = 0; i < 3; i++) {
    if (inputs[i] === answer[i]) strike++;
    else if (answer.includes(inputs[i])) ball++;
  }

  if (strike === 0 && ball === 0) {
    appendResultLine(`
      <div class="left">${v1} ${v2} ${v3}</div>
      :
      <div class="right">
        <div class="out num-result">O</div>
      </div>
    `);
  } else {
    appendResultLine(`
      <div class="left">${v1} ${v2} ${v3}</div>
      :
      <div class="right">
        ${strike} <div class="strike num-result">S</div>
        ${ball} <div class="ball num-result">B</div>
      </div>
    `);
  }

  // 횟수
  attempts--;
  $attempts.textContent = attempts;

  // 입력 초기화
  clearInputsAndFocus();

  // 승,패 이미지 출력
  if (strike === 3) {
    endGame("./success.png");
    return;
  }

  if (attempts <= 0) {
    endGame("./fail.png");
    return;
  }
}