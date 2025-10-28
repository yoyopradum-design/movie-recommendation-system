async function getRecommendations() {
  const age = document.getElementById("age").value;
  const interests = document.getElementById("interests").value;
  const fav_movie = document.getElementById("fav_movie").value;
  const resultDiv = document.getElementById("result");
  resultDiv.innerHTML = "<p>Loading recommendations...</p>";

  const response = await fetch("/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ age, interests, fav_movie }),
  });

  const data = await response.json();
  if (data.recommendations.length === 0) {
    resultDiv.innerHTML = "<p>❌ No recommendations found. Try another movie.</p>";
  } else {
    let html = "<h3>✨ Recommended Movies:</h3><ul>";
    data.recommendations.forEach((movie) => {
      html += `<li>${movie}</li>`;
    });
    html += "</ul>";
    resultDiv.innerHTML = html;
  }
}
