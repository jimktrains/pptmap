#bg {
    line-color: #85c5d3;
    line-width: 2;
    line-join: round;
    [pop_densit < 16579] {
      polygon-fill: #9ff;
    }
    [pop_densit > 16579] [pop_densit < 34346] {
      polygon-fill: #6cf;
    }
    [pop_densit > 34346] [pop_densit < 54726]{
      polygon-fill: #69f;
    }
    [pop_densit > 54726] [pop_densit < 89945] {
      polygon-fill: #66f;
    }
    [pop_densit > 89945] [pop_densit < 392950] {
      polygon-fill: #60f;
    }
}
