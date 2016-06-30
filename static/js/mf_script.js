// JavaScript Document
$(document).ready(function(e) {
  //text-box focus
  $(".text-box").focus(function(e) {
    $(this).css("background", "#e8f6f4")
  });
  $(".text-box").blur(function(e) {
    $(this).css("background", "#fff")
  });
  //text-box focus ends above
  //login form replace div
  $("#frgt-btn").click(function(e) {
    $(".login-form").css("display", "none");
    $(".reset-form").css("display", "block");

  });
  //login form replace div
  //date picker
  $(function() {
    $("#datepicker").datepicker({
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });
  $(function() {
    $("#date-picker-gc").datepicker({
      showOtherMonths: true,
      selectOtherMonths: true
    });
  });
  $(function() {
    $("#date-picker-cc").datepicker({
      showOtherMonths: true,
      selectOtherMonths: true,
      dateFormat: 'yy-m-dd',
    });
  });
  $(function() {
    $("#datepicker-dob").datepicker({
      changeMonth: true,
      changeYear: true
    });
  });
  //datepicker
  //vertical bar
  $("#togg-btn").unbind('click').bind("click", function() {
    if ($("#togg-btn").hasClass("margin-lft")) {
      $(".nav-2").animate({
        left: '-200px'
      });
      $("#togg-btn").removeClass("margin-lft");
      $(".home-div-gp").delay(500).css("margin-left", "2%");
      $("#fulldata-container").css("transition", "0.5s");
      return false;
    } else {
      $(".nav-2").animate({
        left: '0px'
      });
      $(".home-div-gp").addClass("margin-lft");
      $("#togg-btn").addClass("margin-lft");
      $("#togg-btn").css("transition", "0.5s");
      $(".home-div-gp").css("margin-left", "20%");
      $("#fulldata-container").css("transition", "0.5s");
      return false;
    }
    return false;
  });
  $(".mem").unbind('click').bind("click", function() {
    console.log("click")
    $(".mem-drop").slideToggle('slow', function() {
      console.log("toggle")
      return false;
    });
    return false;
  });
  $(".acc").unbind('click').bind("click", function() {
    $(".acc-drop").slideToggle('slow', function() {
      return false;
    });
    return false;
  });
  $(".sav").unbind('click').bind("click", function() {
    $(".sav-drop").slideToggle('slow', function() {
      return false;
    });
    return false;
  });
  $(".loan").unbind('click').bind("click", function() {
    $(".loan-drop").slideToggle('slow', function() {
      return false;
    });
    return false;
  });
  $(".more").unbind('click').bind("click", function() {
    $(".more-drop").slideToggle('slow', function() {
      return false;
    });
    return false;
  });
  //vertical bar
  //nav bar caret
  $(".navbar-default .navbar-nav>li>a").mouseenter(function() {
    $(".navbar-default .navbar-nav>.dropdown>a .caret").css("border-top-color", "#ddd");
    $(".navbar-default .navbar-nav>.dropdown>a .caret").css("border-bottom-color", "#ddd");

  });
  //ready function ended below
});
