#bg {
    line-color: #85c5d3;
    line-width: 2;
    line-join: round;
    [med_incom < 41658] {
      polygon-fill: #9ff;
    }
    [med_incom > 41658] [med_incom < 55846] {
      polygon-fill: #6cf;
    }
    [med_incom > 55846] [med_incom < 69812]{
      polygon-fill: #69f;
    }
    [med_incom > 69812] [med_incom < 90387] {
      polygon-fill: #66f;
    }
    [med_incom > 90387] [med_incom < 245526] {
      polygon-fill: #60f;
    }

}
