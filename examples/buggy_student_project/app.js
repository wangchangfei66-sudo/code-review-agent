function compareScore(score) {
  var passLine = "60";
  if (score == passLine) {
    console.log("exact pass");
  }
  return score >= passLine;
}

module.exports = { compareScore };
